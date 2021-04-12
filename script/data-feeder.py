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
def bay(name: str = None):
    """
    testing typer and questionary bay function
    :param name: the name of the user
    :return: farewell
    """
    if name is None:
        name = questionary.text("Please give me your name?").ask()
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
    print(f'Good bay {name}')


# Run CLI Tool app
if __name__ == "__main__":
    cli_app()
