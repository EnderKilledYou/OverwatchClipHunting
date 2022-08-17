export const baseUrl = ''
export const add_streamer_path = '/add_streamer/'
export const remove_streamer_path = '/remove_streamer/'
export const list_streamer_path = '/list_streamer'
export const list_clips_path = '/clips/'
export const all_list_clips_path = '/all_clips/'
export const delete_clips_path = '/delete_clips/'
const api = require('./api.js')
export const API = api.API

export async function add_streamer(streamer: string): Promise<StreamerResponse> {
    const result = await fetch(baseUrl + add_streamer_path + streamer, {})
    let response = await result.json();
    return new StreamerResponse(response)

}

export async function remove_streamer(streamer: string) {
    const result = await fetch(baseUrl + remove_streamer_path + streamer, {})
    let response = await result.json();
    return new StreamerResponse(response)
}

export async function list_streamer(): Promise<StreamerResponse> {
    const result = await fetch(baseUrl + list_streamer_path, {})
    let response = await result.json();
    return new StreamerResponse(response)

}

export async function delete_clip(clip_id: number): Promise<ClipsResponse> {
    const result = await fetch(baseUrl + delete_clips_path + encodeURIComponent(clip_id), {})
    let response = await result.json();
    return new ClipsResponse(response)

}

export async function list_clips(streamer: string, type: string, page: number = 1): Promise<ClipsResponse> {
    const result = await fetch(baseUrl + list_clips_path + encodeURIComponent(streamer) + "/" + encodeURIComponent(page), {})
    let response = await result.json();
    return new ClipsResponse(response)

}

export async function list_all_clips(type: string, page: number = 1): Promise<ClipsResponse> {
    const result = await fetch(baseUrl + all_list_clips_path + encodeURIComponent(type) + '/' + encodeURIComponent(page), {})
    let response = await result.json();
    return new ClipsResponse(response)

}

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
    viewer_count = 0
    started_at = 0
    game_name = ''
    thumbnail_url = ''

    constructor(part: Partial<TwitchLiveStreamData>) {
        Object.assign(this, part)

    }
}

export class StreamerMonitorState {
    name = ""
    size = 0
    back_fill_seconds = 0
    queue_size = 0
    frames_read = 0
    frames_done = 0
    frames_read_seconds = 0
    data: TwitchLiveStreamData

    constructor(part: Partial<StreamerMonitorState>) {
        debugger
        Object.assign(this, part)
        if (part && part.data) {
            this.data = new TwitchLiveStreamData(part.data)
        } else {
            this.data = new TwitchLiveStreamData({})
        }
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


