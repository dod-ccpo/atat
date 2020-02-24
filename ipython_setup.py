from atat.app import make_config, make_app
from atat.database import db
from atat.models import *

app = make_app(make_config())
ctx = app.app_context()
ctx.push()

print(
    "\nWelcome to atat. This shell has all models in scope, and a SQLAlchemy session called db."
)
