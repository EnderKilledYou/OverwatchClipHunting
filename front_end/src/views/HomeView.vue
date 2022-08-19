<template>

  <div>
    <div class="col-md-12">
      <div class="col-md-4">
        <label for="streamer_name"> Add Streamer
          <input class="text-info" id="streamer_name" type="text" v-model="streamerName">
          <button @click="Watch()" class="btn btn-block">Add</button>
        </label>
      </div>
      <div class="row">
        <div class="btn-group-justified">

          <button @click="Twitch()" class="btn btn-block" v-show="twitch_streams.length ===0">Look at Twitch
          </button>
          <button @click="HideTwitch()" class="btn btn-block" v-show="twitch_streams.length !==0">Hide</button>
          <button @click="ToggleInactiveSetting()" class="btn btn-block" v-if="showInactive">Hide Inactive</button>
          <button @click="ToggleInactiveSetting()" class="btn btn-block" v-if="!showInactive">Show Inactive</button>

        </div>
      </div>
    </div>
    <div class="row">
      <on-twitch-now :streams="twitch_streams_filtered"
                     @updatedmonitored="list_items"/>
    </div>
    <div class="row">
      <currently-live :items="items"
                      :show_inactive="showInactive" @updatedmonitored="list_items"/>
    </div>

  </div>

</template>

<script lang="ts">
import Monitor, {API, StreamerMonitorState, TwitchLiveStreamData} from "@/api";
import OnTwitchNow from "@/views/OnTwitchNow.vue";
import CurrentlyLive from "@/views/CurrentlyLive.vue"; // @ is an alias to /src

let interval: number | null | undefined = null


import {Component, Prop, Vue} from "vue-facing-decorator";

@Component({
  components: {
    CurrentlyLive,
    OnTwitchNow,

  },
})
export default class HomeView extends Vue {

  streamerName: string = ""


  showTwitchers: boolean = false

  private interval: number = 0;
  private twitch_streams: any[] = [];


  async HideTwitch() {
    this.twitch_streams = []
    this.showTwitchers = false
  }

  async Twitch() {
    this.twitch_streams = await API.get_live_streamers()
    this.showTwitchers = true
  }

  async AutoTwitch() {
    await API.start_farm_twitch()

  }

  async StopAutoTwitch() {
    await API.stop_farm_twitch()

  }

  showInactive = false

  ToggleInactiveSetting() {
    this.showInactive = !this.showInactive
  }

  get twitch_streams_filtered() {
    if (!this.twitch_streams) return []
    let filter = this.twitch_streams.filter(a => {
      if (!this.items) return []
      return !this.items[0].find(b => b.broadcaster.toLowerCase() === a.user_name.toLowerCase())
    });
    if (!this.showInactive) {
      return filter.filter(this.RowHasExtraData.bind(this))
    }
    return filter
  }

  RowHasExtraData(watcher: Monitor) {

  }

  created() {

    this.list_items()
    if (interval)
      clearInterval(interval)
    interval = setInterval(this.list_items.bind(this), 35000)
  }


  async Watch2(streamerName: string) {
    const streamerResponse = await API.add(streamerName)
    this.list_items()
  }

  async Watch() {
    const streamerResponse = await API.add(this.streamerName)
    this.list_items()
  }

  items?: [Monitor[], TwitchLiveStreamData[]]

  async list_items() {

    const streamerResponse = await API.list_streamers()
    this.items = streamerResponse.items

  }

}
</script>
