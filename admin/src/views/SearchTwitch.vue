<template>
  <div class="home">

    <div class="row">
      <div class="col-md-3">
        <label for="streamer_name"> Streamer Name
          <input class="form-control" id="broadcaster_id" type="text" v-model="broadcaster_id">

        </label>
      </div>
      <div class="col-md-3">
        <label for="clip_id"> Clip List
          <textarea class="form-control" id="clip_id" type="text" v-model="clip_id"/>

        </label>
      </div>
      <div class="col-md-3">
        <label for="streamer_name"> game_id
          <input class="form-control" id="game_id" type="text" v-model="game_id">

        </label>
      </div>
      <div class="col-md-3">
        <label for="started_at"> Search Starting Date
          <input class="form-control" id="started_at" type="date" v-model="started_at">

        </label>
      </div>
      <div class="col-md-3">
        <label for="ended_at"> Search Starting Date Ended At
          <input class="form-control" id="ended_at" type="date" v-model="ended_at">

        </label>
      </div>


    </div>


    <button @click="Search()" class="btn btn-block btn-primary">Search</button>
    <div class="btn-group-justified">


      <button class="btn btn-info" @click="NextPage">Next</button>
    </div>
    <table class="table table-striped table-responsive">
      <thead>
      <tr>
        <th>
          Thumbnail
        </th>
        <th>
          Streamer
        </th>
        <th>

        </th>
        <th>
          Title
        </th>

      </tr>
      </thead>
      <tbody>
      <tr v-for="clip in items">
        <td>
          <a target="_blank" :href="clip.url"> <img :src="clip.thumbnail_url" class="img-responsive"/></a>
        </td>
        <td>
          {{ clip.broadcaster_name }}
        </td>
        <td>
          <button class="btn btn-primary" @click="Rescan(clip)">Scan Clip</button>
        </td>
        <td>
          {{ clip.title }}
        </td>


      </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import {Options, Vue} from 'vue-class-component';

import {API, TwitchClipLog} from "@/api"; // @ is an alias to /src

@Options({
  components: {},
})


export default class SearchTwitch extends Vue {
  private items: TwitchClipLog[] = [];
  streamerName: string = ""
  clipType: string = "all"
  private interval: number = 0;
  private streamer: string = "";
  private lastpage: { cursor: string } | null = null
  private page: { cursor: string } | null = null
  private page_list: any[] = []
  private clip_id: string = ""
  private broadcaster_id: string = "";
  private game_id: string = "488552";
  private ended_at: string = "";
  private started_at: string = "";
  private game_ids: any

  created() {
 //   this.getGameIds()

  }

  async getGameIds() {
    this.game_ids = await API.get_game_ids()
    console.log(this.game_ids)
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
    await API.remove(clip.id)
    await this.list_items()
  }

  async update_list_items() {
    await API.clips(this.streamer, this.clipType, this.page)
  }

  async Rescan(clip: TwitchClipLog) {
    await API.add_clip(clip.id)
  }

  async PrevPage() {
    if (this.page_list.length > 1) {
      this.page_list.pop()
      const last = this.page_list[this.page_list.length - 1]
      await this.list_items(last.api_result.pagination.cursor)
    }
  }

  async NextPage() {
    if (this.page) {
      await this.list_items(this.page.cursor)
    }
  }

  async list_items(page: string | null = null, before_page: string | null = null) {
    try {
      let slips = this.clip_id.length == 0 ? null : this.clip_id.split('\n').map(a => a.trim());
      let endedAt = this.ended_at.trim().length == 0 ? null : this.ended_at;
      let started_at = this.started_at.trim().length == 0 ? null : this.started_at;
      let broadcaster_id = this.broadcaster_id.trim().length == 0 ? null : this.broadcaster_id;
      let game_id = this.game_id.trim().length == 0 ? null : this.game_id;

      let streamerResponse = await API.search_twitch_clips(broadcaster_id, game_id, slips, endedAt, started_at, page, before_page)
      if (this.items.length > 0) {
        this.page_list.push(streamerResponse)
      }
      this.items = streamerResponse.api_result.data
      this.lastpage = this.page
      this.page = streamerResponse.api_result.pagination
    } catch (e: any) {
      alert(e)
    } finally {
    }
  }

}
</script>
