from queue import Queue

from pipelines.image_pre_processor import get_image_pre_processor
from pipelines.image_to_text_processor import get_image_to_text_processor
from pipelines.overwatch_text_processor import get_overwatch_text_processor
from pipelines.queue_boss import QueueBossBase


class PipeLineImageQueue(QueueBossBase):
    def _process(self, numpy_image):
        image_queue = get_image_pre_processor()
        image_to_text = get_image_to_text_processor()
        text_to_overwatch = get_overwatch_text_processor()
        return_queue = Queue()
        image_queue.add_work(numpy_image, return_queue)
        cropped_image = return_queue.get()
        image_to_text.add_work(cropped_image, return_queue)
        text = return_queue.get()
        text_to_overwatch.add_work(text, None)  # no return, sends to event emitter


piq = [PipeLineImageQueue().start()] #a pipe line of one, starts a thread that waits for add_work and calls _process. Max threads
                                     #is the number of pipelines create


def get_pipe_line_image_queue():
    return piq[0] #normally use priority queue
