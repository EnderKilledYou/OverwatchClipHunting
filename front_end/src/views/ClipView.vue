<template>
  <div class="home">

    <div class="row">

      <div class="col-md-2">
        <div class="btn-group-justified">
          <button class="btn btn-info" @click="PrevPage">Previous</button>
          {{ page }}
          <button class="btn btn-info" @click="NextPage">Next</button>
        </div>
      </div>
      <div class="col-md-4">
        <label for="clip_type"> Search Type
          <select  class="form-select" style="height:20vh" v-model="clipType" multiple>
            <option value="elim">Eliminations</option>
            <option value="blocking">Blocking</option>
            <option value="elimed">Deaths</option>
            <option value="healing">Healing</option>
            <option value="orbed">Orbed</option>
            <option value="slept">Slept</option>
            <option value="assist">Assist</option>
            <option value="defense">Defending</option>
            <option value="spawn_room">Spawn Room</option>
            <option value="game_start">Game Start</option>
            <option value="game_end">Game End</option>
            <option value="queue_start">Queue Start</option>


          </select>

          <input class="text-info" id="streamer_name" type="text" v-model="streamerName" placeholder=" Search Streamer">
          <input class="text-info" id="streamer_name" type="number" min="0" v-model="duration_min"
                 placeholder="Action Duration Min">
        </label>
      </div>
      <div class="col-md-4">
        <div class="btn-group btn-group-sm" role="group" >
          <button @click="Clear()" class="btn btn-sm btn-outline-dark">Clear</button>
          <button @click="Search()" class="btn btn-sm btn-outline-dark">Search</button>
        </div>
      </div>
    </div>
    <div class="row row-cols-3 row-cols-md-4 g-4">
      <div class="col" v-for="item in items" :key="item.id">
        <div class="card">
          <a target="_blank" :href="`https://clips.twitch.tv/` +item[0].video_id"><img class="card-img-top"
                                                                                       :src="item[0].thumbnail_url"
                                                                                       :alt="title"></a>

          <div class="card-body">
            <h5 class="card-title"> {{ item[0].broadcaster_name }}</h5>
            <p class="card-text">{{ item[0].title }}</p>
            <div class="row" v-for="tag in ordered_tags(item[1])">
              {{ tag.tag }} betweens {{ tag.clip_start }} {{ tag.clip_end }} ({{ tag.tag_duration }})<a

                :href="`/video/${tag.id}`"><span
                class="small"> view</span></a>

            </div>
          </div>
          <div class="card-footer">

            <button class="btn btn-info" @click="Rescan(item[0])">Rescan</button>
            <button class="btn btn-danger" @click="Delete(item[0])">Delete</button>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script lang="ts">
import {Options, Vue} from 'vue-class-component';

import {
  API, TwitchClipLog, TwitchClipTag
} from "@/api"; // @ is an alias to /src

@Options({
  components: {},
})
export default class ClipView extends Vue {
  private items: [TwitchClipLog, TwitchClipTag][] = [];

  streamerName: string = ""
  clipType: string[] = []
  private interval: number = 0;
  private streamer: string = "";
  private page: number = 1
  private clip_id: string = ""
  duration_min = 0

  async Rescan(clip: TwitchClipLog) {

    await API.add_clip(clip.video_id)
  }

  Clear() {
    this.clipType = []
    this.streamerName = ""
    this.streamer = ""
    this.clip_id = ""
    this.page = 1
    this.duration_min = 0
  }

  ordered_tags(item: TwitchClipTag[]) {
    return item.slice().sort((a, b) => a.clip_start - b.clip_start)
  }

  created() {

    this.list_items()

  }

  onUnmounted() {
    clearInterval(this.interval)
  }

  async AddClip() {
    await API.add_clip(this.clip_id)
    await this.list_items()
  }

  async Search() {
    this.list_items()
  }

  async Delete(clip: TwitchClipLog) {
    await API.deleteclips(clip.id)
    await this.list_items()
  }

  async update_list_items() {
    await API.clips(this.streamer, this.clipType, this.page)
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

  async list_items() {
    let streamerResponse;
    streamerResponse = await API.clips_search(this.streamer, this.clipType, this.duration_min, this.page)
    this.items = streamerResponse.items
  }

}
</script>
