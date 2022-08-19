import json

from app import app
from Database.monitor import claim_monitor, Monitor


def test_query():
    tmp = Monitor("Asdfasd",{})
    dumps = json.dumps(tmp)
    print(dumps)
    print('ok')


