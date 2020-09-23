import importlib

from flask import current_app as app
from sqlalchemy import Column
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import reconstructor, relationship
from transitions import Machine
from transitions.extensions.states import Tags, add_state_features

import atat.models.mixins as mixins
from atat.database import db
from atat.domain.csp.cloud.models import stage_to_classname
from atat.models.base import Base
from atat.models.mixins.state_machines import (
    AzureStages,
    PortfolioStates,
    StageStates,
    StateMachineMisconfiguredError,
    _build_transitions,
)
from atat.models.types import Id


def get_stage_csp_class(stage, class_type):
    """
    given a stage name and class_type return the class
    class_type is either 'payload' or 'result'

    """
    cls_name = f"{stage_to_classname(stage)}CSP{class_type.capitalize()}"
    try:
        return getattr(
            importlib.import_module("atat.domain.csp.cloud.models"), cls_name
        )
    except AttributeError:
        raise StateMachineMisconfiguredError(
            f"could not import CSP Payload/Result class {cls_name}"
        )


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
        SQLAEnum(PortfolioStates, native_enum=False, create_constraint=False),
        default=PortfolioStates.UNSTARTED,
        nullable=False,
    )

    def __init__(self, portfolio, cloud=None, **kwargs):
        self.portfolio = portfolio
        self.attach_machine()

    def after_state_change(self, event):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<PortfolioStateMachine(state='{self.current_state.name}', portfolio='{self.portfolio.name}'"

    @property
    def state_str(self):
        """
        If the state column has not been serialized to the database,
        it's an instance of PortfolioStates. If it has been serialized and
        deserialized, it's a string. This property will always return
        it as a string.
        """
        return getattr(self.state, "name", self.state)

    @reconstructor
    def attach_machine(self, stages=AzureStages, cloud=None):
        """
        This is called as a result of a sqlalchemy query.
        Attach a machine depending on the current state.
        """
        self.machine = StateMachineWithTags(
            model=self,
            send_event=True,
            initial=self.current_state if self.state else PortfolioStates.UNSTARTED,
            auto_transitions=False,
            after_state_change="after_state_change",
        )
        states, transitions = _build_transitions(stages)
        self.cloud = cloud if cloud else app.csp.cloud
        self.machine.add_states(self.system_states + states)
        self.machine.add_transitions(self.system_transitions + transitions)

    @property
    def current_state(self):
        if isinstance(self.state, str):
            return getattr(PortfolioStates, self.state)
        return self.state

    @property
    def current_stage(self) -> str:
        """Returns the current stage of the CSP provisioning process

        E.g. TENANT_IN_PROGRESS -> tenant
        """
        for stage_state in StageStates:
            if self.current_state.name.endswith(stage_state.name):
                stage, stage_state = self.current_state.name.split(
                    f"_{stage_state.name}"
                )
                return stage.lower()

    def trigger_next_transition(self, **kwargs):
        state_obj = self.machine.get_state(self.state)

        kwargs["csp_data"] = kwargs.get("csp_data", {})
        if self.current_state == PortfolioStates.UNSTARTED:
            self.start_next_stage(**kwargs)

        elif state_obj.is_FAILED:
            self.resume_stage_progress(**kwargs)

        elif state_obj.is_CREATED:
            if "complete" in self.machine.get_triggers(state_obj.name):
                self.trigger("complete", **kwargs)
            else:
                self.start_next_stage(**kwargs)

    def _do_provisioning_stage(self, payload):
        payload_data_class = get_stage_csp_class(self.current_stage, "payload")
        payload_data = payload_data_class(**payload)
        return getattr(self.cloud, f"create_{self.current_stage}")(payload_data)

    def _update_csp_data(self, payload: dict) -> None:
        # TODO: this is a good candidate for a domain class method, but trying
        # to import the Portfolios domain class results in what appears to be a
        # cyclical import error
        if self.portfolio.csp_data is None:
            self.portfolio.csp_data = {}
        self.portfolio.csp_data.update(payload)
        db.session.add(self.portfolio)
        db.session.commit()

    def after_in_progress_callback(self, event):
        try:
            payload = event.kwargs.get("csp_data")
            response = self._do_provisioning_stage(payload)
            if response.reset_stage:
                self.reset_stage()
            else:
                self._update_csp_data(response.dict())
                self.finish_stage()
        except:
            self.fail_stage()
            raise

    def is_csp_data_valid(self, event):
        """
        This function guards advancing states from *_IN_PROGRESS to *_COMPLETED.
        """
        if self.portfolio.csp_data is None or not isinstance(
            self.portfolio.csp_data, dict
        ):
            # TODO: Should this throw an exception and fail the portfolio? Is
            # this even necessary?
            print("no csp data")
            return False

        return True

    def is_ready_resume_progress(self, event):
        """
        This function guards advancing states from FAILED to *_IN_PROGRESS.
        """
        # TODO: Make this real
        return True

    @property
    def history(self):
        return self.get_changes()

    @property
    def application_id(self):
        return None
