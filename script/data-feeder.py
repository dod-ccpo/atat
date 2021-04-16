"""
Tool set for seed data into the ATAT application
"""

# TODO: This operation required to be logs.

import os
import re
from typing import Optional, List

import pendulum
import json
from uuid import uuid4
import time

# main libraries
import typer
import questionary
from questionary import Choice, Validator, ValidationError, prompt
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
def get_atat_dev_user(name: str = "amanda"):
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


def get_atat_user_by_dod_id(dod_id: str = None):
    with web_app.app_context():
        try:
            if dod_id is None:
                return None
            else:
                return Users.get_by_dod_id(dod_id)
        except NotFoundError:
            print(NotFoundError("user"))
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
                    portfolio_name
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


def get_cli_user(dod_id: str = None, name: str = None):
    """
    If the name is not pass then it show the list of dev user to the user to chose one and return the selected one.

    :param dod_id: the DOD Id of the user.
    :param name: the name of the dev user.
    :return:
    """

    # Collecting requirements
    if None in [name, dod_id]:
        get_user_by = questionary.select(
            "Find a user by?",
            choices=[
                Choice(title="DOD ID", value="id"),
                Choice(title="Developer list of users", value="user"),
            ],
        ).ask()
    if get_user_by == "user":
        name = questionary.select(
            "Please write the selected", choices=list(_DEV_USERS.keys()),
        ).ask()
    elif get_user_by == "id":
        dod_id = questionary.text(
            "Please write the DOD_ID of the user?", validate=CliValidatorDodId,
        ).ask()

    # Get User object:
    if name is not None:
        user = get_atat_dev_user(name=name)
    elif dod_id is not None:
        user = get_atat_user_by_dod_id(dod_id)

    return user


def add_cli_portfolio_interactive(
        owner_name: str = None,
        owner_dod_id: str = None,
        name: str = None,
        desc: str = None,
        comp: Optional[str] = None,
):
    # get user owner object
    owner_user = get_cli_user(name=owner_name, dod_id=owner_dod_id)

    if name is None:
        name = questionary.text(
            "Portfolio name?", validate=CliValidatorPortfolioName
        ).ask()
    if desc is None:
        desc = questionary.text("Portfolio Description?").ask()
    if comp is None:
        comp = questionary.checkbox(
            "Select DoD component(s) funding your Portfolio:",
            choices=CHOICE_SERVICE_BRANCHES,
        ).ask()

    # spinner set
    spinner = Spinner("Loading.. ")

    # spinner spin one step
    spinner.next()

    # adding the portfolio
    portfolio = create_atat_portfolio(owner_user, name, desc, comp)

    # spinner spin second step
    spinner.next()

    print()
    print("Name %s", name)
    print("Desc %s", desc)
    print("Comp", comp)

    # Success indicator
    if portfolio is not None:
        is_good(True)
    else:
        is_good(False)


def add_cli_portfolio_json(feed_json: str = None):
    if feed_json is None:
        feed_json = questionary.path(
            "please choice an PDF file?",
            validate=CliValidatorFileJSON
        ).ask()

    if feed_json is not None:
        with open(feed_json) as json_file:
            portfolios_request = json.load(json_file)
            print("portfolios_request", portfolios_request)
            print("portfolios_request len", len(portfolios_request))
            bar = Bar("Processing...", max=len(portfolios_request)+1)
            for index, portfolio in enumerate(portfolios_request, start=1):
                # TODO: replace the print with logs
                bar.next()
                portfolio = None
                print(" Evaluating portfolio number {} ".format(index))
                # happy path values
                dod_id = portfolio["user_owner"]["dod_id"]
                portfolio_name = portfolio["portfolio"]["name"]
                portfolio_desc = portfolio["portfolio"]["desc"]
                portfolio_branch = portfolio["portfolio"]["branch"]

                # required fields validations
                if not is_valid_dod_id(dod_id):
                    print(" Not valid dod_id on portfolio number {} ".format(index))
                    is_good(False)
                    continue
                if not is_valid_portfolio_name(portfolio_name):
                    print(" Not valid Portfolio name on portfolio number {} ".format(index))
                    is_good(False)
                    continue

                # get user owner object
                # owner_user = get_cli_user(dod_id=dod_id)
                # adding the portfolio
                # portfolio = create_atat_portfolio(owner_user, portfolio_name, portfolio_desc, portfolio_branch)
                # Success indicator
                if portfolio is not None:
                    is_good(True)
                else:
                    is_good(False)

            # bar process completed.
            bar.next()
            bar.finish()


# CLI input validations


def is_valid_dod_id(dod_id: str = None):
    if dod_id is None:
        return False
    else:
        return True if re.match("^\d{10}$", dod_id) else False


def is_valid_portfolio_name(portfolio_name: str = None):
    if portfolio_name is None:
        return False
    else:
        return (
            True
            if re.match("^[A-Za-z0-9\-_,'\".\s]{4,100}$$", portfolio_name)
            else False
        )


def is_valid_uri_json_file(file_json: str = None):
    if file_json is None:
        return False
    else:
        return (
            True
            if re.match("^[a-zA-Z\/\-\_]+.json$", file_json)
            else False
        )


def is_valid_component_branches_list(component_branches: list = []):
    if isinstance(component_branches, list):
        if len(component_branches) > 0:
            return True
    return False


class CliValidatorDodId(Validator):
    def validate(self, document):
        if not is_valid_dod_id(document.text):
            raise ValidationError(
                message="Please enter a 10-digit DoD ID number.",
                cursor_position=len(document.text),
            )


class CliValidatorFileJSON(Validator):
    def validate(self, document):
        if not is_valid_uri_json_file(document.text):
            raise ValidationError(
                message="This is not a valid json File.",
                cursor_position=len(document.text),
            )


class CliValidatorPortfolioName(Validator):
    def validate(self, document):
        if not is_valid_portfolio_name(document.text):
            raise ValidationError(
                message="Portfolio names can be between 4-100 characters.",
                cursor_position=len(document.text),
            )


# CLI Commands


@cli_app.command()
def get_user(name: str = None, dod_id: str = None):
    """
    Select one of the test profile users and get the user object.

    :param dod_id: DOD ID of the user

    :param name: the name of the dev user

    :return: User Object print out
    """
    user = get_cli_user(name=name, dod_id=dod_id)
    if user is not None:
        print("user is: ", user.first_name)
        print(user)
    else:
        print("user not found")


@cli_app.command()
def add_portfolio(
        owner_name: str = None,
        owner_dod_id: str = None,
        name: str = None,
        desc: str = None,
        comp: Optional[str] = None,
        feed_json: str = None,
):
    """
    Add A New Portfolio like form on ATAT

    :param owner_dod_id: portfolio owner user dod id.

    :param owner_name: portfolio owner username form the dev list (test mode only).

    :param feed_json: pass a file on json format to add one or more portfolios.

    :param name: A name that is descriptive enough for users to identify the Portfolio. You may consider naming based on.

    :param desc: Add a brief one to two sentence description of your portfolio. Consider this your statement of work.

    :param comp: Select the DOD component(s) that will fund all Applications within this Portfolio. Multiple DoD organizations can fund the same Portfolio.
Select all that apply.

    :return: create a portfolio on the DB of ATAT
    """

    # select type of interaction
    if None in [owner_name, owner_dod_id, feed_json]:
        get_user_by = questionary.select(
            "Add a portfolio by:",
            choices=[
                Choice(title="Interactive console", value="cli"),
                Choice(title="Load a json file", value="json"),
            ],
        ).ask()

    if get_user_by == "json":
        add_cli_portfolio_json(feed_json=feed_json)


    else:
        add_cli_portfolio_interactive(
            owner_name=owner_name,
            owner_dod_id=owner_dod_id,
            name=name,
            desc=desc,
            comp=comp,
        )


# Run CLI Tool app
if __name__ == "__main__":
    config = make_config({"default": {"DEBUG": False}})
    web_app = make_app(config)

    # Cli tool on
    cli_app()
