<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">

    <router-link class="navbar-brand" to="/">
      <img v-if="hasRole('admin')" :src="profileImage()" width="30" height="30" class="d-inline-block align-top"
           alt="">
      {{ displayName }}
    </router-link>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav"
            aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav">
        <li class="nav-item  ">

          <router-link class="nav-link" to="/">Home <span class="sr-only">(current)</span></router-link>
        </li>

        <li class="nav-item">
          <router-link class="nav-link" to="/clips_viewer">scanned clips</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/search_twitch">Twitch search</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/list_scan_jobs">scanners</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/ListClipsMade/">clips</router-link>
        </li>
        <li class="nav-item" v-if="!hasRole('admin')">
          <a class="nav-link" href="/login">login</a>
        </li>
        <li class="nav-item" v-else>
          <a class="nav-link" href="/logout">logout</a>
        </li>
      </ul>
    </div>
  </nav>

  <div class="container-fluid">
    <router-view/>
  </div>
</template>
<script lang="ts">

import {Component, Vue} from "vue-facing-decorator";
import {DisplayName, HasRole, IsLoggedIn, ProfileImage} from "@/views/has_role";


@Component({
  components: {},
})
export default class AppView extends Vue {
  profileImage() {
    return ProfileImage()
  }

  Login() {
    //@ts-ignore
    window.location = '/login'
  }

  Logout() {
    //@ts-ignore
    window.location = '/login'
  }



  hasRole(role: string) {
    return HasRole(role)
  }

  get displayName() {

    return DisplayName()
  }
}
</script>
