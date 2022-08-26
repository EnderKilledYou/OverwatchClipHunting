import threading


class TableThreadJob:

    def __init__(self, table_type):
        self.thread = None
        self._table_type = table_type
        self._id = None

    def __del__(self):
        self._table_type = None
        self.thread = None

    def start(self):
        threading_thread = threading.Thread(target=self._start)
        threading_thread.start()
        self.thread = threading_thread

    def _start(self):
        self._table_type.query

    def _stop(self):
        if self._id is None:
            return


