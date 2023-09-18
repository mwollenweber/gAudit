#!/usr/bin/python
'''
Copyright Matthew Wollenweber 2014
Google Audit Service

'''

import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'mysql://gaudit:introvert42@localhost:3306/gAudit'
domain = "insomniac.technology"
mydomain = "insomniac.technology"
admin = "service_account"

# MDL
MDL_URL = 'http://www.malwaredomainlist.com/mdlcsv.php'

DEBUG = True


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://gaudit:introvert42@localhost:3306/gaudit'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    WTF_CSRF_ENABLED = False


class HerokuConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('JAWSDB_URL')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler

        credentials = None
        secure = None
        # if getattr(cls, 'MAIL_USERNAME', None) is not None:
        # credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
        # if getattr(cls, 'MAIL_USE_TLS', None):
        # secure = ()
        # mail_handler = SMTPHandler(
        # mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
        # fromaddr=cls.FLASKY_MAIL_SENDER,
        # toaddrs=[cls.FLASKY_ADMIN],
        # subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
        # credentials=credentials,
        # secure=secure)
        # mail_handler.setLevel(logging.ERROR)
        # app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'default': DevelopmentConfig
}
