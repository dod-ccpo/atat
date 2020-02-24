from flask import current_app as app


def generate_user_principal_name(name, domain_name):
    mail_name = generate_mail_nickname(name)
    return f"{mail_name}@{domain_name}.{app.config.get('OFFICE_365_DOMAIN')}"


def generate_mail_nickname(name):
    return name.replace(" ", ".").lower()
