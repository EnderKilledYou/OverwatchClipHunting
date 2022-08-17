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
          <button @click="AutoTwitch()" class="btn btn-block">Auto Twitch</button>
          <button @click="StopAutoTwitch()" class="btn btn-block">Stop Auto Twitch</button>
        </div>
      </div>
    </div>
    <div class="row">
      <on-twitch-now v-if="showTwitchers" :streams="twitch_streams_filtered"
                     @updatedmonitored="list_items"/>
    </div>
    <div class="row">
      <currently-live :items="streamerMonitorStates"
                      @updatedmonitored="list_items"/>
    </div>

  </div>

</template>

<script lang="ts">
import {API, StreamerMonitorState} from "@/api";
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
  streamerMonitorStates: StreamerMonitorState[] = [];
  streamerName: string = ""


  get showTwitchers() {
    return this.twitch_streams && this.twitch_streams.length > 0
  }

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
      return !this.streamerMonitorStates.find(b => b.name.toLowerCase() === a.user_name.toLowerCase())
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
    this.list_items()
  }

  async Watch() {
    const streamerResponse = await API.add(this.streamerName)
    this.list_items()
  }


  async list_items() {
    debugger
    const streamerResponse = await API.list()
    this.streamerMonitorStates = streamerResponse.items.map((a: any) => new StreamerMonitorState(a))
  }

}
</script>
