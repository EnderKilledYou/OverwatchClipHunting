<template>
  <div class="col-md-2" v-for="watcher in streams" :key="watcher.name">
    <div class="card">
      <img class="card-img-top"
           :src="GetThumbnailUrl(watcher)"/>

      <div class="card-body">
        <h5 class="card-title"><a target="_blank" :href="`https://twitch.tv/` + watcher.user_name">{{
            watcher.user_name
          }}</a></h5>
        <p class="card-text"> {{ watcher.viewer_count }} watching since:
          {{ new Date(watcher.started_at).toLocaleString() }}</p>
        <p class="card-text"> {{ watcher.game_name }} </p>
      </div>
      <button class="btn btn-danger" @click="Watch2( watcher.user_name)">Watch</button>
    </div>

  </div>


</template>
<script lang="ts">
import {API, StreamerMonitorState, TwitchLiveStreamData} from "@/api";
import {Component, Emit, Prop, Vue} from "vue-facing-decorator";


@Component
export default class OnTwitchNow extends Vue {
  @Prop
  streams?: TwitchLiveStreamData[]

  GetThumbnailUrl(watcher: TwitchLiveStreamData) {

    const base_image = watcher.thumbnail_url.replace('{width}', '300').replace('{height}', '300');
    return base_image + '?cache_burst=' + Math.random()
  }

  async Watch2(streamerName: string) {
    const streamerResponse = await API.add(streamerName)
    this.update_monitor()
  }

  @Emit('updatedmonitored')
  update_monitor() {

  }
}
</script>