import tornado

from atst.handler import BaseHandler
from atst.forms.financial import FinancialForm
from atst.domain.requests import Requests
from atst.domain.pe_numbers import PENumbers


class RequestFinancialVerification(BaseHandler):
    def initialize(self, page, db_session):
        self.page = page
        self.requests_repo = Requests(db_session)
        self.pe_numbers_repo = PENumbers(db_session)

    def get_existing_request(self, request_id):
        return self.requests_repo.get(request_id)

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, request_id=None):
        existing_request = self.get_existing_request(request_id)
        form = FinancialForm(data=existing_request.body.get('financial_verification'))
        self.render(
            "requests/financial_verification.html.to",
            page=self.page,
            f=form,
            request_id=request_id,
        )

    @tornado.gen.coroutine
    def update_request(self, request_id, form_data):
        request_data = {
            "creator_id": self.current_user["id"],
            "request": {"financial_verification": form_data},
        }
        return self.requests_repo.update(request_id, request_data)

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self, request_id=None):
        self.check_xsrf_cookie()
        post_data = self.request.arguments
        existing_request = self.get_existing_request(request_id)
        form = FinancialForm(post_data)

        rerender_args = dict(request_id=request_id, f=form)

        if form.validate():
            yield self.update_request(request_id, form.data)
            valid = yield form.perform_extra_validation(
                existing_request.body.get('financial_verification'),
                self.pe_numbers_repo
            )
            if valid:
                self.redirect(
                    self.application.default_router.reverse_url("financial_verification_submitted")
                )
            else:
                self.render(
                    "requests/financial_verification.html.to",
                    **rerender_args
                )
        else:
            self.render(
                "requests/financial_verification.html.to",
                **rerender_args
            )
