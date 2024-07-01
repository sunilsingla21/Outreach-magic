import os

from app.extensions import secret_manager

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = secret_manager.get('SECRET_KEY')
    MONGO_URI = secret_manager.get('MONGO_URI')

    GOOGLE_CLIENT_ID = secret_manager.get('GOOGLE_CLIENT_ID')

    MS_SCOPE = [
        'email',
        'https://outlook.office.com/IMAP.AccessAsUser.All',
        'https://outlook.office.com/SMTP.Send',
    ]
    MS_REDIRECT_URI = secret_manager.get('MS_REDIRECT_URI')

    SESSION_TYPE = 'mongodb'
    SESSION_MONGODB_DB = 'v4'
    SESSION_MONGODB_COLLECT = 'webAppSessions'

    VALID_SERVERS = ['google', 'microsoft', 'yahoo']
