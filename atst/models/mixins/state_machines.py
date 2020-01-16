from enum import Enum


class StageStates(Enum):
    CREATED = "created"
    IN_PROGRESS = "in progress"
    FAILED = "failed"


class AzureStages(Enum):
    TENANT = "tenant"
    BILLING_PROFILE = "billing profile"
    ADMIN_SUBSCRIPTION = "admin subscription"


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


def _build_transitions(csp_stages):
    transitions = []
    states = []
    compose_state = lambda csp_stage, state: getattr(
        FSMStates, "_".join([csp_stage.name, state.name])
    )

    for stage_i, csp_stage in enumerate(csp_stages):
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

    def prepare_init(self, event):
        pass

    def before_init(self, event):
        pass

    def after_init(self, event):
        pass

    def prepare_start(self, event):
        pass

    def before_start(self, event):
        pass

    def after_start(self, event):
        pass

    def prepare_reset(self, event):
        pass

    def before_reset(self, event):
        pass

    def after_reset(self, event):
        pass

    def fail_stage(self, stage):
        fail_trigger = "fail" + stage
        if fail_trigger in self.machine.get_triggers(self.current_state.name):
            self.trigger(fail_trigger)

    def finish_stage(self, stage):
        finish_trigger = "finish_" + stage
        if finish_trigger in self.machine.get_triggers(self.current_state.name):
            self.trigger(finish_trigger)
