import tornado
from atst.handler import BaseHandler
from atst.forms.request import RequestForm
from atst.forms.organization_info import OrganizationInfoForm
from atst.forms.funding import FundingForm
from atst.forms.readiness import ReadinessForm
from atst.forms.review import ReviewForm
import tornado.httputil


class RequestNew(BaseHandler):
    screens = [
            {
                'title' : 'Details of Use',
                'section_id': 'details_of_use',
                'form'  : RequestForm,
                'subitems' : [
                {'title' : 'Application Details',
                 'id' : 'application-details'},
                {'title' : 'Computation',
                  'id' : 'computation' },
                {'title' : 'Storage',
                  'id' : 'storage' },
                {'title' : 'Usage',
                  'id' : 'usage' },
            ]},
            {
                'title' : 'Organizational Info',
                'section_id': 'organizational_info',
                'form'  : OrganizationInfoForm,
            },
            {
                'title' : 'Funding/Contracting',
                'section_id': 'funding_contracting',
                'form'  : FundingForm,
            },
            {
                'title' : 'Readiness Survey',
                'section_id': 'readiness_survey',
                'form'  : ReadinessForm,
            },
            {
                'title' : 'Review & Submit',
                'section_id': 'review_and_submit',
                'form'  : ReviewForm,
            }
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
        form = form_metadata['form'](self.request.arguments)
        if form.validate():
            request_data = {form_metadata['section_id']: form.data}
            response = yield self.create_or_update_request(
                request_data, request_id)
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
        if request_id:
            request = yield self.get_request(request_id)
            if request.ok:
                form_metadata = self.screens[int(screen) - 1]
                form_data = request.json['body'].get(form_metadata['section_id'], {})
                form = form_metadata['form'](data=form_data)

        self.show_form(screen=screen, form=form, request_id=request_id)

    def show_form(self, screen=1, form=None, request_id=None):
        if not form:
            form = self.screens[int(screen) - 1]["form"](self.request.arguments)
        self.render(
            "requests/screen-%d.html.to" % int(screen),
            f=form,
            page=self.page,
            screens=self.screens,
            current=int(screen),
            next_screen=int(screen) + 1,
            request_id=request_id,
        )

    @tornado.gen.coroutine
    def get_request(self, request_id):
        request = yield self.requests_client.get(
            "/users/{}/requests/{}".format(self.get_current_user(), request_id),
            raise_error=False,
        )
        return request

    @tornado.gen.coroutine
    def create_or_update_request(self, form_data, request_id=None):
        request_data = {
            "creator_id": self.get_current_user()["id"],
            "request": form_data,
        }
        if request_id:
            response = yield self.requests_client.patch(
                "/requests/{}".format(request_id), json=request_data
            )
        else:
            response = yield self.requests_client.post("/requests", json=request_data)
        return response
