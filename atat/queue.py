from celery import Celery

celery = Celery(__name__)


def update_celery(celery, app):
    schedule_value = app.config.get("CELERYBEAT_SCHEDULE_VALUE", 60)
    celery.conf.update(app.config)
    celery.conf.CELERYBEAT_SCHEDULE = {
        "beat-dispatch_provision_portfolio": {
            "task": "atat.jobs.dispatch_provision_portfolio",
            "schedule": schedule_value,
        },
        "beat-dispatch_create_application": {
            "task": "atat.jobs.dispatch_create_application",
            "schedule": schedule_value,
        },
        "beat-dispatch_create_environment": {
            "task": "atat.jobs.dispatch_create_environment",
            "schedule": schedule_value,
        },
        "beat-dispatch_create_user": {
            "task": "atat.jobs.dispatch_create_user",
            "schedule": schedule_value,
        },
        "beat-dispatch_create_environment_role": {
            "task": "atat.jobs.dispatch_create_environment_role",
            "schedule": schedule_value,
        },
        "beat-send_task_order_files": {
            "task": "atat.jobs.send_task_order_files",
            "schedule": schedule_value,
        },
        "beat-create_billing_instruction": {
            "task": "atat.jobs.create_billing_instruction",
            "schedule": schedule_value,
        },
    }

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
