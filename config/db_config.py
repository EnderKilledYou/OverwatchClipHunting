import os

import sqlalchemy
from flask_sqlalchemy import SQLAlchemy

def config_db() -> SQLAlchemy:
    """

    :rtype: object
    :return: Initializes the sqlite database for storing your credentials.
    """
    from app import app
    config_app_db_settings(app)
    dbx = SQLAlchemy(app)

    return dbx


def config_app_db_settings(app):

    if 'OCR_PRODUCTION' in os.environ:
        config_mysql(app)

    else:
        config_dev_db(app)


def config_dev_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitch.sqlite3'


def config_mysql(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_POOL_SIZE'] = 100
    app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = sqlalchemy.engine.url.URL.create(
        drivername="mysql+pymysql",
        username=os.environ['DB_USER'],
        password=os.environ['DB_SECRET'],
        database=os.environ['DB_NAME'],
        host=os.environ['DB_HOST'],

    )


db = config_db()

from Database import *
from Database.Twitch import *
def init_db():

    db.create_all()


def get_db() -> SQLAlchemy:
    return db
