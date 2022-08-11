from sqlalchemy_serializer import SerializerMixin


class ClipTimeStamp(SerializerMixin):
    id = 0
    start = 0
    end = 0
    duration = 0
    type = ''
    start_buffer = 0
    end_buffer = 0
