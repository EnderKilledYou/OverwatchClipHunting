<template>
  <div class="col-md-2" v-for="watcher in items" :key="watcher.name">
    <div class="card">
      <img class="card-img-top" v-if="RowHasExtraData(watcher)"
           :src="watcher.data.thumbnail_url.replace('{width}','300').replace('{height}','300')"/>

      <div class="card-body">
        <h5 class="card-title"><a target="_blank" :href="`https://twitch.tv/` + watcher.name">{{
            watcher.name
          }}</a></h5>
        <p class="card-text"> {{ watcher.frames_done }} ( {{ watcher.seconds }} s) / {{ watcher.frames_read }} (
          {{ watcher.frames_read_seconds }} s)</p>
        <p v-if="RowHasExtraData(watcher)" class="card-text"> {{ watcher.data.viewer_count }} watching since:
          {{ new Date(watcher.data.started_at).toLocaleString() }}</p>
        <p v-if="RowHasExtraData(watcher)" class="card-text"> {{ watcher.data.game_name }} </p>
      </div>
      <div class="card-footer">

        <button class="btn btn-danger" @click="Unwatch(watcher)">Stop</button>
      </div>
    </div>

  </div>
</template>
<script lang="ts">
import {API, StreamerMonitorState} from "@/api";

import {Component, Emit, Prop, Vue} from "vue-facing-decorator";

@Component
export default class CurrentlyLive extends Vue {
  async Unwatch(watcher: StreamerMonitorState) {
    this.update_monitor()

  }

  @Prop
  items?: StreamerMonitorState[]

  @Emit('updatedmonitored')
  update_monitor() {

  }

  RowHasExtraData(watcher: StreamerMonitorState) {

    return (watcher.data && watcher.data.thumbnail_url.length > 0)
  }


}
</script>