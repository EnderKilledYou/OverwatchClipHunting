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
    <label for="clip_type"> Search by clip id
      <input class="text-info" id="clip_id" type="text" v-model="clip_id">

    </label>

    <button @click="Search()" class="btn btn-block">Search</button>
    <table class="table table-striped table-responsive">
      <thead>
      <tr>
        <th>
          Id
        </th>
        <th>
          Clip Id
        </th>
        <th>
          State
        </th>
        <th>
          Created At
        </th>
        <th>
          Error
        </th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="scan_job in items">
        <td>

          {{ scan_job.id }}
        </td>
        <td>
          {{ scan_job.clip_id }}
        </td>
        <td>
          {{ scan_job.state }}
        </td>
        <td>
          {{ scan_job.created_at }}
        </td>

        <td>
          {{ scan_job.error }}
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import {Options, Vue} from 'vue-class-component';

import {
   API,

  StreamerMonitorState,
  TwitchClipLog, TwitchClipTag
} from "@/api"; // @ is an alias to /src

@Options({
  components: {

  },
})
export default class ClipView extends Vue {

  private tags: TwitchClipTag[] = []


  created() {



  }

  async get_item() {

  }

}
</script>
