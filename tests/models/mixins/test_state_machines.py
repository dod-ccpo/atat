from enum import Enum

import pytest
from pytest import raises

from atat.models.mixins.state_machines import (
    AzureStages,
    PortfolioStates,
    StageStates,
    StateMachineMisconfiguredError,
    _build_csp_states,
    _build_transitions,
    compose_state,
)
from tests.factories import PortfolioFactory
from tests.utils import lists_contain_same_members


class AzureStagesTest(Enum):
    TENANT = "tenant"
    POLICIES = "policies"


def test_find_and_call_stage_trigger():
    portfolio = PortfolioFactory.create(state="TENANT_IN_PROGRESS")
    portfolio.state_machine._find_and_call_stage_trigger("fail_")
    assert portfolio.state_machine.state == PortfolioStates.TENANT_FAILED


def test_find_and_call_stage_trigger_fails():
    portfolio = PortfolioFactory.create(state="UNSTARTED")
    with raises(StateMachineMisconfiguredError):
        portfolio.state_machine._find_and_call_stage_trigger(
            "wont_find_a_trigger_with_this_prefix"
        )
    assert portfolio.state_machine.state == PortfolioStates.CONFIGURATION_ERROR


@pytest.mark.state_machine
class Test_build_transitions:
    @pytest.fixture(scope="class")
    def states(self):
        states, _ = _build_transitions(AzureStagesTest)
        return states

    @pytest.fixture(scope="class")
    def transitions(self):
        _, transitions = _build_transitions(AzureStagesTest)
        return transitions

    def test_states(self, states):
        state_names = [s.get("name").name for s in states]
        expected_state_names = [
            "TENANT_CREATED",
            "TENANT_IN_PROGRESS",
            "TENANT_FAILED",
            "POLICIES_CREATED",
            "POLICIES_IN_PROGRESS",
            "POLICIES_FAILED",
        ]
        assert lists_contain_same_members(state_names, expected_state_names)

    def test_tags(self, states):
        tags = [s.get("tags") for s in states]
        expected_tags = [
            ["TENANT", "CREATED"],
            ["TENANT", "IN_PROGRESS"],
            ["TENANT", "FAILED"],
            ["POLICIES", "CREATED"],
            ["POLICIES", "IN_PROGRESS"],
            ["POLICIES", "FAILED"],
        ]
        assert lists_contain_same_members(tags, expected_tags)

    def test_triggers(self, transitions):
        triggers = [t.get("trigger") for t in transitions]
        expecte_triggers = [
            "create_tenant",
            "finish_tenant",
            "reset_tenant",
            "fail_tenant",
            "resume_progress_tenant",
            "create_policies",
            "finish_policies",
            "reset_policies",
            "fail_policies",
            "resume_progress_policies",
            "complete",
        ]
        assert lists_contain_same_members(triggers, expecte_triggers)

    def test_correct_states_for_trigger(self, transitions):
        created_to_in_progress_trigger = next(
            (t for t in transitions if t.get("trigger") == "create_policies")
        )
        assert (
            created_to_in_progress_trigger["source"] == PortfolioStates.TENANT_CREATED
        )
        assert (
            created_to_in_progress_trigger["dest"]
            == PortfolioStates.POLICIES_IN_PROGRESS
        )


@pytest.mark.state_machine
def test_build_csp_states():
    states = _build_csp_states(AzureStagesTest)
    assert list(states) == [
        "UNSTARTED",
        "COMPLETED",
        "CONFIGURATION_ERROR",
        "TENANT_CREATED",
        "TENANT_IN_PROGRESS",
        "TENANT_FAILED",
        "POLICIES_CREATED",
        "POLICIES_IN_PROGRESS",
        "POLICIES_FAILED",
    ]


@pytest.mark.state_machine
def test_compose_state():
    assert (
        compose_state(AzureStages.TENANT, StageStates.CREATED)
        == PortfolioStates.TENANT_CREATED
    )
