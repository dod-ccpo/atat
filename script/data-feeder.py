"""
Tool set for seed data into the ATAT application
"""

# TODO: This operation required to be log but like this is out of atat the standard log would not work.

import os
from typing import Optional

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
from atat.domain import NotFoundError
from atat.domain.users import Users
from atat.forms.data import SERVICE_BRANCHES, JEDI_CLIN_TYPES
from atat.utils import pick
from atat.routes.dev import _DEV_USERS

# this module constants and variables
cli_app = typer.Typer()
CHOICE_SERVICE_BRANCHES = []
for branch in SERVICE_BRANCHES:
    print(branch[1])
    CHOICE_SERVICE_BRANCHES.append(Choice(title=branch[1], value=branch[0]))


# Methods and classes


# get a valid user
def get_a_user(dod_id: str = None, atat_id: str = None, name: str = "amanda"):
    """
    Get a user from ATAT when by, atat_id, dod_id or name from the testing data.
    or return None in case it does not found one.
    :param dod_id:
    :param atat_id:
    :param name:
    :return: User Object or None
    """

    # TODO: 'name' is for use on the test user only contain on _DEV_USERS so only
    #       available on the development environment
    # TODO: Method to find the user like using dod_id would be more likely for a external source
    #       looking for ATAT id is very unlikely because is only percent on the specific installation
    #       of ATAT and is not portable.
    try:
        portfolio_owner = Users.get_or_create_by_dod_id(
            "2345678901",
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
            "Could not find demo users; will not create demo portfolio {}".format(name)
        )
        return None


# Commands
@cli_app.command()
def hello(name: str = "you"):
    """
    testing typer hello function
    :param name: the name of the user
    :return: salutation
    """
    print(f"Hello {name}")


@cli_app.command()
def add_new_portfolio(name: str = None, desc: str = None, comp: Optional[str] = None, feed_json: bool = False):
    """
    Add A New Portfolio like form on ATAT
    :param feed_json:
    :param name: A name that is descriptive enough for users to identify the Portfolio. You may consider naming based on.
    :param desc: Add a brief one to two sentence description of your portfolio. Consider this your statement of work.
    :param comp: Select the DOD component(s) that will fund all Applications within this Portfolio. Multiple DoD organizations can fund the same Portfolio.
Select all that apply.
    :return: create a portfolio on the DB of ATAT
    """

    if name is None:
        name = questionary.text("Portfolio name?").ask()
    if desc is None:
        desc = questionary.text("Portfolio Description?").ask()
    if comp is None:
        comp = questionary.checkbox(
            "Select DoD component(s) funding your Portfolio:",
            # choices=SERVICE_BRANCHES,
            choices=CHOICE_SERVICE_BRANCHES,
        ).ask()

    bar = Bar("Processing", max=20)
    for i in range(20):
        time.sleep(0.3)
        bar.next()
    bar.finish()

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

    ending = typer.style("good", fg=typer.colors.GREEN, bold=True)
    typer.echo(ending)
    pass


# Run CLI Tool app
if __name__ == "__main__":
    cli_app()
