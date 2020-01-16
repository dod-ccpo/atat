import os
import re
from random import choice, choices, randrange
from urllib.parse import urlparse

from locust import HttpLocust, TaskSequence, seq_task

from pyquery import PyQuery as pq

# Provide username/password for basic auth
USERNAME = os.getenv("ATAT_BA_USERNAME", "")
PASSWORD = os.getenv("ATAT_BA_PASSWORD", "")

# Ability to disable SSL verification for bad cert situations
DISABLE_VERIFY = os.getenv("DISABLE_VERIFY", "true").lower() == "true"

# Alpha numerics for random entity names
LETTERS = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890" #pragma: allowlist secret

NEW_PORTFOLIO_CHANCE = 10
NEW_APPLICATION_CHANCE = 10


def login(l):
    l.client.get("/login-dev", auth=(USERNAME, PASSWORD))


def logout(l):
    l.client.get("/logout")


def get_index(l):
    l.client.get("/")


def get_csrf_token(response):
    d = pq(response.text)
    return d("#csrf_token").val()


def extract_id(path):
    entity_id_matcher = re.compile(
        ".*\/?(?:portfolios|applications)\/([0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}).*",
        re.I,
    )

    entity_id_match = entity_id_matcher.match(path)

    assert entity_id_match is not None, f"Could not find id in {path}"
    if entity_id_match:
        return entity_id_match.group(1)


def get_portfolios(l):
    response = l.client.get("/portfolios")
    d = pq(response.text)
    portfolio_links = [
        p.attr("href")
        for p in d(
            ".global-panel-container .atat-table tbody tr td:first-child a"
        ).items()
    ]
    force_new_portfolio = randrange(0, 100) < NEW_PORTFOLIO_CHANCE
    if len(portfolio_links) == 0 or force_new_portfolio:
        portfolio_links += [create_portfolio(l)]

    l.locust.portfolio_links = portfolio_links


def get_portfolio(l):
    portfolio_link = choice(l.locust.portfolio_links)
    response = l.client.get(portfolio_link)
    d = pq(response.text)
    application_links = [
        p.attr("href")
        for p in d(".application-list .accordion__actions a:first-child").items()
    ]
    if len(application_links) > 0:
        portfolio_id = extract_id(portfolio_link)
        update_app_registry(l, portfolio_id, application_links)


def update_app_registry(l, portfolio_id, app_links):
    if not hasattr(l.locust, "app_links"):
        l.locust.app_links = {}
    l.locust.app_links[portfolio_id] = app_links


def get_app(l):
    app_link = pick_app(l)
    force_new_app = randrange(0, 100) < NEW_APPLICATION_CHANCE
    if app_link is not None and not force_new_app:
        l.client.get(app_link)
    else:
        portfolio_id = extract_id(choice(l.locust.portfolio_links))
        update_app_registry(l, portfolio_id, [create_new_app(l, portfolio_id)])


def pick_app(l):
    if hasattr(l.locust, "app_links") and len(l.locust.app_links.items()) > 0:
        return choice(choice(list(l.locust.app_links.values())))


def create_new_app(l, portfolio_id):
    create_app_url = f"/portfolios/{portfolio_id}/applications/new"
    new_app_form = l.client.get(create_app_url)

    create_app_body = {
        "name": f"Load Test Created - {''.join(choices(LETTERS, k=5))}",
        "description": "Description",
        "csrf_token": get_csrf_token(new_app_form),
    }

    create_app_response = l.client.post(
        create_app_url,
        create_app_body,
        headers={"Referer": l.parent.host + create_app_url},
    )
    application_id = extract_id(create_app_response.url)

    create_environments_body = {
        "environment_names-0": "Development",
        "environment_names-1": "Testing",
        "environment_names-2": "Staging",
        "environment_names-3": "Production",
        "csrf_token": get_csrf_token(create_app_response),
    }

    create_environments_url = f"/applications/{application_id}/new/step_2"

    l.client.post(
        create_environments_url + f"?portfolio_id={portfolio_id}",
        create_environments_body,
        headers={"Referer": l.parent.host + create_environments_url},
    )

    return f"/applications/{application_id}/settings"


def create_portfolio(l):
    new_portfolio_form = l.client.get("/portfolios/new")
    new_portfolio_body = {
        "name": f"Load Test Created - {''.join(choices(LETTERS, k=5))}",
        "defense_component": "army",
        "description": "Test",
        "csrf_token": get_csrf_token(new_portfolio_form),
    }

    response = l.client.post(
        "/portfolios",
        new_portfolio_body,
        headers={"Referer": l.parent.host + "/portfolios"},
    )

    return urlparse(response.url).path


class UserBehavior(TaskSequence):
    def on_start(self):
        self.client.verify = not DISABLE_VERIFY
        login(self)

    @seq_task(1)
    def home(l):
        get_index(l)

    @seq_task(2)
    def portfolios(l):
        get_portfolios(l)

    @seq_task(3)
    def pick_a_portfolio(l):
        get_portfolio(l)

    @seq_task(4)
    def pick_an_app(l):
        get_app(l)

    def on_stop(self):
        logout(self)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 3000
    max_wait = 9000


if __name__ == "__main__":
    # if run as the main file, will spin up a single locust
    WebsiteUser().run()

