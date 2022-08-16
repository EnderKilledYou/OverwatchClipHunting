function makeURL(route) {
    if (window.baseURL) return window.baseURL + route;
    return route;
}

export class Core {
    static makeRequest(route, body) {
        return new Promise((resolve, reject) => {
            fetch(makeURL(route), {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(body),
            }).then((r) => {
                r.json().then((data) => {
                    if (data.result != null && "error" in data.result) {
                        reject(data.result.error);
                        return;
                    }
                    resolve(data.result);
                });
            }).catch((e) => {
                reject(e);
            })
        });
    }
}

export class API {
    static add (stream_name,) {

    return Core.makeRequest("/api/streamer/add", {
        stream_name: stream_name,
        });
}

static list () {

    return Core.makeRequest("/api/streamer/list", {
        });
}

static remove (stream_name,) {

    return Core.makeRequest("/api/streamer/remove", {
        stream_name: stream_name,
        });
}

static start_farm_twitch () {

    return Core.makeRequest("/api/monitor/start_farm_twitch", {
        });
}

static stop_farm_twitch () {

    return Core.makeRequest("/api/monitor/stop_farm_twitch", {
        });
}

static get_live_streamers () {

    return Core.makeRequest("/api/monitor/get_live_streamers", {
        });
}

static add_tag_clipping (clip_id,tag_id,) {

    return Core.makeRequest("/api/monitor/add_tag_clipping", {
        clip_id: clip_id,
        tag_id: tag_id,
        });
}

static add_clip (clip_id,) {

    return Core.makeRequest("/api/clips/add_clip", {
        clip_id: clip_id,
        });
}

static get_game_ids () {

    return Core.makeRequest("/api/clips/get_game_ids", {
        });
}

static get_clip_scan_jobs (page,) {

    return Core.makeRequest("/api/clips/get_clip_scan_jobs", {
        page: page,
        });
}

static add_clip_scan (clip_id,) {

    return Core.makeRequest("/api/clips/add_clip_scan", {
        clip_id: clip_id,
        });
}

static deleteclips (clip_id,) {

    return Core.makeRequest("/api/clips/deleteclips", {
        clip_id: clip_id,
        });
}

static clip_tags (clip_id,tag_id,) {

    return Core.makeRequest("/api/clips/clip_tags", {
        clip_id: clip_id,
        tag_id: tag_id,
        });
}

static search_twitch_clips (broadcaster,game_id,clip_id,ended_at,started_at,after_cursor,before_cursor,) {

    return Core.makeRequest("/api/clips/search_twitch_clips", {
        broadcaster: broadcaster,
        game_id: game_id,
        clip_id: clip_id,
        ended_at: ended_at,
        started_at: started_at,
        after_cursor: after_cursor,
        before_cursor: before_cursor,
        });
}

static tags_job (clip_id,) {

    return Core.makeRequest("/api/clips/tags_job", {
        clip_id: clip_id,
        });
}

static clips_search (creator_name,clip_type,page,) {

    return Core.makeRequest("/api/clips/clips_search", {
        creator_name: creator_name,
        clip_type: clip_type,
        page: page,
        });
}

static all_clips (clip_type,page,) {

    return Core.makeRequest("/api/clips/all_clips", {
        clip_type: clip_type,
        page: page,
        });
}
}