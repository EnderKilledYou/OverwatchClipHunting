def parse_broadcaster_id(broadcaster, twitch_api):
    try:
        broadcaster_id = None
        if broadcaster is None:
            return None

        result2 = twitch_api.get_users(logins=[broadcaster])
        if len(result2['data']) > 0:
            broadcaster_id = result2['data'][0]['id']
        else:
            raise ValueError("No Such Streamer")
        return broadcaster_id
    except:
        pass
    return None
