from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import os
from flask_googlecharts import GoogleCharts

#setting a bunch of environment variables that flask requires
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)
charts = GoogleCharts(app)

from app import routes, models, errors

db.create_all() #if any tables should exist but dont, they are created here, useful in the first time running the program in a new system

if not app.debug: #allows the debug mode to not log errors, including sending emails
    if app.config['MAIL_SERVER']:#sets up the mail server - completely unfinished and unfunctional
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='tt_elo Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    if not os.path.exists('logs'):#ensures folder exists for logs
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/tt_elo.log', maxBytes=10240,
                                       backupCount=10)#sets size and location for logs
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('tt_elo startup")#command line output shows that program has started