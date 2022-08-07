
import sys
from config.config import broadcasters
import threading


from queue import Queue, Empty


from Ocr.ordered_frame_aggregator import OrderedFrameAggregator
from Ocr.overwatch_screen_reader import OverwatchScreenReader
from Ocr.twitch_video_frame_buffer import TwitchVideoFrameBuffer
from config.config import max_frames_to_scan_per_second
from overwatch_events import overwatch_event
from thread_with_id import ThreadWithId


def start_monitor(broadcaster, start_control=True):
    print("read starting " + broadcaster)
    ocr = TwitchVideoFrameBuffer(max_frames_to_scan_per_second)
    ocr.frame_streamer_name = broadcaster
    agg = OrderedFrameAggregator(overwatch_event)
    matcher = OverwatchScreenReader(ocr, agg)
    producer_thread = threading.Thread(target=ocr.buffer_twitch_broadcast, args=[broadcaster])
    matcher.show = True
    consumer_threads = []
    for i in range(0, 4):
        consumer_thread = threading.Thread(target=matcher.consume_twitch_broadcast)
        consumer_threads.append(consumer_thread)
    producer_thread.start()


    for consumer_thread in consumer_threads:
        consumer_thread.start()
    if start_control:
        input_thread = threading.Thread(target=input_control, args=[matcher, ocr])
        input_thread.start()
    else:
        return matcher, ocr, consumer_threads, producer_thread
    join_consumers(consumer_threads)
    print("Matcher threads exited")
    producer_thread.join()
    print("Video stream thread exited")
    input_thread.join()


def join_consumers(consumer_threads):
    print("joining consumer threads")
    for consumer_thread in consumer_threads:
        consumer_thread.join()


stdInQueue = Queue()


def input_reader(matcher: OverwatchScreenReader, ocr: TwitchVideoFrameBuffer):
    while matcher.Active and ocr.Active:
        item = sys.stdin.readline().strip()
        if item == "quit":
            print("quitting")
            matcher.Active = False
            ocr.Active = False
            print("clearing sub watchers")
            try:
                while True:
                    (m2, o2, consumers, producer) = matchers.get(True, 1)
                    print("clearing sub watchers")
                    m2.Active = False
                    o2.Active = False
                    join_consumers(consumers)
                    producer.join()

            except Empty as e:
                pass
            print("cleared sub watchers")

        stdInQueue.put(item)


def get_next() -> str:
    try:
        return stdInQueue.get(True, 5)
    except Empty as e:
        return ''


matchers = Queue()


def input_control(matcher: OverwatchScreenReader, ocr: TwitchVideoFrameBuffer):
    print("control thread started")
    input_thread = ThreadWithId(target=input_reader, args=[matcher, ocr])
    input_thread.start()
    showBuffered = False
    for stream in broadcasters[1:]:
        (m2, o2, consumers, producer) = start_monitor(stream, start_control=False)
        matchers.put((m2, o2, consumers, producer))
    while matcher.Active and ocr.Active:
        item: str = get_next()
        if item is None:
            pass
        if item == 'show stats':
            showBuffered = True
        if item == 'hide stats':
            showBuffered = False
        if item.startswith('watch '):
            params = item.split(' ')
            stream = params[1]
            (m2, o2, consumers, producer) = start_monitor(stream, start_control=False)
            matchers.put((m2, o2, consumers, producer))

        qsize = ocr.buffer.qsize()
        if showBuffered or qsize > 300:
            if qsize > 300:
                print("warning buffer is getting back logged! live streaming clips may be misaligned! ")
            seconds = qsize / max_frames_to_scan_per_second
            print("Total buffered: " + str(qsize) + " in seconds: " + str(seconds))

    input_thread.join()
