<template>
  <div class="col-md-3" v-for="watcher in ShowableItems" :key="watcher.name">
    <div class="card">
      <img class="card-img-top" v-if="GetLiveStream(watcher)"
           :src="GetThumbnailUrl(watcher)"/>

      <div class="card-body">
        <h5 class="card-title"><a target="_blank" :href="`https://twitch.tv/` + watcher.broadcaster">{{
            watcher.broadcaster
          }}</a></h5>
        <p class="card-text" v-if="watcher.is_active"> {{ watcher.frames_done }} ( {{
            watcher.back_fill_seconds
          }} s lag) / {{ watcher.frames_read }}
          (
          {{ prettyMilliseconds(watcher.frames_read_seconds * 1000) }} s <small class="text-danger"> read</small>)</p>
        <p v-if="GetLiveStream(watcher)" class="card-text">
          {{ GetLiveStream(watcher).viewer_count }} watching since:
          {{ GetLiveStream(watcher).started_at }}</p>
        <p v-if="GetLiveStream(watcher)" class="card-text"> {{ GetLiveStream(watcher).game_name }} </p>
      </div>
      <span v-if="watcher.is_active" class="text-success">({{
          watcher.stream_resolution
        }}@{{ watcher.fps }})</span> <span v-if="WatcherClaimed(watcher)"
                                           class="text-success"> Managed by: {{
        watcher.activated_by
      }} last seen :(  <span class="small text-muted">{{ watcher.activated_at }} )</span> </span>

      <button class="btn btn-danger btn-block btn-outline-dark" @click="Avoid(watcher)">Avoid Watching</button>

      <button class="btn btn-success btn-block btn-outline-dark" @click="Requeue(watcher)">Requeue</button>

    </div>

  </div>
</template>
<script lang="ts">
import Monitor, {API, StreamerMonitorState, TwitchLiveStreamData} from "@/api";

import {Component, Emit, Prop, Vue, Watch} from "vue-facing-decorator";
import prettyMilliseconds from 'pretty-ms';

@Component
export default class CurrentlyLive extends Vue {
  private twitch_streams: any[] = [];

  prettyMilliseconds(time: any) {
    return prettyMilliseconds(time)
  }

  async Unwatch(watcher: Monitor) {
    await API.remove(watcher.broadcaster)
    await this.update_monitor()

  }

  WatcherClaimed(watcher: Monitor) {
    return watcher.activated_by && watcher.activated_by.length > 0
  }

  Requeue(monitor: Monitor) {
    API.add(monitor.broadcaster)
  }

  GetLiveStream(monitor: Monitor) {
    return this.LiveStreams.find(a => a.user_login === monitor.broadcaster.toLowerCase())
  }

  IsActive(monitor: Monitor) {
    return monitor.activated_by && monitor.activated_by.trim().length > 0
  }

  get ShowableItems() {
    return this.streamerMonitorStates.filter(this.ShouldShow.bind(this))
  }

  ShouldShow(watcher: Monitor) {

    if (this.show_inactive) {
      return true
    }
    return watcher.is_active
  }

  @Prop show_inactive?: boolean

  async Avoid(watcher: Monitor) {
    alert("avoiding " + watcher.broadcaster)
    await API.avoid_user(watcher.broadcaster)
    await this.update_monitor()

  }

  streamerMonitorStates: Monitor[] = [];
  private LiveStreams: TwitchLiveStreamData[] = [];
  @Prop
  items?: [Monitor[], TwitchLiveStreamData[]]

  created() {

  }

  @Watch('items') items_changed(streamerResponse: [Monitor[], TwitchLiveStreamData[]]) {
    this.update_from_props();
  }

  private update_from_props() {
    debugger
    if (!this.items) return
    let item = this.items[0];
    if (item) {
      this.streamerMonitorStates = item.map((a: any) => new Monitor(a));
    }
    if (this.items.length > 1 && this.items[1])
      this.LiveStreams = this.items[1].map((a: any) => new TwitchLiveStreamData(a));
  }

  @Emit('updatedmonitored')
  update_monitor() {

  }

  GetThumbnailUrl(watcher: Monitor) {

    const live_stream = this.GetLiveStream(watcher)
    if (!live_stream) return ''
    const base_image = live_stream.thumbnail_url.replace('{width}', '300').replace('{height}', '300');
    return base_image + '?cache_burst=' + Math.random()
  }


}
</script>