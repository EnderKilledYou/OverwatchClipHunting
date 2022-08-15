<template>
  <div class="container-fluid">
    <div class="d-grid gap-2 col-6 mx-auto">
      <div class="btn-group-justified">
        <button class="btn btn-info" @click="PrevPage">Previous</button>
        {{ page }}
        <button class="btn btn-info" @click="NextPage">Next</button>

      </div>
    </div>
    <div class="row row-cols-3 row-cols-md-4 g-4">
      <div class="col" v-for="item in items" :key="item.id">
        <div class="card">
          <a target="_blank" :href="`https://clips.twitch.tv/` +item[1].video_id"><img class="card-img-top"
                                                                                       :src="item[1].thumbnail_url"
                                                                                       :alt="title"></a>

          <div class="card-body">
            <h5 class="card-title"> {{ stateToString(item[0].state) }}</h5>
            <p class="card-text">{{ item[1].title }}</p>
            <p class="card-text">{{ item[0].error}} </p>
          </div>
          <div class="card-footer">

            <div class="progress">
              <div class="progress-bar" role="progressbar" :style="`width: ${item[0].percent * 100}%`"
                   :aria-valuenow="item[0].percent * 100" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
            <button @click="Rescan(item[1])" v-if="item[0].state === 3">
              Rescan
            </button>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>
<script lang="ts">
import {Options, Vue} from "vue-class-component";
import TwitchClipInstanceScanJob from "@/views/TwitchClipInstanceScanJob";
import {API, TwitchClipLog} from "@/api";

@Options({
  components: {},
})
export default class ListScanJob extends Vue {
  items: [TwitchClipInstanceScanJob, TwitchClipLog][] = []
  page: number = 1

  stateToString(num: number) {
    switch (+num) {
      case 0:
        return "in queue"
      case 1:
        return "running"
      case 2:
        return "complete"
      case 3:
        return "error"
      case 5:
        return "in queue"
      default:
        return "unknown"
    }
  }

  async PrevPage() {
    if (this.page === 0) return;
    this.page = this.page - 1
    await this.list_items()
  }

  async NextPage() {
    this.page = this.page + 1
    await this.list_items()
  }

  async Rescan(clip: TwitchClipLog) {
    await API.add_clip(clip.video_id)
    await this.list_items();
  }

  created() {
    this.list_items()
  }

  async list_items() {
    const jobs = await API.get_clip_scan_jobs(this.page)
    this.items = jobs.items.map((a: Partial<TwitchClipInstanceScanJob>) => new TwitchClipInstanceScanJob(a));
  }
}
</script>