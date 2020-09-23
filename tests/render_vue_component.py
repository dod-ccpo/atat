import pytest
from bs4 import BeautifulSoup
from flask import Markup
from flask import current_app as app
from wtforms import Form, FormField
from wtforms.fields import StringField
from wtforms.validators import InputRequired
from wtforms.widgets import CheckboxInput, ListWidget

from atat.forms.task_order import CLINForm, TaskOrderForm
from atat.models import Permissions
from atat.routes.task_orders.new import render_task_orders_edit
from atat.utils.context_processors import user_can_view
from tests import factories


class InitialValueForm(Form):
    datafield = StringField(label="initialvalue value", default="initialvalue")

    errorfield = StringField(
        label="error", validators=[InputRequired(message="Test Error Message")]
    )


class TaskOrderPdfForm(Form):
    filename = StringField(default="filename")
    object_name = StringField(default="objectName")

    errorfield = StringField(
        label="error", validators=[InputRequired(message="Test Error Message")]
    )


class TaskOrderForm(Form):
    pdf = FormField(TaskOrderPdfForm, label="task_order_pdf")
    number = StringField(label="task_order_number", default="number")


@pytest.fixture
def env(app, scope="function"):
    return app.jinja_env


@pytest.fixture
def upload_input_macro(env):
    # override tojson as identity function to prevent
    # wrapping strings in extra quotes
    env.filters["tojson"] = lambda x: x
    upload_template = env.get_template("components/upload_input.html")
    return getattr(upload_template.module, "UploadInput")


@pytest.fixture
def checkbox_input_macro(env):
    checkbox_template = env.get_template("components/checkbox_input.html")
    return getattr(checkbox_template.module, "CheckboxInput")


@pytest.fixture
def multi_checkbox_input_macro(env):
    multi_checkbox_template = env.get_template("components/multi_checkbox_input.html")
    return getattr(multi_checkbox_template.module, "MultiCheckboxInput")


@pytest.fixture
def text_input_macro(env):
    text_input_template = env.get_template("components/text_input.html")
    return getattr(text_input_template.module, "TextInput")


@pytest.fixture
def initial_value_form(scope="function"):
    return InitialValueForm()


@pytest.fixture
def task_order_form(scope="function"):
    return TaskOrderForm()


@pytest.fixture
def error_task_order_form(scope="function"):
    return ErrorTaskOrderForm()


def write_template(content, name):
    with open("js/test_templates/{}".format(name), "w") as fh:
        fh.write(content)


def test_make_checkbox_input_template(checkbox_input_macro, initial_value_form):
    initial_value_form.datafield.widget = CheckboxInput()
    rendered_checkbox_macro = checkbox_input_macro(initial_value_form.datafield)
    write_template(rendered_checkbox_macro, "checkbox_input_template.html")


def test_make_multi_checkbox_input_template(
    multi_checkbox_input_macro, initial_value_form
):
    initial_value_form.datafield.widget = ListWidget()
    initial_value_form.datafield.option_widget = CheckboxInput()
    initial_value_form.datafield.choices = [("a", "A"), ("b", "B")]
    rendered_multi_checkbox_input_macro = multi_checkbox_input_macro(
        initial_value_form.datafield, optional=Markup("'optional'")
    )
    write_template(
        rendered_multi_checkbox_input_macro, "multi_checkbox_input_template.html"
    )


def test_make_upload_input_template(upload_input_macro, task_order_form):
    rendered_upload_macro = upload_input_macro(
        task_order_form.pdf, file_size_limit=int(app.config.get("FILE_SIZE_LIMIT")),
    )
    write_template(rendered_upload_macro, "upload_input_template.html")


def test_make_upload_input_error_template(upload_input_macro, task_order_form):
    task_order_form.validate()
    rendered_upload_macro = upload_input_macro(
        task_order_form.pdf, file_size_limit=int(app.config.get("FILE_SIZE_LIMIT")),
    )
    write_template(rendered_upload_macro, "upload_input_error_template.html")


def test_make_task_order_with_clin_form_template(app, request_ctx):
    request_ctx.g.current_user = factories.UserFactory.create()
    request_ctx.g.application = None
    request_ctx.g.portfolio = None
    # hard-code the portfolio ID so it does not change the fragment every time
    # this is run
    portfolio = factories.PortfolioFactory.create(
        id="e4edf994-04f4-4aaa-ba30-39507e1068a8"
    )
    # hard-code the TO number for the same reason
    task_order = factories.TaskOrderFactory.create(
        portfolio=portfolio, number="1234567890123"
    )
    task_order_form = TaskOrderForm(obj=task_order)
    step3 = render_task_orders_edit(
        "task_orders/step_3.html",
        form=task_order_form,
        portfolio_id=task_order.portfolio_id,
        extra_args={
            "portfolio": task_order.portfolio,
            "permissions": Permissions,
            "user_can": user_can_view,
            "task_order": task_order,
            "contract_start": app.config.get("CONTRACT_START_DATE"),
            "contract_end": app.config.get("CONTRACT_END_DATE"),
        },
    )
    dom = BeautifulSoup(step3, "html.parser")
    to_form = dom.find("to-form")
    write_template(str(to_form), "to_form.html")


def test_make_clin_fields(env, app):
    step3_template = env.get_template("components/clin_fields.html")
    clin_fields_macro = getattr(step3_template.module, "CLINFields")
    clin_fields = clin_fields_macro(
        app.config.get("CONTRACT_START_DATE"),
        app.config.get("CONTRACT_END_DATE"),
        CLINForm(),
        0,
    )
    write_template(clin_fields, "clin_fields.html")


def test_make_pop_date_range(env, app):
    pop_date_range_template = env.get_template("components/pop_date_range.html")
    pop_date_range_macro = getattr(pop_date_range_template.module, "PopDateRange")
    form = CLINForm()
    pop_date_range = pop_date_range_macro(
        start_field=form.start_date,
        end_field=form.end_date,
        mindate=app.config.get("CONTRACT_START_DATE"),
        maxdate=app.config.get("CONTRACT_END_DATE"),
        index=1,
    )
    write_template(pop_date_range, "pop_date_range.html")


def test_make_text_input_template(text_input_macro, task_order_form):
    text_input_to_number = text_input_macro(
        task_order_form.number, validation="taskOrderNumber"
    )
    write_template(text_input_to_number, "text_input_to_number.html")
