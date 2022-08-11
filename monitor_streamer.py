from cli_helper import start_monitor, start_cli, add_stream_to_monitor
from config.config import broadcasters
from twitch_helpers import get_twitch_api

if __name__ == '__main__':
    # for broadcaster in broadcasters:
    #     add_stream_to_monitor(broadcaster)
    # start_cli()
    twitch = get_twitch_api()
    # stream = twitch.get_streams(user_login='sunshinebread')
    # print(stream)
    clip = twitch.get_clips(clip_id='IncredulousRelatedCheeseBudStar-mwq2wt5iKH6CLmNO')
    print(clip)


