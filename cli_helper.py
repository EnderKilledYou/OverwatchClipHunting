import sys
from config.config import broadcasters
from config.streamer_configs import get_streamer_config
import threading

from queue import Queue, Empty

from Ocr.ordered_frame_aggregator import OrderedFrameAggregator
from Ocr.overwatch_screen_reader import OverwatchScreenReader
from Ocr.twitch_video_frame_buffer import TwitchVideoFrameBuffer

from frame_buffer import set_frame_buffer

from overwatch_events import overwatch_event
from thread_with_id import ThreadWithId


def start_cli():
    input_thread = threading.Thread(target=input_control, args=[])
    input_thread.start()
    input_thread.join()


def start_monitor(broadcaster):
    print("read starting " + broadcaster)

    ocr = TwitchVideoFrameBuffer(broadcaster, get_streamer_config(broadcaster).max_frames_to_scan_per_second)
    ocr.frame_streamer_name = broadcaster
    set_frame_buffer(broadcaster, ocr)

    agg = OrderedFrameAggregator(overwatch_event)
    matcher = OverwatchScreenReader(ocr, agg)
    producer_thread = threading.Thread(target=ocr.watch_streamer, args=[])
    matcher.show = True
    consumer_threads = []
    for i in range(0, 4):
        consumer_thread = threading.Thread(target=matcher.consume_twitch_broadcast)
        consumer_threads.append(consumer_thread)
    producer_thread.start()

    for consumer_thread in consumer_threads:
        consumer_thread.start()

    return matcher, ocr, consumer_threads, producer_thread


def join_consumers(consumer_threads, who):
    print("joining consumer threads " + who)
    for consumer_thread in consumer_threads:
        consumer_thread.join()
    print("joined consumer threads  " + who)


stdInQueue = Queue()


def input_reader():
    while True:
        item = sys.stdin.readline().strip()
        if item == "quit":
            stdInQueue.put(item)
            print("quitting")
            try:
                for (m2, o2, consumers, producer) in matchers:
                    print("clearing sub watchers " + o2.frame_streamer_name)
                    m2.Active = False
                    o2.Active = False
                    join_consumers(consumers, o2.frame_streamer_name)
                    print("joining producer thread " + o2.frame_streamer_name)
                    producer.join()
                    print("cleared sub watchers " + o2.frame_streamer_name)
                matchers.clear()

            except Empty as e:
                pass
            print("cleared sub watchers")
            return

        stdInQueue.put(item)


def get_next() -> str:
    try:
        return stdInQueue.get(True, 5)
    except Empty as e:
        return ''


matchers = []


def input_control():
    print("control thread started")
    input_thread = ThreadWithId(target=input_reader)
    input_thread.start()
    showBuffered = False
    for stream in broadcasters[1:]:
        add_stream_to_monitor(stream)
    if len(sys.argv) > 1:
        add_stream_to_monitor(sys.argv[1])
    while True:
        item: str = get_next()
        if item is None:
            pass
        if item == 'quit':
            sys.exit(0)
            return
        if item == 'show stats':
            showBuffered = True
        if item == 'hide stats':
            showBuffered = False
        if item.startswith('watch '):
            params = item.split(' ')
            add_stream_to_monitor(params[1])

        for (matcher, ocr, consumers, producer) in matchers:
            qsize = ocr.buffer.qsize()
            if showBuffered or qsize > 300:
                if qsize > 300:
                    print(
                        "warning buffer is getting back logged! dumping!" + ocr.frame_streamer_name + "live streaming clips "
                                                                                                      "may be misaligned! ")
                    dump_queue_items(ocr)
                seconds = qsize / get_streamer_config(ocr.frame_streamer_name).max_frames_to_scan_per_second
                print("({2}) Total buffered: {0} in seconds: {1}".format(str(qsize), str(seconds),
                                                                         ocr.frame_streamer_name))
    input_thread.join()


def dump_queue_items(ocr):
    for i in range(0, 250):
        try:
            ocr.buffer.get(False)
        except Empty as e:
            pass


def add_stream_to_monitor(stream):
    (m2, o2, consumers, producer) = start_monitor(stream)
    matchers.append((m2, o2, consumers, producer))
