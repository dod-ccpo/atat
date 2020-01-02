from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, text, Enum as SQLAEnum
from sqlalchemy.orm import relationship, reconstructor
from sqlalchemy.dialects.postgresql import UUID


from transitions import Machine
from transitions.extensions.states import add_state_features, Tags

from flask import current_app as app

from atst.queue import celery
from atst.models.types import Id
from atst.models.base import Base
from atst.domain.csp import MockCSP, AzureCSP
from atst.domain.csp.cloud import ConnectionException, UnknownServerException
import atst.models.mixins as mixins
from atst.database import db


class FSMStageStates(Enum):
    CREATED = "created"
    IN_PROGRESS = "in progress"
    FAILED = "failed"

class FSMStages(Enum):
    TENANT = "tenant"
    BILLING_PROFILE = "billing profile"
    ADMIN_SUBSCRIPTION = "admin subscription"

states = {
    'UNSTARTED' : "unstarted",
    'STARTING' : "starting",
    'STARTED' : "started",
    'COMPLETED' : "completed",
    'FAILED' : "failed",
}
for stage in FSMStages:
    for state in FSMStageStates:
        states[stage.name+"_"+state.name] = stage.value+" "+state.value

FSMStates = Enum('FSMStates', states)


"""
class FSMStates(Enum):
    UNSTARTED = "unstarted"
    STARTING = "starting"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"

    TENANT_CREATED = "tenant created"
    TENANT_IN_PROGRESS = "tenant creation in progress"
    TENANT_FAILED = "tenant creation failed"

    BILLING_PROFILE_CREATED = "billing profile created"
    BILLING_PROFILE_IN_PROGRESS = "billing profile creation in progress"
    BILLING_PROFILE_FAILED = "billing profile creation failed"

    BILLING_PROFILE_UPDATED = "billing profile updated"
    BILLING_PROFILE_UPDATE_IN_PROGRESS = "billing profile update in progress"
    BILLING_PROFILE_UPDATE_FAILED = "billing profile update failed"

    ADMIN_SUBSCRIPTION_CREATED = "admin subscription created"
    ADMIN_SUBSCRIPTION_IN_PROGRESS = "admin subscription creation in progress"
    ADMIN_SUBSCRIPTION_FAILED = "admin subscription creation failed"
"""


class TenantMixin():

    tenant_states = [
        {'name': FSMStates.TENANT_CREATED.name, 'tags': ['tenant']},
        {'name': FSMStates.TENANT_IN_PROGRESS.name, 'tags': ['tenant', 'in_progress']},
        {'name': FSMStates.TENANT_FAILED.name, 'tags': ['tenant']},
    ]

    transitions_tenant = [
        {
            'trigger': 'create_tenant',
            'source': FSMStates.STARTED, 'dest': FSMStates.TENANT_IN_PROGRESS,
            'prepare': 'prepare_tenant',
            'before': 'before_tenant',
            'after': 'after_tenant',
        },
        {
            'trigger': 'finish_tenant',
            'source': FSMStates.TENANT_IN_PROGRESS, 'dest': FSMStates.TENANT_CREATED,
            'conditions': ['is_tenant_created',],
        },
        {
            'trigger': 'fail_tenant',
            'source': FSMStates.TENANT_IN_PROGRESS, 'dest': FSMStates.TENANT_FAILED
        },
    ]

    def prepare_tenant(self, event): pass
    def before_tenant(self, event): pass

    def after_tenant(self, event):
        # enter in_progress state and make api call
        # after state transitions to TENANT_IN_PROGRESS.
        kwargs = dict(creds={"username": "mock-cloud", "pass": "shh"},
                    user_id='123',
                    password='123',
                    domain_name='123',
                    first_name='john',
                    last_name='doe',
                    country_code='US',
                    password_recovery_email_address='password@email.com')

        csp = event.kwargs.get('csp')

        if csp is not None:
            self.csp = AzureCSP(app).cloud
        else:
            self.csp = MockCSP(app).cloud

        for attempt in range(5):
            try:
                response = self.csp.create_tenant(**kwargs)
            except (ConnectionException, UnknownServerException) as exc:
                print('caught exception. retry', attempt)
                continue
            else: break
        else:
            # failed all attempts
            self.machine.fail_tenant()


        if self.portfolio.csp_data is None:
            self.portfolio.csp_data = {}
        self.portfolio.csp_data["tenant_data"] = response
        db.session.add(self.portfolio)
        db.session.commit()


    def is_tenant_created(self, event):
        # check portfolio csp details json field for fields

        if self.portfolio.csp_data is None or \
                not isinstance(self.portfolio.csp_data, dict):
            return False

        return all([
            "tenant_data" in self.portfolio.csp_data,
            "tenant_id" in self.portfolio.csp_data['tenant_data'],
            "user_id" in self.portfolio.csp_data['tenant_data'],
            "user_object_id" in self.portfolio.csp_data['tenant_data'],
        ])

class BillingProfileMixin:

    billing_profile_states = [
        {'name': FSMStates.BILLING_PROFILE_CREATED.name, 'tags': ['billing_profile']},
        {'name': FSMStates.BILLING_PROFILE_IN_PROGRESS.name, 'tags': ['billing_profile', 'in_progress']},
        {'name': FSMStates.BILLING_PROFILE_FAILED.name, 'tags': ['billing_profile']},
    ]

    transitions_billing_profile = [
        {
            'trigger': 'create_billing_profile',
            'source': FSMStates.TENANT_CREATED,
            'dest': FSMStates.BILLING_PROFILE_IN_PROGRESS,
            'prepare': 'prepare_billing_profile',
            'before': 'before_billing_profile',
            'after': 'after_billing_profile',
        },
        {
            'trigger': 'finish_billing_profile',
            'source': FSMStates.BILLING_PROFILE_IN_PROGRESS,
            'dest': FSMStates.BILLING_PROFILE_CREATED,
            'conditions': ['is_billing_profile_created',],
        },
        {
            'trigger': 'fail_billing_profile',
            'source': FSMStates.BILLING_PROFILE_IN_PROGRESS,
            'dest': FSMStates.BILLING_PROFILE_FAILED
        },
    ]

    def prepare_billing_profile(self, event): pass
    def before_billing_profile(self, event): pass

    def after_billing_profile(self, event):
        # enter in_progress state and make api call
        # after state transitions to BILLING_IN_PROGRESS.

        csp = event.kwargs.get('csp')
        creds={"username": "mock-cloud", "pass": "shh"}

        if csp is not None:
            self.csp = AzureCSP(app).cloud
        else:
            self.csp = MockCSP(app).cloud

        for attempt in range(5):
            try:
                response = self.csp.create_billing_profile({}, '123', **kwargs)
            except (ConnectionException, UnknownServerException) as exc:
                print('caught exception. retry', attempt)
                continue
            else: break
        else:
            # failed all attempts
            self.machine.fail_billing_profile()


        if self.portfolio.csp_data is None:
           self.portfolio.csp_data = {}
        self.portfolio.csp_data["billing_profile_data"] = response
        db.session.add(self.portfolio)
        db.session.commit()

    def is_billing_profile_created(self, event):
        # check portfolio csp details json field for fields

        if self.portfolio.csp_data is None or \
                not isinstance(self.portfolio.csp_data, dict):
            return False

        return all([
            #"tenant_data" in self.portfolio.csp_data,
            #"tenant_id" in self.portfolio.csp_data['tenant_data'],
            #"user_id" in self.portfolio.csp_data['tenant_data'],
            #"user_object_id" in self.portfolio.csp_data['tenant_data'],
        ])

class AzureFSMMixin():

    states_base = [
        {'name': FSMStates.UNSTARTED.name, 'tags': ['system']},
        {'name': FSMStates.STARTING.name, 'tags': ['system']},
        {'name': FSMStates.STARTED.name, 'tags': ['system']},
        {'name': FSMStates.FAILED.name, 'tags': ['system']},
        {'name': FSMStates.COMPLETED.name, 'tags': ['system']},
    ]

    transitions_base = [
        {'trigger': 'init', 'source': FSMStates.UNSTARTED, 'dest': FSMStates.STARTING},
        {'trigger': 'start', 'source': FSMStates.STARTING, 'dest': FSMStates.STARTED},
        {'trigger': 'reset', 'source': '*', 'dest': FSMStates.UNSTARTED},
        {'trigger': 'fail', 'source': '*', 'dest': FSMStates.FAILED,}
    ]

    def prepare_init(self, event): pass
    def before_init(self, event): pass
    def after_init(self, event): pass

    def prepare_start(self, event): pass
    def before_start(self, event): pass
    def after_start(self, event): pass

    def prepare_reset(self, event): pass
    def before_reset(self, event): pass
    def after_reset(self, event): pass


@add_state_features(Tags)
class StateMachineWithTags(Machine):
    pass

class PortfolioStateMachine(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.DeletableMixin,
    AzureFSMMixin,
    TenantMixin,
    BillingProfileMixin,
):
    __tablename__ = "portfolio_state_machines"

    id = Id()

    portfolio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id"),
    )
    portfolio = relationship("Portfolio", back_populates="state_machine")

    state = Column(
        SQLAEnum(FSMStates, native_enum=False, create_constraint=False),
        default=FSMStates.UNSTARTED, nullable=False
    )

    def __init__(self, portfolio, csp=None, **kwargs):
        self.portfolio = portfolio
        self.attach_machine()

    def after_state_change(self, event):
        db.session.add(self)
        db.session.commit()

    @reconstructor
    def attach_machine(self):
        """ This is called as a result of a sqlalchemy query.  Attach a machine depending on the current state.
        """
        self.machine = StateMachineWithTags(
                model = self,
                send_event=True,
                initial=self.state.name if self.state else FSMStates.UNSTARTED.name,
                auto_transitions=False,
                after_state_change='after_state_change',
        )
        #TODO see if based on current state tag some of these states/transitions can be excluded
        #if self.machine.get_state(self.state).is_system
        #if self.machine.get_state(self.state).is_tenant_creation
        #if self.machine.get_state(self.state).is_billing_profile_creation


        self.machine.add_states(self.states_base)
        self.machine.add_transitions(self.transitions_base)

        PROVISION_STAGE_STATES = ['IN_PROGRESS', 'CREATED', 'FAILED']
        PROVISION_STAGES = ['TENANT', 'BILLING_PROFILE']
        states = []
        transitions = []
        fsmstate = lambda stage, state: FSMStates.__members__.get("_".join([stage, state]))
        for stage_i, stage in enumerate(PROVISION_STAGES):
            for state_i, state in enumerate(PROVISION_STAGE_STATES):
                states.append(dict(name=fsmstate(stage, state).name, tags=[stage, state]))
                if state_i == 0:
                    if stage_i > 0:
                        src = fsmstate(PROVISION_STAGES[stage_i-1], 'CREATED')
                    else:
                        src=FSMStages.STARTED
                    transitions.append(
                        dict(
                            trigger='create_'+stage.lower(),
                            source=src, dest=stage+"_"+state,
                            prepare='prepare_' + stage.lower(),
                            before='before_' + stage.lower(),
                            after='after_' + stage.lower(),
                        )
                    )
                elif state_i == 1:
                    transitions.append(
                        dict(
                            trigger='create_'+stage.lower(),
                            source='',
                            dest='',
                        )
                    )
                elif state_i == 0:
                    transitions.append(
                        dict(
                            trigger='create_'+stage.lower(),
                            source='',
                            dest='',
                        )
                    )

        self.machine.add_states(states)
        self.machine.add_transitions(transitions)


    @property
    def application_id(self):
        return None
