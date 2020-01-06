from dataclasses import dataclass
from typing import Dict#, Any

from sqlalchemy import Column, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import relationship, reconstructor
from sqlalchemy.dialects.postgresql import UUID

from transitions import Machine
from transitions.extensions.states import add_state_features, Tags

from flask import current_app as app

from atst.domain.csp.cloud import ConnectionException, UnknownServerException
from atst.domain.csp import MockCSP, AzureCSP
from atst.database import db
from atst.queue import celery
from atst.models.types import Id
from atst.models.base import Base
import atst.models.mixins as mixins
from atst.models.mixins.state_machines import (
    FSMStates, AzureStages, _build_transitions
)


@dataclass
class BaseCSPPayload:
    #{"username": "mock-cloud", "pass": "shh"}
    creds: Dict

@dataclass
class TenantCSPPayload(BaseCSPPayload):
    user_id: str
    password: str
    domain_name: str
    first_name: str
    last_name: str
    country_code: str
    password_recovery_email_address: str


@dataclass
class BillingProfileAddress():
    address: Dict
    """
    "address": {
        "firstName": "string",
        "lastName": "string",
        "companyName": "string",
        "addressLine1": "string",
        "addressLine2": "string",
        "addressLine3": "string",
        "city": "string",
        "region": "string",
        "country": "string",
        "postalCode": "string"
    },
    """
@dataclass
class BillingProfileCLINBudget():
    clinBudget: Dict
    """
        "clinBudget": {
            "amount": 0,
            "startDate": "2019-12-18T16:47:40.909Z",
            "endDate": "2019-12-18T16:47:40.909Z",
            "externalReferenceId": "string"
        }
    """

@dataclass
class BillingProfileCSPPayload(BaseCSPPayload, BillingProfileAddress, BillingProfileCLINBudget):
    displayName: str
    poNumber: str
    invoiceEmailOptIn: str

    """
    {
        "displayName": "string",
        "poNumber": "string",
        "address": {
            "firstName": "string",
            "lastName": "string",
            "companyName": "string",
            "addressLine1": "string",
            "addressLine2": "string",
            "addressLine3": "string",
            "city": "string",
            "region": "string",
            "country": "string",
            "postalCode": "string"
        },
        "invoiceEmailOptIn": true,
        Note: These last 2 are also the body for adding/updating new TOs/clins
        "enabledAzurePlans": [
            {
            "skuId": "string"
            }
        ],
        "clinBudget": {
            "amount": 0,
            "startDate": "2019-12-18T16:47:40.909Z",
            "endDate": "2019-12-18T16:47:40.909Z",
            "externalReferenceId": "string"
        }
    }
    """

@add_state_features(Tags)
class StateMachineWithTags(Machine):
    pass

class PortfolioStateMachine(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.DeletableMixin, mixins.FSMMixin,
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
        """
        This is called as a result of a sqlalchemy query.
        Attach a machine depending on the current state.
        """
        self.machine = StateMachineWithTags(
                model = self,
                send_event=True,
                initial=self.current_state if self.state else FSMStates.UNSTARTED,
                auto_transitions=False,
                after_state_change='after_state_change',
        )
        states, transitions = _build_transitions(AzureStages)
        self.machine.add_states(self.system_states+states)
        self.machine.add_transitions(self.system_transitions+transitions)

    @property
    def current_state(self):
        if isinstance(self.state, str):
            return getattr(FSMStates, self.state)
        return self.state

    def trigger_next_transition(self):
        state_obj = self.machine.get_state(self.state)

        if state_obj.is_system:
            if self.current_state in (FSMStates.UNSTARTED, FSMStates.STARTING):
                # call the first trigger availabe for these two system states
                trigger_name = self.machine.get_triggers(self.current_state.name)[0]
                self.trigger(trigger_name)

            elif self.current_state == FSMStates.STARTED:
                # get the first trigger that starts with 'create_'
                create_trigger = list(filter(lambda trigger: trigger.startswith('create_'),
                    self.machine.get_triggers(FSMStates.STARTED.name)))[0]
                self.trigger(create_trigger)

        elif state_obj.is_IN_PROGRESS:
            pass

        #elif state_obj.is_TENANT:
        #    pass
        #elif state_obj.is_BILLING_PROFILE:
        #    pass


    #@with_payload
    def after_in_progress_callback(self, event):
        stage = self.current_state.name.split('_IN_PROGRESS')[0].lower()

        if stage == 'tenant':
            payload = TenantCSPPayload(
                    creds={"username": "mock-cloud", "pass": "shh"},
                    user_id='123',
                    password='123',
                    domain_name='123',
                    first_name='john',
                    last_name='doe',
                    country_code='US',
                    password_recovery_email_address='password@email.com'
            )
        elif stage == 'billing_profile':
            payload = BillingProfileCSPPayload(
                    creds={"username": "mock-cloud", "pass": "shh"},
            )

        csp = event.kwargs.get('csp')

        if csp is not None:
            self.csp = AzureCSP(app).cloud
        else:
            self.csp = MockCSP(app).cloud

        for attempt in range(5):
            try:
                response = getattr(self.csp, 'create_'+stage)(payload)
            except (ConnectionException, UnknownServerException) as exc:
                print('caught exception. retry', attempt)
                continue
            else: break
        else:
            # failed all attempts
            getattr(self.machine, 'fail_'+stage)()

        if self.portfolio.csp_data is None:
            self.portfolio.csp_data = {}
        self.portfolio.csp_data[stage+"_data"] = response
        db.session.add(self.portfolio)
        db.session.commit()

        self.trigger('finish_'+stage)

    def is_csp_data_valid(self, event):
        # check portfolio csp details json field for fields
        if self.portfolio.csp_data is None or \
                not isinstance(self.portfolio.csp_data, dict):
            return False

        stage = self.current_state.name.split('_IN_PROGRESS')[0].lower()
        if stage == 'tenant':
            return all([
                "tenant_data" in self.portfolio.csp_data,
                "tenant_id" in self.portfolio.csp_data['tenant_data'],
                "user_id" in self.portfolio.csp_data['tenant_data'],
                "user_object_id" in self.portfolio.csp_data['tenant_data'],
            ])
        elif stage == 'billing_profile':
            return all([])

        print('failed condition', self.portfolio.csp_data)


    @property
    def application_id(self):
        return None
