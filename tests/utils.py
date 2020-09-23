import os
from contextlib import contextmanager
from unittest.mock import Mock

import pendulum
from flask import template_rendered

import tests.factories as factories
from atat.utils.notification_sender import NotificationSender


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class FakeLogger:
    def __init__(self):
        self.messages = []
        self.extras = []

    def log(self, _lvl, msg, *args, **kwargs):
        self._log(_lvl, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log("debug", msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log("info", msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log("warning", msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log("error", msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self._log("exception", msg, *args, **kwargs)

    def _log(self, _lvl, msg, *args, **kwargs):
        self.messages.append(msg % args)
        if "extra" in kwargs:
            self.extras.append(kwargs["extra"])


FakeNotificationSender = lambda: Mock(spec=NotificationSender)


def lists_contain_same_members(list_1, list_2):
    return sorted(list_1) == sorted(list_2)


class EnvQueryTest:
    @property
    def NOW(self):
        return pendulum.now(tz="UTC")

    @property
    def YESTERDAY(self):
        return self.NOW.subtract(days=1)

    @property
    def TOMORROW(self):
        return self.NOW.add(days=1)

    def create_portfolio_with_clins(
        self,
        start_and_end_dates,
        env_data=None,
        app_data=None,
        state_machine_status=None,
        task_order_signed_at=pendulum.now(tz="UTC"),
    ):
        env_data = env_data or {}
        app_data = app_data or {}
        return factories.PortfolioFactory.create(
            state=state_machine_status,
            applications=[
                {
                    "name": "Mos Eisley",
                    "description": "Where Han shot first",
                    "environments": [{"name": "thebar", **env_data}],
                    **app_data,
                }
            ],
            task_orders=[
                {
                    "create_clins": [
                        {"start_date": start_date, "end_date": end_date}
                        for (start_date, end_date) in start_and_end_dates
                    ],
                    "signed_at": task_order_signed_at,
                }
            ],
        )
