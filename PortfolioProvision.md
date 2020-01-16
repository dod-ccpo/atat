
Each CSP will have a set of "stages" that are required to be completed before the provisioning process can be considered complete.

Azure Stages:
    tenant,
    billing profile,
    admin subscription
    etc.

`atst.models.mixins.state_machines` module contains:

    python Enum classes that define the stages for a CSP

        class AzureStages(Enum):
            TENANT = "tenant"
            BILLING_PROFILE = "billing profile"
            ADMIN_SUBSCRIPTION = "admin subscription"

there are two types of python dataclass subclasses defined in `atst.models.portoflio_state_machine` module.

one holds the data that is submitted to the CSP

    @dataclass
    class TenantCSPPayload():
        user_id: str
        password: str
        etc.

the other holds the results of the call to the CSP
    @dataclass
    class TenantCSPResult():
        user_id: str
        tenant_id: str
        user_object_id: str
        etc.

A Finite State Machine `atst.models.portoflio_state_machine.PortfolioStateMachine` is created for each provisioning process and tied to an instance of Portfolio class.

Aach time the FSM is created/accessed it will generate a list of States and Transitions between the states.

There is a set of "system" states such as UNSTARTED, STARTING, STARTED, COMPLETED, FAILED etc

There is a set of CSP specific states generated for each "stage" in the FSM.
    TENANT_IN_PROGRESS
    TENANT_IN_COMPLETED
    TENANT_IN_FAILED
    BILLING_PROFILE_IN_PROGRESS
    BILLING_PROFILE_IN_COMPLETED
    BILLING_PROFILE_IN_FAILED
    etc.

There is a set of callbacks defined that are triggered as the process transitions between stages.

    callback `PortfolioStateMachine.after_in_progress_callback`
        The CSP api call is made as the process transitions into IN_PROGESS state for each state.

    callback `PortfolioStateMachine.is_csp_data_valid`
        validates the collected data.

A transition into the next state can be triggered using PortfolioStateMachine.trigger_next_transition`










