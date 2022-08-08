from cli_helper import start_monitor, start_cli, add_stream_to_monitor
from config.config import broadcasters

if __name__ == '__main__':
    start_cli()
    for broadcaster in broadcasters:
        add_stream_to_monitor(broadcaster)

