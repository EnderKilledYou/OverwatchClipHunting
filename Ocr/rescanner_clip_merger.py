from Database.Twitch.get_tag_and_bag import get_tag_and_bag_by_clip_id, delete_tag_and_bag_by_id, \
    update_tag_and_bag_start_and_duration


def merge_clip_parts(clip):
    clip_parts = get_tag_and_bag_by_clip_id(clip.id)
    clips_merged = {}
    for bag in clip_parts:
        if bag.tag not in clips_merged:
            clips_merged[bag.tag] = [bag]
            continue
        should_add = True
        for i in range(0, len(clips_merged[bag.tag])):
            existing_tag = clips_merged[bag.tag][i]
            if existing_tag.tag_start == bag.tag_start:
                if existing_tag.tag_duration < bag.tag_duration:
                    delete_tag_and_bag_by_id(existing_tag.id)  # the clip is longer
                    clips_merged[bag.tag][i] = bag
                else:
                    delete_tag_and_bag_by_id(bag.id)  # the existing clip is longer
                should_add = False
                break
            intersection = does_intersect_time(bag, existing_tag)

            if len(intersection) > 0:
                duration_max, tag_min = get_new_start_end(bag, existing_tag)
                existing_tag.tag_start = tag_min
                duration_max_tag_min = duration_max - tag_min
                existing_tag.tag_duration = duration_max_tag_min
                update_tag_and_bag_start_and_duration(existing_tag.id, tag_min, duration_max_tag_min)
                delete_tag_and_bag_by_id(bag.id)
                should_add = False
                break

        if should_add:
            clips_merged[bag.tag].append(bag)
    for item in clips_merged:
        clips_merged[item].clear()
    clips_merged.clear()


def get_new_start_end(bag, existing_tag):
    clip_1_end = existing_tag.tag_start + existing_tag.tag_duration
    clip_2_end = bag.tag_start + bag.tag_duration
    tag_min = min(bag.tag_start, existing_tag.tag_start)
    duration_max = max(clip_1_end, clip_2_end)
    return duration_max, tag_min


def does_intersect_time(bag, existing_tag):
    clip_1_end = existing_tag.tag_start + existing_tag.tag_duration
    clip_2_end = bag.tag_start + bag.tag_duration
    clip_1 = range(existing_tag.tag_start, clip_1_end + 2)
    clip_2 = range(bag.tag_start, clip_2_end + 2)
    xs = set(clip_1)
    intersection = xs.intersection(clip_2)
    return intersection
