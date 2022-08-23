import shutil

import requests
from twitchdl import twitch
from twitchdl.commands.download import get_clip_authenticated_url

from Ocr.twitch_dl_args import Args


def fast_download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
            r.close()




def _download_clip(slug, args):
    print("<dim>Looking up clip...</dim>")
    clip = twitch.get_clip(slug)
    if not clip:
        return
    game = clip["game"]["name"] if clip["game"] else "Unknown"

    url = get_clip_authenticated_url(slug, args.quality)
    print("Selected URL: {}".format(url))

    print("Downloading clip...")
    print(url, args.output)
    fast_download_file(url, args.output)
    print("Downloaded: {} ".format(args.output))


if __name__ == '__main__':
    _download_clip('KathishIncredulousMilkCharlietheUnicorn-Z2f3jnIXtOkmAwwZ',
                   Args('KathishIncredulousMilkCharlietheUnicorn-Z2f3jnIXtOkmAwwZ', 'test.mp4'))
