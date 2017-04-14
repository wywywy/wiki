import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = True
    SECRET_KEY = '_c\n(2\x9d\x00\x8d\x9d\xcc(\x1b\x90\x96\xf9\x03\xe9XJ\x06s;\xf9['
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = '1418734887@qq.com'
    MAIL_PASSWORD = 'vbcsjlidypawiiii'
    MAIL_DEFAULT_SENDER = 'wangyu<1418734887@qq.com>'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flaskr]'
    FlASKR_ADMIN = '1418734887@qq.com'


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.db')

    BROKER_URL = 'amqp://wangyu:Wy123456@localhost:5672//'
    CELERY_RESULT_BACKEND = 'amqp://wangyu:Wy123456@localhost:5672//'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Europe/Oslo'
    CELERY_ENABLE_UTC = True


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.db')
    DEBUG = False


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.db')
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'produce': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}



