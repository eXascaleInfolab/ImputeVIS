<template>
  <header>

    <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top">
      <a class="navbar-brand ps-3" href="/">
        <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="30" height="30">
        <span class="ml-2">ImputeVIS</span>
      </a>
      <div class= "navbar-collapse justify-content-center ps-n3 ms-n3" id="navbarNav">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item dropdown text-center me-2">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown-comparison" role="button"
               data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Datasets
            </a>
            <div class="dropdown-menu" aria-labelledby="navbarDropdown-comparison-select">
              <RouterLink class="dropdown-item" to="/display">Display</RouterLink>
              <RouterLink class="dropdown-item" to="/contamination">Contaminate</RouterLink>
              <RouterLink class="dropdown-item" to="/feature_extraction">Feature Extraction</RouterLink>
            </div>
          </li>


          <li class="nav-item dropdown text-center me-2">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown-optimization" role="button" data-bs-toggle="dropdown"
               aria-haspopup="true" aria-expanded="false">
              Imputation
            </a>
            <div class="dropdown-menu" aria-labelledby="navbarDropdown-optimization-select">
              <RouterLink class="dropdown-item" to="/imputation">Impute</RouterLink>
              <RouterLink class="dropdown-item" to="/auto_optimizer">Auto-ML Opt.</RouterLink>
              <RouterLink class="dropdown-item" to="/user_optimizer">User-defined Opt.</RouterLink>
            </div>
          </li>

          <li class="nav-item dropdown text-center me-2">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown-optimization" role="button" data-bs-toggle="dropdown"
               aria-haspopup="true" aria-expanded="false">
              Explanation
            </a>
            <div class="dropdown-menu" aria-labelledby="navbarDropdown-optimization-select">
              <RouterLink class="dropdown-item" to="/explainers">Explainer</RouterLink>
            </div>
          </li>

          <!--
          <li class="nav-item dropdown text-center me-2">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown-algorithm" role="button"
               data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              OLD
            </a>
            <div class="dropdown-menu" aria-labelledby="navbarDropdown-algorithm-select">
              <RouterLink class="dropdown-item" to="/compare">OLD :Select Datasets</RouterLink>
              <RouterLink class="dropdown-item" to="/optimization/cdrec">OLD : OPTI CDRec</RouterLink>
              <RouterLink class="dropdown-item" to="/algorithms/cdrec">OLD : ALGO CDRec</RouterLink>
              <RouterLink class="dropdown-item" to="/datasets/categorizer">OLD : FE - Select Datasets</RouterLink>
            </div>
          </li>
          -->


          <li class="nav-item ms-1 text-center">
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