<template>
  <div class="home">
    <label for="streamer_name"> Add Streamer
      <input class="text-info" id="streamer_name" type="text" v-model="streamerName">
      <button @click="Watch()" class="btn btn-block">Add</button>
      <button @click="Twitch()" class="btn btn-block" v-show="twitch_streams_filtered.length ===0">Look at Twitch
      </button>
      <button @click="HideTwitch()" class="btn btn-block" v-show="twitch_streams_filtered.length !==0">Hide</button>
      <button @click="AutoTwitch()" class="btn btn-block">Auto Twitch</button>
      <button @click="StopAutoTwitch()" class="btn btn-block">Stop Auto Twitch</button>
    </label>
    <table class="table table-striped table-responsive" v-if="twitch_streams_filtered.length >0">
      <thead>
      <tr>
        <th>
          Started At
        </th>
        <th>

        </th>

      </tr>
      </thead>
      <tbody>
      <tr v-for="watcher in twitch_streams_filtered">
        <td>
          <figure class="figure">
            <a target="_blank" :href="`https://twitch.tv/` +watcher.video_id"> <img
                :src="watcher.thumbnail_url.replace('{width}','100').replace('{height}','100')"
                class="  img-responsive"/></a>

            <figcaption> {{ watcher.user_name }}</figcaption>
            <figcaption> {{ watcher.started_at }}</figcaption>
          </figure>
        </td>
        <td>
          <button class="btn btn-danger" @click="Watch2( watcher.user_name)">Watch</button>
        </td>
      </tr>
      </tbody>
    </table>
    <div class="row row-cols-3 row-cols-md-4 g-4">
      <div class="col" v-for="watcher in items" :key="watcher.name">
        <div class="card">
          <img class="card-img-top"
               :src="watcher.data.thumbnail_url.replace('{width}','300').replace('{height}','300')"/>

          <div class="card-body">
            <h5 class="card-title"><a target="_blank" :href="`https://twitch.tv/` + watcher.name">{{
                watcher.name
              }}</a></h5>
            <p class="card-text"> {{ watcher.frames_done }} / {{ watcher.frames_read }} ( {{ watcher.seconds }} s) </p>

          </div>
          <div class="card-footer">

            <button class="btn btn-danger" @click="Unwatch(watcher)">Stop</button>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import HelloWorld from '@/components/HelloWorld.vue';
import {add_streamer, list_streamer, remove_streamer, StreamerMonitorState, API} from "@/api"; // @ is an alias to /src

let interval: number | null | undefined = null

@Options({
  components: {
    HelloWorld,
  },
})
export default class HomeView extends Vue {
  private items: StreamerMonitorState[] = [];
  streamerName: string = ""
  private interval: number = 0;
  private twitch_streams: any[] = [];

  async HideTwitch() {
    this.twitch_streams = []
  }

  async Twitch() {
    this.twitch_streams = await API.get_live_streamers()
  }

  async AutoTwitch() {
    await API.start_farm_twitch()

  }

  async StopAutoTwitch() {
    await API.stop_farm_twitch()

  }

  get twitch_streams_filtered() {
    if (!this.twitch_streams) return []
    return this.twitch_streams.filter(a => {
      return !this.items.find(b => b.name.toLowerCase() === a.user_name.toLowerCase())
    })
  }

  created() {
    this.list_items()
    if (interval)
      clearInterval(interval)
    interval = setInterval(this.list_items.bind(this), 5000)
  }


  async Watch2(streamerName: string) {
    const streamerResponse = await API.add(streamerName)
    this.items = streamerResponse.items
  }

  async Watch() {
    const streamerResponse = await API.add(this.streamerName)
    this.items = streamerResponse.items
  }

  async Unwatch(watcher: StreamerMonitorState) {
    const streamerResponse = await API.remove(watcher.name)

    this.items = streamerResponse.items
  }

  async list_items() {

    const streamerResponse = await API.list()
    this.items = streamerResponse.items
  }

}
</script>
