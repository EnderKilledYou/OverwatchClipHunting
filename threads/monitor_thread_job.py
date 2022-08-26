from Database.monitor import Monitor
from Database.unclaim_monitor import unclaim_table_type
from Ocr.twitch_video_frame_buffer import TwitchEater
from threads.TableThreadJob import TableThreadJob


class MonitorThreadJob(TableThreadJob):

    def __init__(self, broadcaster):
        super(MonitorThreadJob,self).__init__(Monitor)
        self.broadcaster = broadcaster

    def _do_work(self, work: Monitor):
        print(f"starting do broadcast for {work.broadcaster}")
        with TwitchEater(work.broadcaster) as ocr:
            self._stop = ocr.stop
            self._get_stats = ocr.get_stats
            ocr.buffer_broadcast()
            self._get_stats = None
            self._stop = None
            print(f"Exiting do broadcast for {work.broadcaster}")
        print(f"Unclaiming for {work.broadcaster}")
        unclaim_table_type(Monitor, self._id)
        print(f"Unclaimed for {work.broadcaster}")
