from Ocr.re_scaner import ReScanner


from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_video_id


def test_rescanner_clipper_monitor():
    return
    scanner = ReScanner()
    monitor = ReScannerMonitor(scanner)
    # api = get_twitch_api()
    # bag_and_tag_clip(api)
    video_id = 'IncredulousRelatedCheeseBudStar-mwq2wt5iKH6CLmNO'
    clip = get_twitch_clip_instance_by_video_id(video_id)
    monitor.add_job(clip.id)
    monitor.start()
    scanner.start()
