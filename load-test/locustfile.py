import os
import re
from random import choice, choices, randrange
from functools import wraps

from locust import HttpUser, SequentialTaskSet, task, between

import names
from pyquery import PyQuery as pq
from uuid import uuid4
import string

# Provide username/password for basic auth
USERNAME = os.getenv("ATAT_BA_USERNAME", "")
PASSWORD = os.getenv("ATAT_BA_PASSWORD", "")

# Ability to disable SSL verification for bad cert situations
DISABLE_VERIFY = os.getenv("DISABLE_VERIFY", "true").lower() == "true"

# matcher used in extracting id from url path
ENTITY_ID_MATCHER = re.compile(
    ".*\/?(?:portfolios|applications|task_orders)\/([0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}).*",
    re.I,
)

# chance something will happen
NEW_PORTFOLIO_CHANCE = 10
NEW_APPLICATION_CHANCE = 10
NEW_TASK_ORDER_CHANCE = 10
NEW_LOGOUT_CHANCE = 10

dod_ids = set()


def update_user_profile(client, parent):
    # get csrf token
    user_url = "/user"
    response = client.get(user_url)
    csrf_token = get_csrf_token(response)

    d = pq(response.text)

    # get values from input form elements
    keys = (x.attr("name") for x in d(f"[initial-value]").items())
    update_user_body = {k: d(f"[key='{k}']").attr("initial-value") for k in keys}

    # get values from non-input form elements
    keys = (x.attr("name") for x in d(f"[v-bind\:initial-value]").items())
    update_user_body.update(
        {k: d(f"[key='{k}']").attr("v-bind:initial-value")[1:-1] for k in keys}
    )

    # update phone number and add csrf token
    update_user_body.update(
        {
            "csrf_token": csrf_token,
            "phone_number": "".join(choices(string.digits, k=10)),
            "email": client.email,
            "citizenship": client.citizenship,
            "service_branch": client.service_branch,
            "designation": client.designation,
        }
    )

    # post new values for user profiles
    client.post(user_url, update_user_body, headers={"Referer": parent.host + user_url})


def create_application(client, parent, portfolio_id):
    # get new application page for csrf token
    create_app_url = f"/portfolios/{portfolio_id}/applications/new"
    new_app_form = client.get(create_app_url)
    csrf_token = get_csrf_token(new_app_form)

    # create new application
    response = client.post(
        create_app_url,
        {
            "name": f"Load Test Created - {''.join(choices(string.ascii_letters, k=5))}",
            "description": "Description",
            "csrf_token": csrf_token,
        },
        headers={"Referer": parent.host + create_app_url},
    )
    application_id = extract_id(response.url)

    # set up application environments
    create_environments_url = f"/applications/{application_id}/new/step_2"
    client.post(
        create_environments_url + f"?portfolio_id={portfolio_id}",
        {
            "environment_names-0": "Development",
            "environment_names-1": "Testing",
            "environment_names-2": "Staging",
            "environment_names-3": "Production",
            "csrf_token": csrf_token,
        },
        headers={"Referer": parent.host + create_environments_url},
    )

    # get environments' ids from step 3 of application creation
    create_team_members_url = f"/applications/{application_id}/new/step_3"
    create_team_members_response = client.get(create_team_members_url)
    d = pq(create_team_members_response.text)
    env_0_id = d("#environment_roles-0-environment_id").val()
    env_1_id = d("#environment_roles-1-environment_id").val()

    # create application member
    client.post(
        create_team_members_url + f"?application_id={application_id}",
        {
            "user_data-first_name": "Bob",
            "user_data-last_name": "Smith",
            "user_data-dod_id": "1234567890",
            "user_data-email": "user@email.com",
            "environment_roles-0-environment_id": env_0_id,
            "environment_roles-0-role": "ADMIN",
            "environment_roles-0-environment_name": "First Env",
            "environment_roles-1-environment_id": env_1_id,
            "environment_roles-1-role": "No Access",
            "environment_roles-1-environment_name": "Second Env",
            "perms_env_mgmt": True,
            "perms_team_mgmt": True,
            "csrf_token": csrf_token,
        },
        headers={"Referer": parent.host + create_team_members_url},
    )


def create_portfolio(client, parent):
    # get portfolios page for csrf token
    response = client.get("/portfolios/new")
    csrf_token = get_csrf_token(response)

    # create new portfolio
    portfolios_url = "/portfolios"
    response = client.post(
        portfolios_url,
        {
            "name": f"Load Test Created - {''.join(choices(string.ascii_letters, k=5))}",
            "defense_component": "army",
            "description": "Test",
            "csrf_token": csrf_token,
        },
        headers={"Referer": parent.host + portfolios_url},
    )

    return extract_id(response.url)


def create_task_order(client, parent, portfolio_id):
    # get init page for csrf token
    response = client.get(f"/portfolios/{portfolio_id}/task_orders/form/step_1")
    csrf_token = get_csrf_token(response)

    # submit TO pdf file
    upload_task_order_pdf_url = f"/portfolios/{portfolio_id}/task_orders/form/step-1"
    response = client.post(
        upload_task_order_pdf_url,
        {
            "pdf-filename": "sample.pdf",
            "pdf-object_name": uuid4(),
            "csrf_token": csrf_token,
        },
        headers={"Referer": parent.host + upload_task_order_pdf_url},
    )

    # get TO ID
    task_order_id = extract_id(response.url)

    # set TO number
    number = "".join(choices(string.digits, k=choice(range(13, 18))))
    set_task_order_number_url = f"/task_orders/{task_order_id}/form/step_2"
    client.post(
        set_task_order_number_url,
        {"number": number, "csrf_token": csrf_token},
        headers={"Referer": parent.host + set_task_order_number_url},
    )

    # set TO parameters
    clins_number = "".join(choices(string.digits, k=4))
    client.post(
        f"/task_orders/{task_order_id}/form/step_3",
        {
            "csrf_token": csrf_token,
            "clins-0-number": clins_number,
            "clins-0-jedi_clin_type": "JEDI_CLIN_1",
            "clins-0-total_amount": 100,
            "clins-0-obligated_amount": 50,
            "clins-0-start_date": "01/11/2020",
            "clins-0-end_date": "01/11/2021",
        },
    )

    # submit TO
    submit_task_order_url = f"/task_orders/{task_order_id}/submit"
    client.post(
        submit_task_order_url,
        {"csrf_token": csrf_token, "signature": "y", "confirm": "y",},
        headers={"Referer": parent.host + submit_task_order_url},
    )


def get_portfolios(client):
    # get all portfolios
    response = client.get("/home")
    d = pq(response.text)
    return [p.attr("href") for p in d(".sidenav__link").items()]


def get_applications(client, portfolio_id):
    # get all applications for a portfolio
    response = client.get(f"/portfolios/{portfolio_id}/applications")
    d = pq(response.text)
    return [
        p.attr("href")
        for p in d(".portfolio-applications .accordion__header-text a").items()
    ]


def has_task_orders(client, portfolio_id):
    response = client.get(f"/portfolios/{portfolio_id}/task_orders")
    d = pq(response.text)
    return not d(".portfolio-funding .empty-state")


def get_csrf_token(response):
    # get csrf token from html
    d = pq(response.text)
    return d("#csrf_token").val()


def extract_id(path):
    # get an id from a url path
    entity_id_match = ENTITY_ID_MATCHER.match(path)

    assert entity_id_match is not None, f"Could not find id in {path}"
    if entity_id_match:
        return entity_id_match.group(1)


def get_new_dod_id():
    while True:
        dod_id = "1" + "".join(choice(string.digits) for _ in range(9))
        if dod_id not in dod_ids:
            dod_ids.add(dod_id)
            return dod_id


def get_new_name():
    return names.get_full_name().split(" ")


def login_as(client):
    dod_id = get_new_dod_id()
    first_name, last_name = get_new_name()

    client.dod_id = dod_id
    client.first_name = first_name
    client.last_name = last_name
    client.email = "".join([first_name.lower(), last_name.lower(), "@loadtest.atat"])
    client.service_branch = choice(
        [
            "air_force",
            "army",
            "marine_corps",
            "navy",
            "space_force",
            "ccmd_js",
            "dafa",
            "osd_psas",
            "other",
        ]
    )
    client.citizenship = choice(["United States", "Foreign National", "Other"])
    client.designation = choice(["military", "civilian", "contractor"])

    result = client.get(
        f"/dev-new-user?first_name={first_name}&last_name={last_name}&dod_id={dod_id}"
    )

    client.logged_in = result.ok


def log_out(client):
    client.get("/logout")
    client.logged_in = False


def user_status(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client = args[0].client

        if not client.logged_in:
            result = client.get(f"/login-local?dod_id={client.dod_id}")
            client.logged_in = result.ok

        f(*args, **kwargs)

        if randrange(0, 100) < NEW_LOGOUT_CHANCE:
            log_out(client)

    return decorated_function


class UserBehavior(SequentialTaskSet):
    def on_start(self):
        self.client.verify = not DISABLE_VERIFY
        login_as(self.client)

    @user_status
    @task
    def user_profile(self):
        update_user_profile(self.client, self.parent)

    @user_status
    @task
    def portfolio(self):
        client = self.client
        portfolio_links = get_portfolios(client)

        if not portfolio_links or randrange(0, 100) < NEW_PORTFOLIO_CHANCE:
            self.portfolio_id = create_portfolio(client, self.parent)
        else:
            self.portfolio_id = extract_id(choice(portfolio_links))

    @user_status
    @task
    def application(self):
        client = self.client
        portfolio_id = self.portfolio_id

        application_links = get_applications(client, portfolio_id)
        if not application_links or randrange(0, 100) < NEW_APPLICATION_CHANCE:
            create_application(client, self.parent, portfolio_id)

    @user_status
    @task
    def task_order(self):
        if (
            not has_task_orders(self.client, self.portfolio_id)
            or randrange(0, 100) < NEW_TASK_ORDER_CHANCE
        ):
            create_task_order(self.client, self.parent, self.portfolio_id)

    def on_stop(self):
        log_out(self.client)


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(3, 9)


if __name__ == "__main__":
    # if run as the main file, will spin up a single locust
    WebsiteUser().run()
