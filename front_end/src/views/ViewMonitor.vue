<template>
  <div class="row" v-if="watcher !== undefined && live_stream !== undefined ">

    <div class="card col-md-10 offset-1">
      <img class="card-img-top"
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
        <p class="card-text">
          {{ live_stream.viewer_count }} watching since:
          {{ live_stream.started_at }}</p>
        <p class="card-text"> {{ live_stream.game_name }} {{live_stream.title}} </p>
      </div>
      <span v-if="watcher.is_active" class="text-success">({{
          watcher.stream_resolution
        }}@{{ watcher.fps }})</span> <span v-if="WatcherClaimed(watcher)"
                                           class="text-success"> Managed by: {{
        watcher.activated_by
      }} last seen :(  <span class="small text-muted">{{ watcher.activated_at }} )</span> </span>

      <button v-if="HasRole('admin')" class="btn btn-danger btn-block btn-outline-dark" @click="Avoid(watcher)">Avoid
        Watching
      </button>

      <button v-if="HasRole('admin')" class="btn btn-success btn-block btn-outline-dark" @click="Requeue(watcher)">
        Requeue
      </button>

    </div>


  </div>
</template>
<script lang="ts">
import Monitor, {API, StreamerMonitorState, TwitchLiveStreamData} from "@/api";

import {Component, Emit, Prop, Vue, Watch} from "vue-facing-decorator";
import prettyMilliseconds from 'pretty-ms';
import {HasRole} from "@/views/has_role";


@Component({
  emits: ['monitor_unselected']

})
export default class ViewMonitor extends Vue {


  prettyMilliseconds(time: any) {
    return prettyMilliseconds(time)
  }

  HasRole(role: string) {
    return HasRole(role)
  }

  WatcherClaimed(watcher: Monitor) {
    return watcher.activated_by && watcher.activated_by.length > 0
  }

  Requeue(monitor: Monitor) {
    API.add(monitor.broadcaster)
  }


  IsActive(monitor: Monitor) {
    return monitor.activated_by && monitor.activated_by.trim().length > 0
  }


  @Prop({required: true}) Me: any
  @Prop({required: true})
  watcher?: Monitor;
  @Prop({required: true})
  live_stream?: TwitchLiveStreamData;

  @Emit('avoid')
  async Avoid(watcher: Monitor) {


  }


  created() {

  }


  @Emit('updatedmonitored')
  update_monitor() {

  }

  GetThumbnailUrl(watcher: Monitor) {

    if (this.live_stream === undefined) return ''
    const base_image = this.live_stream.thumbnail_url.replace('{width}', '900').replace('{height}', '900');
    return base_image + '?cache_burst=' + Math.random()
  }


}
</script>