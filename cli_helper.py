import ctypes
import sys

import threading
from time import sleep

from queue import Queue, Empty
from Ocr.ordered_frame_aggregator import OrderedFrameAggregator
from Ocr.overwatch_screen_reader import OverwatchScreenReader
from Ocr.twitch_video_frame_buffer import TwitchVideoFrameBuffer
from config.config import broadcaster, max_frames_to_scan_per_second
from overwatch_events import overwatch_event
from thread_with_id import ThreadWithId


def start_monitor():
    print("read starting " + broadcaster)
    ocr = TwitchVideoFrameBuffer(max_frames_to_scan_per_second)
    agg = OrderedFrameAggregator(overwatch_event)
    matcher = OverwatchScreenReader(ocr, agg)
    producer_thread = threading.Thread(target=ocr.buffer_twitch_broadcast, args=[broadcaster])
    matcher.show = True
    consumer_threads = []
    for i in range(0, 4):
        consumer_thread = threading.Thread(target=matcher.consume_twitch_broadcast)
        consumer_threads.append(consumer_thread)
    producer_thread.start()
    sleep(5)

    for consumer_thread in consumer_threads:
        consumer_thread.start()

    input_control(matcher, ocr)

    for consumer_thread in consumer_threads:
        consumer_thread.join()
    print("Matcher threads exited")
    producer_thread.join()
    print("Video stream thread exited")


stdInQueue = Queue()


def input_reader(matcher: OverwatchScreenReader, ocr: TwitchVideoFrameBuffer):
    while matcher.Active and ocr.Active:
        item = sys.stdin.readline().strip()
        if item == "quit":
            matcher.Active = False
            ocr.Active = False
            break
        stdInQueue.put(item)


def get_next():
    try:
        return stdInQueue.get(True, 5)
    except Empty as e:
        pass
        return None


def input_control(matcher: OverwatchScreenReader, ocr: TwitchVideoFrameBuffer):
    input_thread = ThreadWithId(target=input_reader, args=[matcher, ocr])
    input_thread.start()
    showBuffered = False
    while matcher.Active and ocr.Active:
        item = get_next()
        if item is None:
            pass
        if item == 'show stats':
            showBuffered = True
        if item == 'hide stats':
            showBuffered = False

        qsize = ocr.buffer.qsize()
        if showBuffered or qsize > 300:
            if qsize > 300:
                print("warning buffer is getting back logged! live streaming clips may be misaligned! ")
            print("Total buffered: " + str(qsize))

    input_thread.join()
