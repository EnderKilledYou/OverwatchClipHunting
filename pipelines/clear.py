def clear_queue(buffer):
    try:
        while True:
            item = buffer.get(False)
            del item
    except Empty:
        pass
