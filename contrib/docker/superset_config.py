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
    BROKER_URL = 'redis://:%s@%s:%s/0' % (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT) \
        if REDIS_PASSWORD is not None else 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
    CELERY_IMPORTS = ('superset.sql_lab', )
    CELERY_RESULT_BACKEND = 'redis://%s:%s/1' % (REDIS_HOST, REDIS_PORT)
    CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}
    CELERY_TASK_PROTOCOL = 1


CELERY_CONFIG = CeleryConfig



## 自定义配置信息
OAUTH_BASE_URL = get_env_variable('OAUTH_BASE_URL')
OAUTH_TOKEN_URL = get_env_variable('OAUTH_TOKEN_URL')
OAUTH_AUTHORIZE_URL = get_env_variable('OAUTH_AUTHORIZE_URL')
OAUTH_KEY = get_env_variable('OAUTH_KEY')
OAUTH_SECRET = get_env_variable('OAUTH_SECRET')
OAUTH2_CLIENT_TYPE = get_env_variable('OAUTH_CLIENT_TYPE')


from superset.security import SupersetSecurityManager
import logging

class CustomSsoSecurityManager(SupersetSecurityManager):
    # authdbview = CustomAuthDBView

    def oauth_user_info(self, provider, response=None):
        logging.debug("Oauth2 provider: {0}.".format(provider))
        if OAUTH2_CLIENT_TYPE == 'keycloakOauth2' or OAUTH2_CLIENT_TYPE is None :
            me = self.appbuilder.sm.oauth_remotes[provider].get('userinfo').data
            logging.debug("user_data: {0}".format(me))
            profile = {'name': me['name'], 'email': me.get('mail', ''), 'id': '', 'username': me['preferred_username'], 'first_name': me['given_name'], 'last_name': ''}
            logging.debug("profile: {0}".format(profile))
            return profile
        elif OAUTH2_CLIENT_TYPE == 'casOauth2':
            me = self.appbuilder.sm.oauth_remotes[provider].get('profile').data
            logging.debug("user_data: {0}".format(me))
            return {'name': me['attributes']['cn'], 'email': me['attributes'].get('mail', ''), 'id': me['id'],
                    'username': me['attributes']['uid'], 'first_name': me['attributes']['sn'], 'last_name': ''}


CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager

# OAuth2 禁用 https检查
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask_appbuilder.security.manager import AUTH_OAUTH
AUTH_TYPE = AUTH_OAUTH
OAUTH_PROVIDERS = [
    {
        'name': 'oauth2_client',
        'token_key': 'access_token',
        'icon': 'fa-openid', # 用的是 https://fontawesome.com/v4.7.0/icons/
        'remote_app': {
            'consumer_key': OAUTH_KEY,
            'consumer_secret': OAUTH_SECRET,
            'request_token_params': {},
            'access_token_method': 'POST',
            'base_url': OAUTH_BASE_URL,
            'access_token_url': OAUTH_TOKEN_URL,
            'authorize_url': OAUTH_AUTHORIZE_URL
        }
    }
]

# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Public"

HTTP_HEADERS = {}
# If you need to allow iframes from other domains (and are
# aware of the risks), you can disable this header:
# HTTP_HEADERS = {}

PUBLIC_ROLE_LIKE_GAMMA=True

# https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-SESSION_COOKIE_SAMESITE
SESSION_COOKIE_SAMESITE = None  # One of [None, 'Lax', 'Strict']

BABEL_DEFAULT_LOCALE = "zh"