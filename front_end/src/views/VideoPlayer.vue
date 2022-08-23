<template>
  <div class="video" v-if="video_id>=0">
    <vue3-video-player   :src="src"></vue3-video-player>
  </div>
</template>
<script lang="ts">
import {Options, Vue} from "vue-class-component";


@Options({
  components: { },
})
export default class VideoPlayer extends Vue {
  video_id: number = -1

  get src() {
    return '/tag_video/' + this.video_id
  }

  created() {
    this.video_id = +this.$route.params['video_id']
  }
}
</script>