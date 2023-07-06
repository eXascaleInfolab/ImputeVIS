<template>
  <header>

    <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top">
      <a class="navbar-brand" href="#">
        <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="30" height="30">
        <span class="ml-2">Parameterizer</span>
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-target="#navbarNav"
        aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item active">
            <RouterLink class="nav-link" to="/">Compare</RouterLink>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Algorithms
            </a>
            <div class="dropdown-menu" aria-labelledby="navbarDropdown">
              <RouterLink class="dropdown-item" to="/algorithms/cdrec">CDRec (WIP)</RouterLink>
              <RouterLink class="dropdown-item" to="/algorithms/iim">IIM (WIP)</RouterLink>
              <RouterLink class="dropdown-item" to="/algorithms/m-rnn">M-RNN (WIP)</RouterLink>
              <RouterLink class="dropdown-item" to="/algorithms/stmvl">STMVL (WIP)</RouterLink>
            </div>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown-data" role="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Datasets
            </a>
            <div class="dropdown-menu" aria-labelledby="navbarDropdown-data">
              <RouterLink class="dropdown-item" to="/datasets/bafu">BAFU TODO</RouterLink>
              <RouterLink class="dropdown-item" to="/datasets/chlorine">Chlorine TODO</RouterLink>
              <RouterLink class="dropdown-item" to="/datasets/climate">Climate TODO</RouterLink>
              <RouterLink class="dropdown-item" to="/datasets/drift">Drift TODO</RouterLink>
              <RouterLink class="dropdown-item" to="/datasets/electricity">Electricity TODO</RouterLink>
              <RouterLink class="dropdown-item" to="/datasets/meteo">Meteo TODO</RouterLink>
            </div>
          </li>
          <!-- Add your additional links here -->
          <li class="nav-item">
            <RouterLink class="nav-link" to="/about">About</RouterLink>
          </li>
        </ul>
      </div>
    </nav>
  </header>

  <div class="content pt-5 mt-2 flex-grow-1">
    <RouterView />
  </div>
  <Footer />
</template>


<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import Footer from './components/Footer.vue';

</script>

<style scoped>
.content {
  padding-top: 70px; /* Adjust this value depending on the height of your navbar */
}
</style>