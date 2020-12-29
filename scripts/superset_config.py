# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import os


def get_env_variable(var_name, default=None):
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        else:
            error_msg = 'The environment variable {} was missing, abort...'\
                        .format(var_name)
            raise EnvironmentError(error_msg)


POSTGRES_USER = get_env_variable('POSTGRES_USER')
POSTGRES_PASSWORD = get_env_variable('POSTGRES_PASSWORD')
POSTGRES_HOST = get_env_variable('POSTGRES_HOST')
POSTGRES_PORT = get_env_variable('POSTGRES_PORT')
POSTGRES_DB = get_env_variable('POSTGRES_DB')

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = 'postgresql://%s:%s@%s:%s/%s' % (POSTGRES_USER,
                                                           POSTGRES_PASSWORD,
                                                           POSTGRES_HOST,
                                                           POSTGRES_PORT,
                                                           POSTGRES_DB)

REDIS_HOST = get_env_variable('REDIS_HOST')
REDIS_PORT = get_env_variable('REDIS_PORT')
REDIS_PASSWORD = get_env_variable('REDIS_PASSWORD')


class CeleryConfig(object):
    BROKER_URL = 'redis://:%s@%s:%s/0' % (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT)
    CELERY_IMPORTS = ('superset.sql_lab', )
    CELERY_RESULT_BACKEND = 'redis://%s:%s/1' % (REDIS_HOST, REDIS_PORT)
    CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}
    CELERY_TASK_PROTOCOL = 1


CELERY_CONFIG = CeleryConfig


import os
from superset.security import SupersetSecurityManager
from superset.app import SUPERSET_URL_PREFIX

import logging

from flask_appbuilder.security.views import redirect, expose, AuthOAuthView, logout_user
from flask import session, url_for


class CustomAuthOAuthView(AuthOAuthView):

    route_base = SUPERSET_URL_PREFIX

    @expose("/login/")
    @expose("/login/<provider>")
    @expose("/login/<provider>/<register>")
    def login(self, provider=None, register=None):
        if provider is None:
            if len(self.appbuilder.sm.oauth_providers) == 1:
                provider_name = self.appbuilder.sm.oauth_providers[0]['name']
                logging.debug("there is one provider, can login direct to {0}"
                              .format(provider_name))
                return redirect(SUPERSET_URL_PREFIX + "/login/" + provider_name)
        return super(CustomAuthOAuthView, self).login(provider, register)

    @expose("/logout/")
    def logout(self):
        api_base_url = None
        oauth_provider_name = session.get("oauth_provider")
        oauth_providers = self.appbuilder.sm.oauth_providers
        for oauth_provider in oauth_providers:
            if oauth_provider['name'] == oauth_provider_name:
                api_base_url = oauth_provider['remote_app']['api_base_url']

        if api_base_url is not None:
            if api_base_url.endswith("/"):
                api_base_url = api_base_url[:-1]
            logging.debug("log out with {0} and url {1}/logout"
                          .format(oauth_provider_name, api_base_url))
            default_url = url_for("%s.%s" % (self.appbuilder.indexview.endpoint,
                                             self.appbuilder.indexview.default_view),
                                  _external=True)
            logout_user()
            return redirect(api_base_url + "/logout?redirect_uri=" + default_url)

        return super(CustomAuthOAuthView, self).logout()


class CustomSsoSecurityManager(SupersetSecurityManager):
    authoauthview = CustomAuthOAuthView

    def oauth_user_info(self, provider, response=None):
        me = self.appbuilder.sm.oauth_remotes[provider].get('userinfo').json()
        logging.debug("user_data: {0}".format(me))
        profile = {'name': me['name'], 'email': me.get('mail', "%s@%s" % (
            me['preferred_username'], "superset.com")), 'id': '',
                   'username': me['preferred_username'], 'first_name': me['given_name'],
                   'last_name': ''}
        logging.debug("profile: {0}".format(profile))
        return profile


CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask_appbuilder.security.manager import AUTH_OAUTH

AUTH_TYPE = AUTH_OAUTH

OAUTH_BASE_URL = get_env_variable('OAUTH_BASE_URL')
OAUTH_TOKEN_URL = get_env_variable('OAUTH_TOKEN_URL')
OAUTH_AUTHORIZE_URL = get_env_variable('OAUTH_AUTHORIZE_URL')
OAUTH_KEY = get_env_variable('OAUTH_KEY')
OAUTH_SECRET = get_env_variable('OAUTH_SECRET')

# https://flask-appbuilder.readthedocs.io/en/latest/security.html#authentication-oauth
OAUTH_PROVIDERS = [
    {
        'name': 'oauth2_client',
        'token_key': 'access_token',
        'icon': 'fa-openid',
        'remote_app': {
            'client_id': OAUTH_KEY,
            'client_secret': OAUTH_SECRET,
            'access_token_params': {
                'client_id': OAUTH_KEY
            },
            'access_token_method': 'POST',
            'api_base_url': OAUTH_BASE_URL,
            'request_token_url': None,
            'access_token_url': OAUTH_TOKEN_URL,
            'authorize_url': OAUTH_AUTHORIZE_URL
        }
    }
]

# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Alpha"

HTTP_HEADERS = {}
# If you need to allow iframes from other domains (and are
# aware of the risks), you can disable this header:
# HTTP_HEADERS = {}

PUBLIC_ROLE_LIKE_GAMMA=True

# https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-SESSION_COOKIE_SAMESITE
SESSION_COOKIE_SAMESITE = None  # One of [None, 'Lax', 'Strict']

BABEL_DEFAULT_LOCALE = "zh"


# class PrefixMiddleware:
#
#     def __init__(self, app, prefix='/superset'):
#         self.app = app
#         self.prefix = prefix
#
#     def __call__(self, environ, start_response):
#
#         if environ['PATH_INFO'].startswith(self.prefix):
#             environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
#             environ['SCRIPT_NAME'] = self.prefix
#             return self.app(environ, start_response)
#         else:
#             start_response('404', [('Content-Type', 'text/plain')])
#             return ["This url does not belong to the app.".encode()]
#
# ADDITIONAL_MIDDLEWARE = [PrefixMiddleware]
