from pipelines.queue_boss import QueueBossBase


class OverwatchTextProcessor(QueueBossBase):
    def _process(self, job_tuple):
        text, frame_tester, frame = job_tuple
        frame_tester.test_overwatch_frame(frame, text)
        text = None


otp = [OverwatchTextProcessor().start()]


def get_overwatch_text_processor():
    return otp[0]
