import tornado
from atst.handler import BaseHandler
from atst.forms.request import RequestForm
from atst.forms.org import OrgForm
from atst.forms.poc import POCForm
from atst.forms.review import ReviewForm
from atst.forms.financial import FinancialForm
import tornado.httputil


class RequestNew(BaseHandler):
    screens = [
        {
            "title": "Details of Use",
            "section": "details_of_use",
            "form": RequestForm,
            "subitems": [
                {"title": "Overall request details", "id": "overall-request-details"},
                {"title": "Cloud Resources", "id": "cloud-resources"},
                {"title": "Support Staff", "id": "support-staff"},
            ],
        },
        {
            "title": "Information About You",
            "section": "information_about_you",
            "form": OrgForm,
        },
        {
            "title": "Primary Point of Contact",
            "section": "primary_poc",
            "form": POCForm,
        },
        {"title": "Review & Submit", "section": "review_submit", "form": ReviewForm},
        {
            "title": "Financial Verification",
            "section": "financial_verification",
            "form": FinancialForm,
        },
    ]

    def initialize(self, page, requests_client):
        self.page = page
        self.requests_client = requests_client

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self, screen=1, request_id=None):
        self.check_xsrf_cookie()
        screen = int(screen)
        form_metadata = self.screens[screen - 1]
        form_section = form_metadata["section"]
        form = form_metadata["form"](self.request.arguments)

        if form.validate():
            response = yield self.create_or_update_request(
                form_section, form.data, request_id
            )
            if response.ok:
                where = self.application.default_router.reverse_url(
                    "request_form_update",
                    str(screen + 1),
                    request_id or response.json["id"],
                )
                self.redirect(where)
            else:
                self.set_status(response.code)
        else:
            self.show_form(screen, form)

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, screen=1, request_id=None):
        form = None
        form_data = None
        is_review_section = screen == 4

        if request_id:
            request = yield self.get_request(request_id)
            if request.ok:
                if is_review_section:
                    form_data = request.json["body"]
                else:
                    form_metadata = self.screens[int(screen) - 1]
                    section = form_metadata["section"]
                    form_data = request.json["body"].get(section, request.json["body"])
                    form = form_metadata["form"](data=form_data)

        self.show_form(screen=screen, form=form, request_id=request_id, data=form_data)

    def show_form(self, screen=1, form=None, request_id=None, data=None):
        if not form:
            form = self.screens[int(screen) - 1]["form"](self.request.arguments)
        self.render(
            "requests/screen-%d.html.to" % int(screen),
            f=form,
            data=data,
            page=self.page,
            screens=self.screens,
            current=int(screen),
            next_screen=int(screen) + 1,
            request_id=request_id,
        )

    @tornado.gen.coroutine
    def get_request(self, request_id):
        request = yield self.requests_client.get(
            "/users/{}/requests/{}".format(self.get_current_user()["id"], request_id),
            raise_error=False,
        )
        return request

    @tornado.gen.coroutine
    def create_or_update_request(self, form_section, form_data, request_id=None):
        request_data = {
            "creator_id": self.get_current_user()["id"],
            "request": {form_section: form_data},
        }
        if request_id:
            response = yield self.requests_client.patch(
                "/requests/{}".format(request_id), json=request_data
            )
        else:
            response = yield self.requests_client.post("/requests", json=request_data)
        return response
