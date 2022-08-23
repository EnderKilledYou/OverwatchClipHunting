export default class TwitchClipInstanceScanJob {
    constructor(part: Partial<TwitchClipInstanceScanJob>) {
        Object.assign(this, part)
    }

    id: string = '';
    clip_id: string = '';
    state: string = '';
    broadcaster: string = '';
    created_at: string = '';
    completed_at: string = '';
    percent: string = '';
    error: string = '';
}