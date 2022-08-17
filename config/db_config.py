from flask_sqlalchemy import SQLAlchemy




def config_db() -> SQLAlchemy:
    """

    :rtype: object
    :return: Initializes the sqlite database for storing your credentials.
    """
    from app import app

    dbx = SQLAlchemy(app)
    return dbx


db = config_db()


def init_db():

    db.drop_all( )
    db.create_all()


def get_db() -> SQLAlchemy:
    return db
