import datetime

from Database.Twitch.list_dicts import list_dicts
from Database.monitor import Monitor
from config.db_config import db


def unclaim_monitor(stream_name) -> Monitor:
    with db.session.begin():
        monitor = Monitor.query.filter_by(broadcaster=stream_name).first()
        if monitor is None:
            return
        monitor.activated_by = ""
        monitor.activated_at = datetime.datetime(1999, 12, 11, 0, 0)
        monitor.is_active = False


def unclaim_table_Type(table_type, id):
    with db.session.begin():
        claimed_record = table_type.query.filter_by(id=id).first()
        if claimed_record is None:
            return
        claimed_record.activated_by = ""
        claimed_record.activated_at = datetime.datetime(1999, 12, 11, 0, 0)
        claimed_record.is_active = False


def claim_table_type(table_type, id, my_claim_id) -> bool:
    with db.session.begin():
        current_time = datetime.datetime.now()
        claimed_record = table_type.query.filter_by(id=id).first()
        if claimed_record is None:
            print(f"Could not claim {id} when looking at streamers")
            return False
        if claimed_record.activated_by == my_claim_id:
            return False
        time_delta = current_time - datetime.datetime(1999, 12, 11, 0, 0)
        if claimed_record.activated_at is not None:
            time_delta = current_time - claimed_record.activated_at
        last_claim_expy = time_delta.seconds > 60 * 3
        if last_claim_expy or not claimed_record.is_active:
            query = Monitor.query.filter_by(
                activated_by=claimed_record.activated_by, id=id)
            update_values = {
                Monitor.activated_by: my_claim_id,
                Monitor.activated_at: current_time,
                Monitor.is_active: True}
            result = query.update(update_values
                                  , synchronize_session=False)

            return result == 1
        return False


def get_table_types(table_type):
    with db.session.begin():
        items = list_dicts(db.query(table_type).filter(table_type.activated_at == ''))
    return items
