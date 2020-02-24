from threading import Thread

from atat.domain.exceptions import ClaimFailedException
from atat.models.utils import claim_for_update, claim_many_for_update

from tests.factories import EnvironmentFactory


def test_claim_for_update(session):
    environment = EnvironmentFactory.create()

    satisfied_claims = []
    exceptions = []

    # Two threads race to do work on environment and check out the lock
    class FirstThread(Thread):
        def run(self):
            try:
                with claim_for_update(environment) as env:
                    assert env.claimed_until
                    satisfied_claims.append("FirstThread")
            except ClaimFailedException:
                exceptions.append("FirstThread")

    class SecondThread(Thread):
        def run(self):
            try:
                with claim_for_update(environment) as env:
                    assert env.claimed_until
                    satisfied_claims.append("SecondThread")
            except ClaimFailedException:
                exceptions.append("SecondThread")

    t1 = FirstThread()
    t2 = SecondThread()
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    session.refresh(environment)

    assert len(satisfied_claims) == 1
    assert len(exceptions) == 1

    if satisfied_claims == ["FirstThread"]:
        assert exceptions == ["SecondThread"]
    else:
        assert satisfied_claims == ["SecondThread"]
        assert exceptions == ["FirstThread"]

    # The claim is released
    assert environment.claimed_until is None


def test_claim_many_for_update(session):
    environments = [
        EnvironmentFactory.create(),
        EnvironmentFactory.create(),
    ]

    satisfied_claims = []
    exceptions = []

    # Two threads race to do work on environment and check out the lock
    class FirstThread(Thread):
        def run(self):
            try:
                with claim_many_for_update(environments) as envs:
                    assert all([e.claimed_until for e in envs])
                    satisfied_claims.append("FirstThread")
            except ClaimFailedException:
                exceptions.append("FirstThread")

    class SecondThread(Thread):
        def run(self):
            try:
                with claim_many_for_update(environments) as envs:
                    assert all([e.claimed_until for e in envs])
                    satisfied_claims.append("SecondThread")
            except ClaimFailedException:
                exceptions.append("SecondThread")

    t1 = FirstThread()
    t2 = SecondThread()
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    for env in environments:
        session.refresh(env)

    assert len(satisfied_claims) == 1
    assert len(exceptions) == 1

    if satisfied_claims == ["FirstThread"]:
        assert exceptions == ["SecondThread"]
    else:
        assert satisfied_claims == ["SecondThread"]
        assert exceptions == ["FirstThread"]

    # The claim is released
    # assert environment.claimed_until is None
