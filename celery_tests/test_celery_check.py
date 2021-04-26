from atat.app import celery, make_app, make_config

config = make_config()
app = make_app(config)
app.app_context().push()


def test_verify_celery_tasks():
    i = celery.control.inspect()
    tasks = i.registered()
    registered_tasks = []
    if tasks:
        for key in dict.keys(tasks):
            for task in tasks[key]:
                registered_tasks.append(task)

    assert registered_tasks == [
        "atat.jobs.create_application",
        "atat.jobs.create_billing_instruction",
        "atat.jobs.create_environment",
        "atat.jobs.create_environment_role",
        "atat.jobs.create_subscription",
        "atat.jobs.create_user",
        "atat.jobs.dispatch_create_application",
        "atat.jobs.dispatch_create_environment",
        "atat.jobs.dispatch_create_environment_role",
        "atat.jobs.dispatch_create_user",
        "atat.jobs.dispatch_provision_portfolio",
        "atat.jobs.provision_portfolio",
        "atat.jobs.send_mail",
        "atat.jobs.send_notification_mail",
        "atat.jobs.send_task_order_files",
    ]
