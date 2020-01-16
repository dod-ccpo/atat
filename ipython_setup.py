from atst.app import make_config, make_app
from atst.database import db
from atst.models import *

app = make_app(make_config())
ctx = app.app_context()
ctx.push()

print(
    "\nWelcome to atst. This shell has all models in scope, and a SQLAlchemy session called db."
)
