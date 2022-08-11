import sys


def in_flask():
    command_line = ' '.join(sys.argv)
    return ('flask' in command_line) or ('gunicorn' in command_line)
