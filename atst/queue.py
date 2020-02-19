from celery import Celery


celery = Celery(__name__)


def update_celery(celery, app):
    celery.conf.update(app.config)
    celery.conf.CELERYBEAT_SCHEDULE = {
        "beat-dispatch_provision_portfolio": {
            "task": "atst.jobs.dispatch_provision_portfolio",
            "schedule": 60,
        },
        "beat-dispatch_create_application": {
            "task": "atst.jobs.dispatch_create_application",
            "schedule": 60,
        },
        "beat-dispatch_create_environment": {
            "task": "atst.jobs.dispatch_create_environment",
            "schedule": 60,
        },
        "beat-dispatch_create_user": {
            "task": "atst.jobs.dispatch_create_user",
            "schedule": 60,
        },
        "beat-dispatch_create_environment_role": {
            "task": "atst.jobs.dispatch_create_environment_role",
            "schedule": 60,
        },
        "beat-send_task_order_files": {
            "task": "atst.jobs.send_task_order_files",
            "schedule": 60,
        },
    }

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
