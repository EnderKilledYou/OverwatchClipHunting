<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">

    <a class="navbar-brand" href="#/">Clip Hunta</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav"
            aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav">
        <li class="nav-item active">

          <router-link class="nav-link" to="/">Home <span class="sr-only">(current)</span></router-link>
        </li>

        <li class="nav-item">
          <router-link class="nav-link" to="/clips_viewer">clips viewer</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/search_twitch/">search</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/list_scan_jobs/">scanners</router-link>
        </li>

      </ul>
    </div>
  </nav>


  <router-view/>
</template>
