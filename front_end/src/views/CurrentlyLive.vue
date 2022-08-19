<template>
  <div class="col-md-3" v-for="watcher in ShowableItems" :key="watcher.name">
    <div class="card">
      <img class="card-img-top" v-if="GetLiveStream(watcher)"
           :src="GetThumbnailUrl(watcher)"/>

      <div class="card-body">
        <h5 class="card-title"><a target="_blank" :href="`https://twitch.tv/` + watcher.name">{{
            watcher.name
          }}</a></h5>
        <p class="card-text" v-if="GetLiveStream(watcher)"> {{ watcher.frames_done }} ( {{
            watcher.back_fill_seconds
          }} s) / {{ watcher.frames_read }}
          (
          {{ watcher.frames_read_seconds }} s)</p>
        <p v-if="GetLiveStream(watcher)" class="card-text">
          {{ watcher.viewer_count }} watching since:
          {{ watcher.started_at }}</p>
        <p v-if="GetLiveStream(watcher)" class="card-text"> {{ watcher.game_name }} </p>
      </div>
      <span class="text-success">({{
          watcher.stream_resolution
        }}@{{ watcher.fps }})</span>
      <button class="btn btn-danger btn-block btn-outline-dark" @click="Avoid(watcher)">Avoid Watching</button>


    </div>

  </div>
</template>
<script lang="ts">
import Monitor, {API, StreamerMonitorState, TwitchLiveStreamData} from "@/api";

import {Component, Emit, Prop, Vue, Watch} from "vue-facing-decorator";

@Component
export default class CurrentlyLive extends Vue {
  private twitch_streams: any[] = [];


  async Unwatch(watcher: Monitor) {
    await API.remove(watcher.broadcaster)
    await this.update_monitor()

  }

  GetLiveStream(monitor: Monitor) {
    return this.LiveStreams.find(a => a.user_login === monitor.broadcaster)
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
    return this.GetLiveStream(watcher)
  }

  @Prop show_inactive?: boolean

  async Avoid(watcher: Monitor) {
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
    this.streamerMonitorStates = item.map((a: any) => new Monitor(a));
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