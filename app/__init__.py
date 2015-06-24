# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask.ext.login import LoginManager, UserMixin
from config import basedir
from momentjs import momentjs
from flask.ext.babel import Babel

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# l10n
babel = Babel(app)

# Настройка авторизации
lm = LoginManager()
lm.init_app(app)

from app import views,models

if not app.debug:
	import logging
	from logging.handlers import RotatingFileHandler
	file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
	file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
	app.logger.setLevel(logging.INFO)
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)
	app.logger.info('microblog startup')

app.jinja_env.globals['momentjs'] = momentjs
