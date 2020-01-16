import pytest

from tests.factories import (
    PortfolioFactory,
    PortfolioStateMachineFactory,
)

from atst.models import FSMStates


@pytest.fixture(scope="function")
def portfolio():
    portfolio = PortfolioFactory.create()
    return portfolio


def test_fsm_creation(portfolio):
    sm = PortfolioStateMachineFactory.create(portfolio=portfolio)
    assert sm.portfolio


def test_fsm_transition_start(portfolio):
    sm = PortfolioStateMachineFactory.create(portfolio=portfolio)
    assert sm.portfolio
    assert sm.state == FSMStates.UNSTARTED

    # next_state does not create the trigger callbacks !!!
    # sm.next_state()

    sm.init()
    assert sm.state == FSMStates.STARTING

    sm.start()
    assert sm.state == FSMStates.STARTED
    sm.create_tenant(a=1, b=2)
    assert sm.state == FSMStates.TENANT_CREATED
