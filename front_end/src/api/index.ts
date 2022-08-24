const api = require('./api.js')
export const API = api.API


export class StreamerResponse {
    success = false
    items: StreamerMonitorState[] = [];


    constructor(part: Partial<StreamerResponse>) {
        Object.assign(this, part)
        this.items = this.items.map(a => new StreamerMonitorState(a))
    }
}

export class ClipsResponse {
    success: boolean = false
    items: TwitchClipLog[] = [];


    constructor(part: Partial<ClipsResponse>) {
        Object.assign(this, part)
        this.items = this.items.map(a => new TwitchClipLog(a))
    }
}

export class TwitchLiveStreamData {
    id: number = 0
    user_login: string = ''
    game_id: string = ''
    user_name: string = ''
    user_id: string = ''
    game_name: string = ''
    type: string = ''
    _title: string = ''
    viewer_count: number = 0
    started_at: string = ''
    language: string = ''
    thumbnail_url: string = ''

    constructor(part: Partial<TwitchLiveStreamData>) {

        Object.assign(this, part)

    }
}

export default class Monitor {
    constructor(part: Partial<Monitor>) {

        Object.assign(this, part)
    }

    id: string = '';
    broadcaster: string = '';
    make_clips: string = '';
    min_healing_duration: string = '';
    min_elims: string = '';
    min_blocking_duration: string = '';
    min_defense_duration: string = '';
    min_assist_duration: string = '';
    stream_prefers_quality: string = '';
    clip_deaths: string = '';
    is_active: string = '';
    activated_at: string = '';
    activated_by: string = '';
    last_check_in: string = '';
    avoid: string = '';
    cancel_request: string = '';
    frames_read: string = '';
    frames_done: string = '';
    frames_read_seconds: string = '';
    back_fill_seconds: string = '';
    fps: string = '';
    queue_size: string = '';
    stream_resolution: string = '';
}



export class StreamerMonitorState {
    broadcaster = ""
    size = 0
    back_fill_seconds = 0
    queue_size = 0
    frames_read = 0
    frames_done = 0
    stream_resolution = ""
    fps = 0
    frames_read_seconds = 0


    constructor(part: Partial<StreamerMonitorState>) {

        Object.assign(this, part)

    }
}

export class TwitchClipTag {
    id = 0
    clip_id = 0
    tag = ""
    clip_start = 0
    clip_end = 0
    has_file = false
    tag_duration = 0

    constructor(part: Partial<TwitchClipLog>) {
        Object.assign(this, part)
    }
}

export class TwitchClipLog {
    id = 0
    video_id = ""
    video_url = ""
    created_at: Date = new Date()
    buffer_before = 0
    buffer_after = 0
    file_path = ""
    thumbnail_url = ""
    title = ""
    tags = []

    get tag_string() {
        return this.tags.join(",")
    }

    creator_name = ""
    broadcaster_name = ""
    type = ""

    constructor(part: Partial<TwitchClipLog>) {
        Object.assign(this, part)
    }
}

export class StreamerConfig {
    constructor(part: Partial<StreamerConfig>) {
        Object.assign(this, part)
    }

    make_clips = true
    min_healing_duration = 99
    min_elims = 99
    min_blocking_duration = 99
    min_defense_duration = 99
    min_assist_duration = 99
    stream_prefers_quality = '720p60'
    wait_for_mode = true
    buffer_prefers_quality = 'best'
    buffer_elim_clip_after = 5
    buffer_elim_clip_before = 5
    buffer_data = false
    clip_deaths = false
}


