from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def config_db() -> SQLAlchemy:
    """

    :rtype: object
    :return: Initializes the sqlite database for storing your credentials.
    """
    from app import app
    dbx = SQLAlchemy(app)
    dbx.init_app(app)
    dbx.create_all()
    return dbx



db = config_db()
