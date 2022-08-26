def clear_queue(buffer, broadcaster):
    try:
        print(f"stopping - emptying buffer - {broadcaster}")
        while True:
            item = buffer.get(False)
            del item
    except:
        pass
