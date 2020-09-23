from enum import Enum
from typing import Dict


class StateMachineMisconfiguredError(Exception):
    def __init__(self, class_details):
        self.class_details = class_details

    @property
    def message(self):
        return self.class_details


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
    PRINCIPAL_APP_GRAPH_API_PERMISSIONS = (
        "grant invite permission to principal application"
    )
    INITIAL_MGMT_GROUP = "initial management group"
    INITIAL_MGMT_GROUP_VERIFICATION = "initial management group verification"
    TENANT_ADMIN_OWNERSHIP = "tenant admin ownership"
    TENANT_PRINCIPAL_OWNERSHIP = "tenant principial ownership"
    BILLING_OWNER = "billing owner"
    TENANT_ADMIN_CREDENTIAL_RESET = "tenant admin credential reset"
    POLICIES = "policies"


def _build_csp_states(csp_stages: Enum) -> Dict[str, str]:
    """Builds a complete dictionary of portfolio provisioning states for a CSP
    
    Includes system states, plus each CSP stage combined with each Stage State. 
    E.g. Given two CSP Stages, `TENANT` & `BILLING_PROFILE`, and three possible 
    stage states, `CREATED`, `IN_PROGRESS`, & FAILED, this function generates a 
    dictionary of system states + states that correspond with:
    - TENANT_CREATED
    - TENANT_IN_PROGRESS
    - TENANT_FAILED
    - BILLING_PROFILE_CREATION_CREATED
    - BILLING_PROFILE_CREATION_IN_PROGRESS
    - BILLING_PROFILE_CREATION_FAILED
    """

    system_states = {
        "UNSTARTED": "unstarted",
        "COMPLETED": "completed",
        "CONFIGURATION_ERROR": "configuration_error",
    }
    csp_states = {
        f"{csp_stage.name}_{stage_state.name}": f"{csp_stage.value} {stage_state.value}"
        for csp_stage in csp_stages
        for stage_state in StageStates
    }
    return {**system_states, **csp_states}


PortfolioStates = Enum("PortfolioStates", _build_csp_states(AzureStages))

compose_state = lambda csp_stage, state: getattr(
    PortfolioStates, f"{csp_stage.name}_{state.name}"
)


def _build_transitions(csp_stages):
    """Build transitions between each provisioning state for a given CSP
    
    For each CSP state (a combination of CSP stages and StateStages) We need 
    transitions: 
    
    - from the system `UNSTARTED` state or the previous stage's `_CREATED` state
      to `<CSP stage>_IN_PROGRESS` to try the provisioning step
        - triggered with a `create_<CSP stage>` trigger
    
    - from `<CSP stage>_IN_PROGRESS` to `<CSP stage>_FAILED`, when the 
      provisioning step fails
        - triggered with a `fail_<CSP stage>` trigger
    
    - from `<CSP stage>_IN_PROGRESS` to the previous `<CSP stage>_CREATED` state
      (or UNSTARTED), when we need to retry the provisioning step
        - triggered with a `reset_<CSP stage>` trigger
    
    - from `<CSP stage>_FAILED` to `<CSP stage>_IN_PROGRESS`, to retry the
      provisioning step
        - triggered with a `resume_progress_<CSP stage>` trigger
    
    - from `<CSP stage>_IN_PROGRESS` to `<CSP stage>_CREATED` state, when the 
      provisioning step is successful
        - triggered with a `finish_<CSP stage>` trigger
    
    - from the last stage's `_CREATED` state to the system `COMPLETED` state
        - triggered with a `complete` trigger
    """
    transitions = []
    states = []
    for stage_index, csp_stage in enumerate(csp_stages):
        for state in StageStates:
            if stage_index > 0:
                previous_state = compose_state(
                    list(csp_stages)[stage_index - 1], StageStates.CREATED
                )
            else:
                previous_state = PortfolioStates.UNSTARTED
            states.append(
                dict(
                    name=compose_state(csp_stage, state),
                    tags=[csp_stage.name, state.name],
                )
            )
            if state == StageStates.CREATED:
                transitions.append(
                    dict(
                        trigger="create_" + csp_stage.name.lower(),
                        source=previous_state,
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
                transitions.append(
                    dict(
                        trigger="reset_" + csp_stage.name.lower(),
                        dest=previous_state,
                        source=compose_state(csp_stage, state),
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
                        after="after_in_progress_callback",
                    )
                )

    # the last CREATED stage has a transition to COMPLETED
    transitions.append(
        dict(
            trigger="complete",
            source=compose_state(list(csp_stages)[-1], StageStates.CREATED),
            dest=PortfolioStates.COMPLETED,
        )
    )

    return states, transitions


class FSMMixin:

    system_states = [
        {"name": PortfolioStates.UNSTARTED.name, "tags": ["system"]},
        {"name": PortfolioStates.CONFIGURATION_ERROR.name, "tags": ["system"]},
        {"name": PortfolioStates.COMPLETED.name, "tags": ["system"]},
    ]

    system_transitions = [
        {"trigger": "reset", "source": "*", "dest": PortfolioStates.UNSTARTED},
        {
            "trigger": "configuration_error",
            "source": "*",
            "dest": PortfolioStates.CONFIGURATION_ERROR,
        },
    ]

    def _find_and_call_stage_trigger(self, trigger_prefix, **kwargs):
        """Given a trigger prefix, find the appropriate trigger to call for the 
        current Portfolio provisioning stage


        E.g. if a portfolio is in the "TENANT" stage, and this method is given
        a trigger prefix of `create`, find the `create_tenant` trigger and call it.
        """
        trigger = next(
            (
                trigger
                for trigger in self.machine.get_triggers(self.state_str)
                if trigger.startswith(trigger_prefix)
            ),
            None,
        )
        if trigger is not None:
            self.trigger(trigger, **kwargs)
        else:
            self.trigger("configuration_error")
            raise StateMachineMisconfiguredError(
                f"could not locate trigger with prefix '{trigger_prefix}' for '{self.__repr__()}'"
            )

    def start_next_stage(self, **kwargs):
        self._find_and_call_stage_trigger("create_", **kwargs)

    def resume_stage_progress(self, **kwargs):
        self._find_and_call_stage_trigger("resume_progress_", **kwargs)

    def fail_stage(self, **kwargs):
        self._find_and_call_stage_trigger("fail_", **kwargs)

    def finish_stage(self, **kwargs):
        self._find_and_call_stage_trigger("finish_", **kwargs)

    def reset_stage(self, **kwargs):
        self._find_and_call_stage_trigger("reset_", **kwargs)
