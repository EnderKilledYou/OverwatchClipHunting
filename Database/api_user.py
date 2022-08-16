from typing import List

from oauthlib.common import generate_token
from sqlalchemy_serializer import SerializerMixin

from Clipper.get_unix_time import get_unix_time
from config.db_config import db

class SubClipPreferences(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = ('id', 'name')
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    before_amount= db.Column(db.String)


class ZombieUser(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = ('id', 'name', 'token =', 'last_check_in_unix_time', 'is_active')
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    token = db.Column(db.String)
    last_check_in_unix_time = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)


class ZombieTask(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    zombie_id = db.Column(db.Integer)
    task = db.Column(db.String)
    state = db.Column(db.Integer)
    last_check_in_unix_time = db.Column(db.Integer)
    is_complete = db.Column(db.Boolean)
    is_started = db.Column(db.Boolean)
    error_message = db.Column(db.String)
    percent_done = db.Column(db.Float)
    did_error = db.Column(db.Boolean)


def add_zombie_task(zombie_id: int, task: str):
    zombie_task = ZombieUser(zombie_id=zombie_id, task=task, state=0, last_check_in_unix_time=get_unix_time(),
                             is_complete=False, percent_done=0, error_message="")
    db.session.add(zombie_task)
    db.session.commit()
    db.session.flush()
    return zombie_task


def update_zombie_task_last_check_in(zombie_task_id: int):
    zombie_task = get_zombie_task_by_id(zombie_task_id)
    if not zombie_task:
        return None
    zombie_task.last_check_in_unix_time = get_unix_time()
    db.session.commit()
    db.session.flush()
    return zombie_task


def update_zombie_last_check_in(zombie_id: int):
    zombie = ZombieUser.query.filter_by(id=zombie_id).first()
    if not zombie:
        return None
    zombie.last_check_in_unix_time = get_unix_time()
    db.session.commit()
    db.session.flush()
    return zombie


def update_zombie_task_state(zombie_task_id: int, state: int):
    zombie_task = get_zombie_task_by_id(zombie_task_id)
    if zombie_task is None:
        return None
    zombie_task.state = state
    db.session.commit()
    db.session.flush()
    return zombie_task


def update_zombie_task_complete(zombie_task_id: int):
    zombie_task = get_zombie_task_by_id(zombie_task_id)
    if zombie_task is None:
        return None
    zombie_task.is_complete = True
    db.session.commit()
    db.session.flush()
    return zombie_task


def update_zombie_task_error(zombie_task_id: int, error_message: str):
    zombie_task = get_zombie_task_by_id(zombie_task_id)
    if zombie_task is None:
        return None
    zombie_task.is_complete = True
    zombie_task.error_message = error_message
    zombie_task.did_error = True
    db.session.commit()
    db.session.flush()
    return zombie_task


def update_zombie_task_percent(zombie_task_id: int, percent: float):
    zombie_task = get_zombie_task_by_id(zombie_task_id)
    if zombie_task is None:
        return None
    zombie_task.percent = percent
    db.session.commit()
    db.session.flush()
    return zombie_task


def get_zombie_unstarted_tasks(zombie_id: int) -> List[ZombieTask]:
    return list(ZombieTask.query.filter_by(id=zombie_id, is_started=False))


def get_zombie_tasks(zombie_id: int) -> List[ZombieTask]:
    return list(ZombieTask.query.filter_by(id=zombie_id))

def get_zombies() -> List[ZombieUser]:
    return list(ZombieUser.query.filter_by())
def get_zombie_task_by_id(zombie_id: int) -> ZombieTask:
    return ZombieTask.query.filter_by(id=zombie_id).first()


def get_zombie_by_id(zombie_id: int) -> ZombieTask:
    return ZombieUser.query.filter_by(id=zombie_id).first()


def get_zombie_by_token(token: str) -> ZombieTask:
    strip_token = token.strip()
    if len(strip_token) < 10:
        return None
    return ZombieUser.query.filter_by(token=strip_token).first()


def add_zombie(name: str):
    zombie = ZombieUser(name=str, last_check_in_unix_time=get_unix_time(), is_active=True, token=generate_token())
    db.session.add(zombie)
    db.session.commit()
    db.session.flush()
    return zombie


def reset_token(zombie_id: int):
    zombie = ZombieUser.query.filter_by(id=zombie_id).first()
    if not zombie:
        return None
    zombie.token = generate_token()
    db.session.commit()
    db.session.flush()
    return zombie


def delete_zombie(zombie_id: int):
    zombie = ZombieUser.query.filter_by(id=zombie_id).first()
    if not zombie:
        return None
    db.session.delete(zombie)
    db.session.commit(zombie)
    db.session.flush()


def delete_zombie_task(zombie_task_id: int):
    zombie_task = get_zombie_task_by_id(zombie_task_id)
    if zombie_task is not None:
        db.session.delete(zombie_task)
        db.session.commit()
        db.session.flush()


def delete_zombie_tasks(zombie_id: int):
    for zombie_task in get_zombie_tasks(zombie_id):
        db.session.delete(zombie_task)
    db.session.commit()
    db.session.flush()
