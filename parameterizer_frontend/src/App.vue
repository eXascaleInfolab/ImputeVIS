<template>
  <header>
    <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top">
      <a class="navbar-brand" href="#">
        <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="30" height="30">
        <span class="ml-2">Parameterizer</span>
      </a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav"
        aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item active">
            <RouterLink class="nav-link" to="/">Home</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/about">About</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/algorithms/iim">IIM</RouterLink>
          </li>
          <!-- Add your additional links here -->
          <li class="nav-item">
            <RouterLink class="nav-link" to="/dummy1">Dummy Link 1</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/dummy2">Dummy Link 2</RouterLink>
          </li>
        </ul>
<!--        <form class="form-inline my-2 my-lg-0">-->
<!--          <input class="form-control mr-sm-2" type="search" placeholder="Search" aria-label="Search">-->
<!--          <button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>-->
<!--        </form>-->
      </div>
    </nav>

<!--    <div class="wrapper">
      <HelloWorld msg="You did it!" />
    </div>-->
  </header>


  <div class="content pt-5">
    <RouterView />
  </div>
  <Footer />
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
// import HelloWorld from './components/HelloWorld.vue'
import Footer from './components/Footer.vue';

</script>

<style scoped>
.content {
  padding-top: 70px; /* Adjust this value depending on the height of your navbar */
}
</style>