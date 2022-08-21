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
          <a target="_blank" :href="`https://clips.twitch.tv/` +item.video_id"><img class="card-img-top"
                                                                                    :src="item.thumbnail_url"
                                                                                    :alt="title"></a>

          <div class="card-body">
            <h5 class="card-title"> {{ item.broadcaster_name }}</h5>
            <p class="card-text">{{ item.title }}</p>
            <p class="card-text">{{ item.created_at }} </p>
          </div>
          <div class="card-footer">

            <button @click="Rescan(item)">
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

let interval: number | null | undefined = null

@Options({
  components: {},
})
export default class ListClipsMade extends Vue {
  items: TwitchClipLog[] = []
  page: number = 1



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
    if (interval)
      clearInterval(interval)
    interval = setInterval(this.list_items.bind(this), 5000)
  }

  async list_items() {
    const jobs = await API.all_clips(this.page)
    this.items = jobs.items.map((a: Partial<TwitchClipInstanceScanJob>) => new TwitchClipInstanceScanJob(a));
  }
}
</script>