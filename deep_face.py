from app import app
from AI.deep_facer import DeepFacer


from Database.Twitch.twitch_clip_instance import   get_twitch_clip_instance_by_id
from Database.Twitch.tag_clipper_job import get_twitch_clip_job, get_twitch_clip_job_by_id



def main():

    facer = DeepFacer()

    job = get_twitch_clip_job_by_id(489)
    if job is None:

        return
    clip = get_twitch_clip_instance_by_id(job.clip_id)
    facer.start()
    facer.add_job((clip.id, clip.file_path, job.id))
    facer.join()

if __name__ == "__main__":
    main()