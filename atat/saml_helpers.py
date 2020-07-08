import random
from urllib.parse import urlparse

from flask import (
    Blueprint,
    request,
    redirect,
    render_template,
    url_for,
    current_app as app,
    session
)
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
import pendulum


def do_login_saml():
    # How can we preserve a "next" parameter for deep links?

    saml_request_config = prepare_flask_request(request)
    saml_auth = init_saml_auth(saml_request_config)

    print("DEV LOGIN REQUEST")
    print(request.args)
    if 'acs' in request.args:

        # unpack response with pysaml lib

        # Can be set before login redirect to ensure parity between outbound auth and inbound
        request_id = None
        if 'AuthNRequestID' in session:
            request_id = session['AuthNRequestID']

        # request_id is optional, but we probably still need to store it outbound above

        saml_auth.process_response(request_id=request_id)
        errors = saml_auth.get_errors()
        if len(errors) == 0:
            if 'AuthNRequestID' in session:
                del session['AuthNRequestID']

            # Assuming these are standard functions, do we inspect fields deeper for other info?
            session['samlUserdata'] = saml_auth.get_attributes()
            session['samlNameId'] = saml_auth.get_nameid()
            session['samlNameIdFormat'] = saml_auth.get_nameid_format()
            session['samlNameIdNameQualifier'] = saml_auth.get_nameid_nq()
            session['samlNameIdSPNameQualifier'] = saml_auth.get_nameid_spnq()
            session['samlSessionIndex'] = saml_auth.get_session_index()

            self_url = OneLogin_Saml2_Utils.get_self_url(saml_request_config)

            # RelayState is set in the IdP config, but can be overidden by passing return_to when login is called
            # if 'RelayState' in request.form and self_url != request.form['RelayState']:
            #     return redirect(saml_auth.redirect_to(request.form['RelayState']))
            return render_template('dev/saml.html')
        else:
            print("Something went wrong SAML")
            print(errors[0])
            print(dir(errors[0]))
    elif request.method == "GET":
        # login takes a return_to param that overrides relay state, useful for deep link?
        return redirect(saml_auth.login())


def init_saml_auth(req):
    auth = OneLogin_Saml2_Auth(req, custom_base_path=app.config['SAML_PATH'])
    return auth


def prepare_flask_request(request):
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    url_data = urlparse(request.url)
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'server_port': url_data.port,
        'script_name': request.path,
        'get_data': request.args.copy(),
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
        'post_data': request.form.copy()
    }
