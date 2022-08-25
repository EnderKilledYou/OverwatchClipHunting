from time import sleep

from sqlalchemy_serializer import SerializerMixin

from Database.monitor import self_id
from config.db_config import db


class Instance(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    is_leader = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DATETIME)


class VoteTable(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.ForeignKey('election.id'))
    year = db.Column(db.Integer)
    day = db.Column(db.Integer)
    month = db.Column(db.Integer)
    hour = db.Column(db.Integer)
    Twenty = db.Column(db.Integer)
    __table_args__ = (
        db.PrimaryKeyConstraint(year, day, month, hour, Twenty) # only allow one election every 20 minutes to avoid race conditions
    )


class Election(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)


def VoteForLeader(vote_id):
    vote = VoteTable(vote_id=vote_id, voter=self_id)
    db.session.add(vote)
    db.session.commit()

    votes = list(VoteTable.query.filter_by(vote_id=vote_id).filter(VoteTable.id < vote.id))
    if len(votes) > 0:
        print("Someone voted before me")
        return None
    sleep(3)
    recount_votes = list(VoteTable.query.filter_by(vote_id=vote_id).filter(VoteTable.id < vote.id))
    if len(recount_votes) == 0:
        return vote  # leader


def CheckForLeader():
    pass


def CheckForLeaderVote():
    pass


def StartLeaderVote():
    pass


def CheckOnLeader():
    pass


def GetRunningInstances():
    pass


def AssignMonitors():
    pass
