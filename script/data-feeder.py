"""
Tool set for seed data into the ATAT application
"""
import os
import pendulum
import json
from uuid import uuid4
import time

# main libraries
import typer
import questionary
from progress.spinner import PieSpinner as Spinner
from progress.bar import FillingCirclesBar as Bar

# app modules imports

# module contents and variables
cli_app = typer.Typer()


# Methods and classes

# Commands
@cli_app.command()
def hello(name: str = "you"):
    """
    testing typer hello function
    :param name: the name of the user
    :return: salutation
    """
    print(f'Hello {name}')

@cli_app.command()
def add_new_portfolio(name: str = None,  desc: str = None, comp = None):
    """
    Add A New Portfolio like form on ATAT
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
        comp = questionary.checkbox("Select DoD component(s) funding your Portfolio:",
                                    choices=["Air Force",
                                             "Army",
                                             "Marine Corps",
                                             "Navy",
                                             "Space Force",
                                             "Combatant Command / Joint Staff (CCMD/JS)",
                                             "Defense Agency and Field Activity (DAFA)",
                                             "Office of the Secretary of Defense (OSD) / Principal Staff Assistants (PSAs)",
                                             "Other"]).ask()

    bar = Bar('Processing', max=20)
    for i in range(20):
        time.sleep(.3)
        bar.next()
    bar.finish()

    state = 0
    spinner = Spinner('Loading ')
    while state < 10:
        # Do some work
        time.sleep(.3)
        state = state + 1
        spinner.next()

    print()
    print('Name %s', name)
    print('Desc %s', desc)
    print('Comp', comp)

    pass


# Run CLI Tool app
if __name__ == "__main__":
    cli_app()
