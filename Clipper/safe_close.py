def safe_close(item):
    try:
        item.close()
    finally:
        pass
