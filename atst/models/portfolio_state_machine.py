import importlib

from sqlalchemy import Column, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import relationship, reconstructor
from sqlalchemy.dialects.postgresql import UUID

from pydantic import ValidationError as PydanticValidationError
from transitions import Machine
from transitions.extensions.states import add_state_features, Tags

from flask import current_app as app

from atst.domain.csp.cloud.exceptions import ConnectionException, UnknownServerException
from atst.database import db
from atst.models.types import Id
from atst.models.base import Base
import atst.models.mixins as mixins
from atst.models.mixins.state_machines import FSMStates, AzureStages, _build_transitions


def _stage_to_classname(stage):
    return "".join(map(lambda word: word.capitalize(), stage.split("_")))


def get_stage_csp_class(stage, class_type):
    """
    given a stage name and class_type return the class
    class_type is either 'payload' or 'result'

    """
    cls_name = f"{_stage_to_classname(stage)}CSP{class_type.capitalize()}"
    try:
        return getattr(
            importlib.import_module("atst.domain.csp.cloud.models"), cls_name
        )
    except AttributeError:
        print("could not import CSP Result class <%s>" % cls_name)


@add_state_features(Tags)
class StateMachineWithTags(Machine):
    pass


class PortfolioStateMachine(
    Base,
    mixins.TimestampsMixin,
    mixins.AuditableMixin,
    mixins.DeletableMixin,
    mixins.FSMMixin,
):
    __tablename__ = "portfolio_state_machines"

    id = Id()

    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"),)
    portfolio = relationship("Portfolio", back_populates="state_machine")

    state = Column(
        SQLAEnum(FSMStates, native_enum=False, create_constraint=False),
        default=FSMStates.UNSTARTED,
        nullable=False,
    )

    def __init__(self, portfolio, csp=None, **kwargs):
        self.portfolio = portfolio
        self.attach_machine()

    def after_state_change(self, event):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<PortfolioStateMachine(state='{self.current_state.name}', portfolio='{self.portfolio.name}'"

    @reconstructor
    def attach_machine(self):
        """
        This is called as a result of a sqlalchemy query.
        Attach a machine depending on the current state.
        """
        self.machine = StateMachineWithTags(
            model=self,
            send_event=True,
            initial=self.current_state if self.state else FSMStates.UNSTARTED,
            auto_transitions=False,
            after_state_change="after_state_change",
        )
        states, transitions = _build_transitions(AzureStages)
        self.machine.add_states(self.system_states + states)
        self.machine.add_transitions(self.system_transitions + transitions)

    @property
    def current_state(self):
        if isinstance(self.state, str):
            return getattr(FSMStates, self.state)
        return self.state

    def trigger_next_transition(self, **kwargs):
        state_obj = self.machine.get_state(self.state)

        if state_obj.is_system:
            if self.current_state in (FSMStates.UNSTARTED, FSMStates.STARTING):
                # call the first trigger availabe for these two system states
                trigger_name = self.machine.get_triggers(self.current_state.name)[0]
                self.trigger(trigger_name, **kwargs)

            elif self.current_state == FSMStates.STARTED:
                # get the first trigger that starts with 'create_'
                create_trigger = next(
                    filter(
                        lambda trigger: trigger.startswith("create_"),
                        self.machine.get_triggers(FSMStates.STARTED.name),
                    ),
                    None,
                )
                if create_trigger:
                    self.trigger(create_trigger, **kwargs)
                else:
                    app.logger.info(
                        f"could not locate 'create trigger' for {self.__repr__()}"
                    )
                    self.fail_stage(stage)

        elif state_obj.is_CREATED:
            # the create trigger for the next stage should be in the available
            # triggers for the current state
            create_trigger = next(
                filter(
                    lambda trigger: trigger.startswith("create_"),
                    self.machine.get_triggers(self.state.name),
                ),
                None,
            )
            if create_trigger is not None:
                self.trigger(create_trigger, **kwargs)

    def after_in_progress_callback(self, event):
        stage = self.current_state.name.split("_IN_PROGRESS")[0].lower()

        # Accumulate payload w/ creds
        payload = event.kwargs.get("csp_data")

        payload_data_cls = get_stage_csp_class(stage, "payload")
        if not payload_data_cls:
            app.logger.info(f"could not resolve payload data class for stage {stage}")
            self.fail_stage(stage)
        try:
            payload_data = payload_data_cls(**payload)
        except PydanticValidationError as exc:
            app.logger.error(
                f"Payload Validation Error in {self.__repr__()}:", exc_info=1
            )
            app.logger.info(exc.json())
            print(exc.json())
            app.logger.info(payload)
            self.fail_stage(stage)

        # TODO: Determine best place to do this, maybe @reconstructor
        self.csp = app.csp.cloud

        try:
            func_name = f"create_{stage}"
            response = getattr(self.csp, func_name)(payload_data)
            if self.portfolio.csp_data is None:
                self.portfolio.csp_data = {}
            self.portfolio.csp_data.update(response.dict())
            db.session.add(self.portfolio)
            db.session.commit()
        except PydanticValidationError as exc:
            app.logger.error(
                f"Failed to cast response to valid result class {self.__repr__()}:",
                exc_info=1,
            )
            app.logger.info(exc.json())
            print(exc.json())
            app.logger.info(payload_data)
            # TODO: Ensure that failing the stage does not preclude a Celery retry
            self.fail_stage(stage)
        # TODO: catch and handle general CSP exception here
        except (ConnectionException, UnknownServerException) as exc:
            app.logger.error(
                f"CSP api call. Caught exception for {self.__repr__()}.", exc_info=1,
            )
            # TODO: Ensure that failing the stage does not preclude a Celery retry
            self.fail_stage(stage)

        self.finish_stage(stage)

    def is_csp_data_valid(self, event):
        """
        This function guards advancing states from *_IN_PROGRESS to *_COMPLETED.
        """
        if self.portfolio.csp_data is None or not isinstance(
            self.portfolio.csp_data, dict
        ):
            print("no csp data")
            return False

        return True

    @property
    def application_id(self):
        return None
