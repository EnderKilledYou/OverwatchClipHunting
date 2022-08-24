<template>
  <div class="video" v-if="video_id>=0">
    <vue3-video-player :src="src" @play="OnPlay" :view-core="onVideoPlayer.bind(this)"></vue3-video-player>
  </div>
</template>
<script lang="ts">
import {Options, Vue} from "vue-class-component";
import {Watch} from "vue-facing-decorator";
import {API, TwitchClipLog} from "@/api";


@Options({
  components: {},
})
export default class VideoPlayer extends Vue {
  tag_id: number = -1
  video_id: number = -1
  tag_start: number = -1;

  get src() {
    return '/clip/' + this.video_id
  }

  onVideoPlayer( player: any) {
    player.seek(this.tag_start)

  }

  OnPlay(player:any) {

  }

  async update_video_id(tag_id: number) {
    const video: any = await API.get_clip_by_tag_id(tag_id)
    this.video_id = +video.video_id
    this.tag_start = +video.tag.tag_start
  }

  created() {
    this.tag_id = +this.$route.params['tag_id']
    this.update_video_id(+this.tag_id)
  }

}
</script>