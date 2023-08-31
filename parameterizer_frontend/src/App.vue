<template>
  <header>

    <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top">
      <a class="navbar-brand ps-3" href="/">
        <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="30" height="30">
        <span class="ml-2">ImputeVIS</span>
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-target="#navbarNav"
              aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse justify-content-center ps-n3 ms-n3" id="navbarNav">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item active">
            <RouterLink class="nav-link" to="/">Compare</RouterLink>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown"
               aria-haspopup="true" aria-expanded="false">
              Algorithms
            </a>
            <div class="dropdown-menu" aria-labelledby="navbarDropdown">
              <RouterLink class="dropdown-item" to="/algorithms/cdrec">CDRec</RouterLink>
              <RouterLink class="dropdown-item" to="/algorithms/iim">IIM</RouterLink>
              <RouterLink class="dropdown-item" to="/algorithms/m-rnn">M-RNN</RouterLink>
              <RouterLink class="dropdown-item" to="/algorithms/stmvl">ST-MVL</RouterLink>
            </div>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown-optimization" role="button"
               data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Algorithm Optimization
            </a>
            <div class="dropdown-menu" aria-labelledby="navbarDropdown-optimization">
              <RouterLink class="dropdown-item" to="/optimization/cdrec">CDRec</RouterLink>
              <RouterLink class="dropdown-item" to="/optimization/iim">IIM</RouterLink>
              <RouterLink class="dropdown-item" to="/optimization/mrnn">M-RNN</RouterLink>
              <RouterLink class="dropdown-item" to="/optimization/stmvl">ST-MVL</RouterLink>
            </div>
          </li>
          <!-- Add additional links here -->
          <li class="nav-item">
            <RouterLink class="nav-link" to="/datasets/categorizer">Dataset Categorizer</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/about">About</RouterLink>
          </li>
        </ul>
      </div>
    </nav>
  </header>

  <div class="content pt-5 mt-3 flex-grow-1">
    <RouterView/>
  </div>
  <Footer/>
</template>


<script setup lang="ts">
import {RouterLink, RouterView} from 'vue-router'
import Footer from './components/Footer.vue';

</script>

<style scoped>
</style>