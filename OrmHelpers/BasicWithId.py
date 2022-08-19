from typing import Dict

from Database.MissingRecordError import MissingRecordError
from config.db_config import db


class UpdateProxy:
    def __init__(self, class_type, id):
        self._class_type = class_type
        self._id = id

    def __setitem__(self, key, value):
        record = self._class_type.query.filter_by(id=self._id).first()
        if not record:
            raise MissingRecordError("No such record " + self._id + " of " + str(self._class_type))
        setattr(record, key, value)
        db.session.commit()
        db.session.flush()


class BasicWithId:
    def __init__(self, class_type):
        self.class_type = class_type

    def if_exists(self, id: int) -> bool:
        return self.class_type.query.filter_by(id=id).first() is None

    def get_by_id(self, id: int):
        return self.class_type.query.filter_by(id=id).first()

    def get_by_filter(self, filter_dict: Dict[str, any]) -> bool:
        return self.class_type.query.filter_by(filter_dict).first()

    def get_all_by_filter(self, filter_dict: Dict[str, any], page: int = 1, per_page: int = 25) -> bool:
        return self.class_type.query.filter_by(filter_dict).paginate(page=page, per_page=per_page).items

    def if_exists_filter(self, filter_dict: Dict[str, any]) -> bool:
        return self.class_type.query.filter_by(filter_dict).first() is None

    def add(self, value_dict: Dict[str, any] = {}):
        item = self.class_type(value_dict)
        db.session.add(item)

        db.session.flush()
