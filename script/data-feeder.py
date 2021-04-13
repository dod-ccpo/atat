"""
Tool set for seed data into the ATAT application
"""

# TODO: This operation required to be log but like this is out of atat the standard log would not work.

import os
from typing import Optional, List

import pendulum
import json
from uuid import uuid4
import time

# main libraries
import typer
import questionary
from questionary import Choice
from progress.spinner import PieSpinner as Spinner
from progress.bar import FillingCirclesBar as Bar

# app modules imports
from atat.app import make_config, make_app
from atat.domain import NotFoundError
from atat.domain.users import Users, User
from atat.forms.data import SERVICE_BRANCHES, JEDI_CLIN_TYPES
from atat.domain.portfolios import Portfolios
from atat.utils import pick
from atat.routes.dev import _DEV_USERS

# this module constants and variables
cli_app = typer.Typer()
CHOICE_SERVICE_BRANCHES = []
for branch in SERVICE_BRANCHES:
    CHOICE_SERVICE_BRANCHES.append(Choice(title=branch[1], value=branch[0]))


# Methods and classes


# get a valid user
def get_atat_user(dod_id: str = None, atat_id: str = None, name: str = "amanda"):
    """
    Get a user from ATAT when by, atat_id, dod_id or name from the testing data.
    or return None in case it does not found one.
    :param dod_id: DOD ID of the user you want - must be on ATAT
    :param atat_id: ATAT ID of the user on the DB of the application
    :param name: dev tester users (only available on test mode and the seed_sample set).
    :return: User Object or None
    """
    # TODO: 'name' is for use on the test user only contain on _DEV_USERS so only
    #       available on the development environment
    # TODO: Method to find the user like using dod_id would be more likely for a external source
    #       looking for ATAT id is very unlikely because is only percent on the specific installation
    #       of ATAT and is not portable.

    with web_app.app_context():
        try:
            portfolio_owner = Users.get_or_create_by_dod_id(
                _DEV_USERS[name]["dod_id"],
                **pick(
                    [
                        "permission_sets",
                        "first_name",
                        "last_name",
                        "email",
                        "service_branch",
                        "phone_number",
                        "citizenship",
                        "designation",
                    ],
                    _DEV_USERS[name],
                ),
            )  # Amanda

            return portfolio_owner
        except NotFoundError:
            print(
                "Could not find demo users; will not create demo portfolio {}".format(
                    name
                )
            )
            return None


def create_atat_portfolio(
    owner: User, portfolio_name: str, portfolio_desc: str, branches: List[str]
):
    with web_app.app_context():
        try:
            portfolio = Portfolios.create(
                user=owner,
                portfolio_attrs={
                    "name": portfolio_name,
                    "defense_component": branches,
                    "description": portfolio_desc,
                },
            )
            return portfolio
        except NotFoundError:
            print(
                "Could not find demo users; will not create demo portfolio {}".format(
                    name
                )
            )
            return None


# CLI input methods


def is_good(good: bool = False):
    """
    An indicator of completion with a messages.
    :param good:
    :return:
    """
    if good:
        ending = typer.style("good", fg=typer.colors.GREEN, bold=True)
        typer.echo(ending)
    else:
        ending = typer.style("bad", fg=typer.colors.RED, bold=True)
        typer.echo(ending)


def get_cli_dev_name(name: str = None):
    """
    if the name is not pass then it show the list of dev user to the user to chose one and return the selected one.
    :param name:
    :return:
    """
    if name is None:
        name = questionary.select(
            "Please write the selected", choices=list(_DEV_USERS.keys()),
        ).ask()

    user = get_atat_user(name=name)
    return user


# CLI Commands


@cli_app.command()
def get_user(name: str = None):
    """
    testing typer hello function
    :param name: the name of the user
    :return: salutation
    """
    user = get_cli_dev_name(name=name)
    if user is not None:
        print("user is: ", user.first_name)
        print(user)
    else:
        print("user not found")


@cli_app.command()
def add_portfolio(
    owner_name: str =  None,
    name: str = None,
    desc: str = None,
    comp: Optional[str] = None,
    feed_json: bool = False,
):
    """
    Add A New Portfolio like form on ATAT
    :param feed_json:
    :param name: A name that is descriptive enough for users to identify the Portfolio. You may consider naming based on.
    :param desc: Add a brief one to two sentence description of your portfolio. Consider this your statement of work.
    :param comp: Select the DOD component(s) that will fund all Applications within this Portfolio. Multiple DoD organizations can fund the same Portfolio.
Select all that apply.
    :return: create a portfolio on the DB of ATAT
    """
    # get user owner object
    owner_user = get_cli_dev_name(owner_name)

    if name is None:
        name = questionary.text("Portfolio name?").ask()
    if desc is None:
        desc = questionary.text("Portfolio Description?").ask()
    if comp is None:
        comp = questionary.checkbox(
            "Select DoD component(s) funding your Portfolio:",
            choices=CHOICE_SERVICE_BRANCHES,
        ).ask()

    # testing progress bar
    bar = Bar("Processing", max=20)
    for i in range(20):
        time.sleep(0.3)
        bar.next()
    bar.finish()

    # adding the portfolio
    portfolio = create_atat_portfolio(owner_user, name, desc, comp)

    state = 0
    spinner = Spinner("Loading ")
    while state < 10:
        # Do some work
        time.sleep(0.3)
        state = state + 1
        spinner.next()

    print()
    print("Name %s", name)
    print("Desc %s", desc)
    print("Comp", comp)
    print("owner_user", owner_user)
    print("portfolio", portfolio)

    is_good(True)


# Run CLI Tool app
if __name__ == "__main__":
    config = make_config({"default": {"DEBUG": False}})
    web_app = make_app(config)

    # Cli tool on
    cli_app()