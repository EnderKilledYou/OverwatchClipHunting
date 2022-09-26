import threading

from cancel_token import CancellationToken

from Database.monitor import self_id
from Database.unclaim_monitor import claim_table_type, unclaim_table_type, get_table_claims, get_claimed


class TableThreadJob:

    def __init__(self, table_type):
        self.thread = None
        self._table_type = table_type
        self._id = None

        self._cancel_token = CancellationToken()




    def __del__(self):
        self._table_type = None
        self.thread = None

    def start(self):
        threading_thread = threading.Thread(target=self._start)
        threading_thread.start()
        self.thread = threading_thread

    def _work(self):
        work = get_claimed(self._table_type, self._id)
        self._do_work(work)
        del work

    def _do_work(self, work):
        pass

    def set_id(self, id):
        self._id = id

    def _start(self):
        if self._id is None:
            for unclaim in get_table_claims(self._table_type):
                if claim_table_type(self._table_type, unclaim.id, self_id):
                    self._id = unclaim.id
                    break
        if self._id is not None:
            self._work()

    def stop(self):
        self._cancel_token.cancel()
        unclaim_table_type(self._table_type, self._id)
