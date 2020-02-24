from enum import Enum

from flask import current_app as app


class StageStates(Enum):
    CREATED = "created"
    IN_PROGRESS = "in progress"
    FAILED = "failed"


class AzureStages(Enum):
    TENANT = "tenant"
    BILLING_PROFILE_CREATION = "billing profile creation"
    BILLING_PROFILE_VERIFICATION = "billing profile verification"
    BILLING_PROFILE_TENANT_ACCESS = "billing profile tenant access"
    TASK_ORDER_BILLING_CREATION = "task order billing creation"
    TASK_ORDER_BILLING_VERIFICATION = "task order billing verification"
    BILLING_INSTRUCTION = "billing instruction"
    PRODUCT_PURCHASE = "purchase aad premium product"
    PRODUCT_PURCHASE_VERIFICATION = "purchase aad premium product verification"
    TENANT_PRINCIPAL_APP = "tenant principal application"
    TENANT_PRINCIPAL = "tenant principal"
    TENANT_PRINCIPAL_CREDENTIAL = "tenant principal credential"
    ADMIN_ROLE_DEFINITION = "admin role definition"
    PRINCIPAL_ADMIN_ROLE = "tenant principal admin"
    INITIAL_MGMT_GROUP = "initial management group"
    INITIAL_MGMT_GROUP_VERIFICATION = "initial management group verification"
    TENANT_ADMIN_OWNERSHIP = "tenant admin ownership"
    TENANT_PRINCIPAL_OWNERSHIP = "tenant principial ownership"
    BILLING_OWNER = "billing owner"


def _build_csp_states(csp_stages):
    states = {
        "UNSTARTED": "unstarted",
        "STARTING": "starting",
        "STARTED": "started",
        "COMPLETED": "completed",
        "FAILED": "failed",
    }
    for csp_stage in csp_stages:
        for state in StageStates:
            states[csp_stage.name + "_" + state.name] = (
                csp_stage.value + " " + state.value
            )
    return states


FSMStates = Enum("FSMStates", _build_csp_states(AzureStages))

compose_state = lambda csp_stage, state: getattr(
    FSMStates, "_".join([csp_stage.name, state.name])
)


def _build_transitions(csp_stages):
    transitions = []
    states = []
    for stage_i, csp_stage in enumerate(csp_stages):
        # the last CREATED stage has a transition to COMPLETED
        if stage_i == len(csp_stages) - 1:
            transitions.append(
                dict(
                    trigger="complete",
                    source=compose_state(
                        list(csp_stages)[stage_i], StageStates.CREATED
                    ),
                    dest=FSMStates.COMPLETED,
                )
            )

        for state in StageStates:
            states.append(
                dict(
                    name=compose_state(csp_stage, state),
                    tags=[csp_stage.name, state.name],
                )
            )
            if state == StageStates.CREATED:
                if stage_i > 0:
                    src = compose_state(
                        list(csp_stages)[stage_i - 1], StageStates.CREATED
                    )
                else:
                    src = FSMStates.STARTED
                transitions.append(
                    dict(
                        trigger="create_" + csp_stage.name.lower(),
                        source=src,
                        dest=compose_state(csp_stage, StageStates.IN_PROGRESS),
                        after="after_in_progress_callback",
                    )
                )
            if state == StageStates.IN_PROGRESS:
                transitions.append(
                    dict(
                        trigger="finish_" + csp_stage.name.lower(),
                        source=compose_state(csp_stage, state),
                        dest=compose_state(csp_stage, StageStates.CREATED),
                        conditions=["is_csp_data_valid"],
                    )
                )
            if state == StageStates.FAILED:
                transitions.append(
                    dict(
                        trigger="fail_" + csp_stage.name.lower(),
                        source=compose_state(csp_stage, StageStates.IN_PROGRESS),
                        dest=compose_state(csp_stage, StageStates.FAILED),
                    )
                )
                transitions.append(
                    dict(
                        trigger="resume_progress_" + csp_stage.name.lower(),
                        source=compose_state(csp_stage, StageStates.FAILED),
                        dest=compose_state(csp_stage, StageStates.IN_PROGRESS),
                        conditions=["is_ready_resume_progress"],
                    )
                )
    return states, transitions


class FSMMixin:

    system_states = [
        {"name": FSMStates.UNSTARTED.name, "tags": ["system"]},
        {"name": FSMStates.STARTING.name, "tags": ["system"]},
        {"name": FSMStates.STARTED.name, "tags": ["system"]},
        {"name": FSMStates.FAILED.name, "tags": ["system"]},
        {"name": FSMStates.COMPLETED.name, "tags": ["system"]},
    ]

    system_transitions = [
        {"trigger": "init", "source": FSMStates.UNSTARTED, "dest": FSMStates.STARTING},
        {"trigger": "start", "source": FSMStates.STARTING, "dest": FSMStates.STARTED},
        {"trigger": "reset", "source": "*", "dest": FSMStates.UNSTARTED},
        {"trigger": "fail", "source": "*", "dest": FSMStates.FAILED,},
    ]

    def fail_stage(self, stage):
        fail_trigger = f"fail_{stage}"
        if fail_trigger in self.machine.get_triggers(self.current_state.name):
            self.trigger(fail_trigger)
            app.logger.info(
                f"calling fail trigger '{fail_trigger}' for '{self.__repr__()}'"
            )
        else:
            app.logger.info(
                f"could not locate fail trigger '{fail_trigger}' for '{self.__repr__()}'"
            )

    def finish_stage(self, stage):
        finish_trigger = f"finish_{stage}"
        if finish_trigger in self.machine.get_triggers(self.current_state.name):
            app.logger.info(
                f"calling finish trigger '{finish_trigger}' for '{self.__repr__()}'"
            )
            self.trigger(finish_trigger)
