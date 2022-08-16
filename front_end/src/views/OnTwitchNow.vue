<template>
  <table class="table table-striped table-responsive" >

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
    <tr v-for="watcher in streams">
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
</template>
<script lang="ts">
import {API} from "@/api";
import {Options, Vue} from "vue-class-component";


@Options({
  props: ['streams'],
  emits: ['updatedmonitored'],


  components: {},
})
export default class HomeView extends Vue {


  async Watch2(streamerName: string) {
    debugger
    const streamerResponse = await API.add(streamerName)
    this.$emit('updatedmonitored')
  }
}
</script>