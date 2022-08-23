<template>
  <div class="home">
    <div class="btn-group-justified">
      <button class="btn btn-info" @click="PrevPage">Previous</button>
      {{ page }}
      <button class="btn btn-info" @click="NextPage">Next</button>
    </div>
    <label for="streamer_name"> Search Streamer
      <input class="text-info" id="streamer_name" type="text" v-model="streamerName">

    </label>
    <label for="clip_type"> Search Type
      <input class="text-info" id="clip_type" type="text" v-model="clipType">

    </label>
    <button @click="Search()" class="btn btn-block">Search</button>
    <button class="btn btn-danger" @click="Tag_and_bag_selected()">Tag and Bag Selected</button>
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
          ClipType
        </th>
        <th>
          Title
        </th>
        <th>
          Tags
        </th>
        <th></th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="clip in items">
        <td>
          <a target="_blank" :href="clip.video_url"> <img :src="clip.thumbnail_url" class="img-responsive"/></a>
        </td>
        <td>
          {{ clip.broadcaster_name }}
        </td>
        <td>
          {{ clip.type }}
        </td>
        <td>
          {{ clip.title }}
        </td>
        <td>
          {{ clip.tag_string }}
        </td>
        <td>
          <b-checkbox :checked="is_clip_selected(clip)" @input="toggle_clip_selected(clip)"></b-checkbox>
          <button class="btn btn-danger" @click="tag_and_bag(clip)">Tag and Bag</button>
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import HelloWorld from '@/components/HelloWorld.vue';
import {
    API,

  StreamerMonitorState,
  TwitchClipLog
} from "@/api"; // @ is an alias to /src

@Options({
  components: {
    HelloWorld,
  },
})
export default class ClipView extends Vue {
  private items: TwitchClipLog[] = [];
  streamerName: string = ""
  clipType: string = "all"
  private interval: number = 0;
  private streamer: string = "";
  private page: number = 1
  private selected_clips: { [code: number]: boolean } = {}

  is_clip_selected(clip: TwitchClipLog) {
    return this.selected_clips[clip.id]
  }

  toggle_clip_selected(clip: TwitchClipLog) {
    this.selected_clips[clip.id] = !this.selected_clips[clip.id]
  }

  tag_and_bag(clip: TwitchClipLog) {

  }

  created() {
    if (this.$route.params.streamerName)
      this.streamer = this.$route.params.streamerName as string;
    else
      this.streamer = ""
    this.list_items()

  }

  onUnmounted() {
    clearInterval(this.interval)
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
    if (this.streamer.length > 0)
      streamerResponse = await API.clips(this.streamer, this.clipType, this.page);
    else
      streamerResponse = await API.all_clips(this.clipType, this.page);
    this.items = streamerResponse.items
  }

}
</script>
