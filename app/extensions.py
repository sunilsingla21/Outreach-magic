from flask_login import LoginManager
from flask_minify import Minify
from flask_session import Session
from google.cloud.storage import Client
from google_auth_oauthlib.flow import Flow
from msal import ConfidentialClientApplication

from app.mongo import Mongo
from app.utils.secret_manager import SecretManager

login_manager = LoginManager()
login_manager.login_message_category = 'info'


SCOPES = [
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid',
]

secret_manager = SecretManager()

client_secrets_file = 'client_secret.json'

try:
    google_flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=SCOPES,
        redirect_uri=secret_manager.get('GOOGLE_REDIRECT_URI'),
    )
except Exception as e:
    print(type(e), e)
    import json
    credentials_str = secret_manager.get('OAUTH_CREDENTIALS')
    client_config = json.loads(credentials_str)
    google_flow = Flow.from_client_config(
        client_config=client_config,
        scopes=SCOPES,
        redirect_uri=secret_manager.get('GOOGLE_REDIRECT_URI'),
    )

try:
    storage_client = Client.from_service_account_json(
        secret_manager.get('OM_APP_CREDENTIALS'))
except Exception as e:
    print(type(e), e)
    storage_client = Client()

microsoft_flow = ConfidentialClientApplication(
    client_id=secret_manager.get('MS_CLIENT_ID'),
    client_credential=secret_manager.get('MS_CLIENT_SECRET'),
    authority=secret_manager.get('MS_AUTHORITY')
)

mongo = Mongo()

minify = Minify()

session = Session()
