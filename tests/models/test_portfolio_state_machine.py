from unittest.mock import Mock, patch

import pendulum
import pydantic
import pytest
from pytest import raises
from tests.factories import (
    ApplicationFactory,
    CLINFactory,
    PortfolioFactory,
    PortfolioStateMachineFactory,
    TaskOrderFactory,
    UserFactory,
)

from atat.models.mixins.state_machines import (
    AzureStages,
    PortfolioStates,
    StateMachineMisconfiguredError,
)
from atat.models.portfolio_state_machine import (
    PortfolioStateMachine,
    _stage_to_classname,
    get_stage_csp_class,
)

# TODO: Write failure case tests


@pytest.fixture
def portfolio():
    today = pendulum.today()
    yesterday = today.subtract(days=1)
    future = today.add(days=100)

    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=owner)
    ApplicationFactory.create(portfolio=portfolio, environments=[{"name": "dev"}])

    TaskOrderFactory.create(
        portfolio=portfolio,
        signed_at=yesterday,
        clins=[CLINFactory.create(start_date=yesterday, end_date=future)],
    )

    return portfolio


@pytest.fixture
def state_machine(portfolio):
    return PortfolioStateMachineFactory.create(portfolio=portfolio)


@pytest.mark.state_machine
def test_fsm_creation(portfolio):
    sm = PortfolioStateMachineFactory.create(portfolio=portfolio)
    assert sm.portfolio


@pytest.mark.state_machine
class TestTriggerNextTransition:
    def test_failed(self, state_machine):
        state_machine.state = PortfolioStates.TENANT_FAILED
        state_machine.trigger_next_transition(
            csp_data=state_machine.portfolio.to_dictionary()
        )
        assert state_machine.current_state == PortfolioStates.TENANT_CREATED

    def test_started(self, state_machine):
        state_machine.state = PortfolioStates.UNSTARTED
        state_machine.trigger_next_transition(
            csp_data=state_machine.portfolio.to_dictionary()
        )
        assert state_machine.current_state == PortfolioStates.TENANT_CREATED


@pytest.mark.state_machine
def test_stage_to_classname():
    assert (
        _stage_to_classname(AzureStages.BILLING_PROFILE_CREATION.name)
        == "BillingProfileCreation"
    )


@pytest.mark.state_machine
def test_get_stage_csp_class():
    csp_class = get_stage_csp_class(list(AzureStages)[0].name.lower(), "payload")
    assert isinstance(csp_class, pydantic.main.ModelMetaclass)


@pytest.mark.state_machine
def test_get_stage_csp_class_import_fail():
    with pytest.raises(StateMachineMisconfiguredError):
        get_stage_csp_class("doesnotexist", "payload")


@pytest.mark.state_machine
def test_state_machine_valid_data_classes_for_stages():
    for stage in AzureStages:
        assert get_stage_csp_class(stage.name.lower(), "payload") is not None
        assert get_stage_csp_class(stage.name.lower(), "result") is not None


@pytest.mark.state_machine
def test_attach_machine(state_machine):
    initial_stages = [
        "reset",
        "configuration_error",
        "create_tenant",
        "finish_tenant",
        "fail_tenant",
        "resume_progress_tenant",
    ]
    state_machine.attach_machine()
    assert list(state_machine.machine.events)[: len(initial_stages)] == initial_stages


@pytest.mark.state_machine
@patch("atat.models.PortfolioStateMachine._do_provisioning_stage")
def test_after_in_progress_callback(_do_provisioning_stage):
    # Given: a portfolio state machine is attempting a provisioning stage
    portfolio = PortfolioFactory.create(state="TENANT_IN_PROGRESS")
    # Given: The provisioning stage throws an exception
    _do_provisioning_stage.side_effect = Exception()

    # When I run the task, then:
    # The exception is re-raised
    with raises(Exception):
        portfolio.state_machine.after_in_progress_callback(Mock())
    # Then the state machine fails the stage
    assert portfolio.state_machine.state == PortfolioStates.TENANT_FAILED


@pytest.mark.state_machine
def test_current_state_property(state_machine):
    assert state_machine.current_state == PortfolioStates.UNSTARTED
    state_machine.state = PortfolioStates.TENANT_IN_PROGRESS
    assert state_machine.current_state == PortfolioStates.TENANT_IN_PROGRESS
    state_machine.state = "UNSTARTED"
    assert state_machine.current_state == PortfolioStates.UNSTARTED


@pytest.mark.state_machine
def test_start_next_stage(state_machine):
    state_machine.state = PortfolioStates.UNSTARTED
    state_machine.start_next_stage(csp_data=state_machine.portfolio.to_dictionary())
    # _IN_PROGRESS automatically triggers callback which fails or finishes the stage
    assert state_machine.state == PortfolioStates.TENANT_CREATED


@pytest.mark.state_machine
def test_resume_stage_progress(state_machine):
    state_machine.state = PortfolioStates.TENANT_FAILED
    state_machine.resume_stage_progress(
        csp_data=state_machine.portfolio.to_dictionary()
    )
    # _IN_PROGRESS automatically triggers callback which fails or finishes the stage
    assert state_machine.state == PortfolioStates.TENANT_CREATED


@pytest.mark.state_machine
def test_fail_stage(state_machine):
    state_machine.state = PortfolioStates.TENANT_IN_PROGRESS
    state_machine.fail_stage()
    assert state_machine.state == PortfolioStates.TENANT_FAILED


@pytest.mark.state_machine
def test_finish_stage(state_machine):
    state_machine.portfolio.csp_data = {}
    state_machine.state = PortfolioStates.TENANT_IN_PROGRESS
    state_machine.finish_stage()
    assert state_machine.state == PortfolioStates.TENANT_CREATED


@pytest.mark.state_machine
@pytest.mark.parametrize(
    "state_machine_state",
    [
        (PortfolioStates.TENANT_IN_PROGRESS),
        (PortfolioStates.TENANT_CREATED),
        (PortfolioStates.TENANT_FAILED),
    ],
)
def test_current_stage(state_machine_state, state_machine):
    state_machine.state = state_machine_state
    assert state_machine.current_stage == "tenant"


@pytest.mark.state_machine
def test_state_machine_initialization(state_machine):
    for stage in AzureStages:

        # check that all stages have a 'create' and 'fail' triggers
        stage_name = stage.name.lower()
        for trigger_prefix in ["create", "fail"]:
            assert hasattr(state_machine, trigger_prefix + "_" + stage_name)

        # check that machine
        in_progress_triggers = state_machine.machine.get_triggers(
            stage.name + "_IN_PROGRESS"
        )
        assert [
            "reset",
            "configuration_error",
            "finish_" + stage_name,
            "fail_" + stage_name,
        ] == in_progress_triggers

        started_triggers = state_machine.machine.get_triggers("UNSTARTED")
        create_trigger = next(
            filter(
                lambda trigger: trigger.startswith("create_"),
                state_machine.machine.get_triggers(PortfolioStates.UNSTARTED.name),
            ),
            None,
        )
        assert ["reset", "configuration_error", create_trigger] == started_triggers


@pytest.mark.state_machine
def test_fsm_transition_start(state_machine: PortfolioStateMachine):

    expected_states = [
        PortfolioStates.TENANT_CREATED,
        PortfolioStates.BILLING_PROFILE_CREATION_CREATED,
        PortfolioStates.BILLING_PROFILE_VERIFICATION_CREATED,
        PortfolioStates.BILLING_PROFILE_TENANT_ACCESS_CREATED,
        PortfolioStates.TASK_ORDER_BILLING_CREATION_CREATED,
        PortfolioStates.TASK_ORDER_BILLING_VERIFICATION_CREATED,
        PortfolioStates.BILLING_INSTRUCTION_CREATED,
        PortfolioStates.PRODUCT_PURCHASE_CREATED,
        PortfolioStates.PRODUCT_PURCHASE_VERIFICATION_CREATED,
        PortfolioStates.TENANT_PRINCIPAL_APP_CREATED,
        PortfolioStates.TENANT_PRINCIPAL_CREATED,
        PortfolioStates.TENANT_PRINCIPAL_CREDENTIAL_CREATED,
        PortfolioStates.ADMIN_ROLE_DEFINITION_CREATED,
        PortfolioStates.PRINCIPAL_ADMIN_ROLE_CREATED,
        PortfolioStates.PRINCIPAL_APP_INVITE_PERMISSION_CREATED,
        PortfolioStates.INITIAL_MGMT_GROUP_CREATED,
        PortfolioStates.INITIAL_MGMT_GROUP_VERIFICATION_CREATED,
        PortfolioStates.TENANT_ADMIN_OWNERSHIP_CREATED,
        PortfolioStates.TENANT_PRINCIPAL_OWNERSHIP_CREATED,
        PortfolioStates.BILLING_OWNER_CREATED,
        PortfolioStates.TENANT_ADMIN_CREDENTIAL_RESET_CREATED,
        PortfolioStates.POLICIES_CREATED,
        PortfolioStates.COMPLETED,
    ]

    config = {"billing_account_name": "billing_account_name"}

    assert state_machine.state == PortfolioStates.UNSTARTED

    for expected_state in expected_states:
        if state_machine.portfolio.csp_data is not None:
            csp_data = state_machine.portfolio.csp_data
        else:
            csp_data = {}
        collected_data = {
            **state_machine.portfolio.to_dictionary(),
            **csp_data,
            **config,
        }
        state_machine.trigger_next_transition(csp_data=collected_data)
        assert state_machine.state == expected_state
