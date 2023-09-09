<template>
  <div class="table-responsive mx-5">
    <table class="table mx-5">
      <tbody>
      <tr>
        <th>Title</th>
        <th class="text-center">Source</th>
        <th class="text-center">Time Series</th>
      </tr>
      <tr v-for="dataset in datasets" :key="dataset.name">
        <td>
          <RouterLink :to="`/compare/${dataset.id}`">{{ dataset.title }}</RouterLink>
        </td>
        <td class="text-center">
          <a :href="dataset.link" target="_blank">
            {{ dataset.source }}
          </a>
        </td>
        <td class="text-center">{{ dataset.timeSeries }}</td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import {defineComponent} from 'vue'

export default defineComponent({
  setup() {
    const datasets = [
      {id: 'BAFU_onetwentyeigth', title: 'BAFU', source: 'Swiss Federal Office for the Environment (FOEN)', link: 'https://www.hydrodaten.admin.ch/en', timeSeries: '10'},
      {id: 'cl2fullLarge_eighth', title: 'Chlorine', source: 'United States Environmental Protection Agency (EPANET)', link: 'https://www.epa.gov/research', timeSeries: '10'},
      {id: 'climate_eighth', title: 'Climate', source: 'University of South Carolina', link: 'https://viterbi-web.usc.edu/~liu32/data.html', timeSeries: '10'},
      {id: 'batch10_eighth', title: 'Drift', source: 'University of California, ChemoSignals', link: 'https://archive.ics.uci.edu/dataset/270/gas+sensor+array+drift+dataset+at+different+concentrations', timeSeries: '10'},
      {id: 'meteo_total_eighth', title: 'Meteo', source: 'Swiss Federal Office of Meteorology and Climatology', link: 'http://meteoswiss.admin.ch', timeSeries: '4',}
    ]
    return {
      datasets
    }
  }
})
</script>
<style>
.table-responsive {
  overflow-x: hidden;
  max-width: 100%;
}
</style>
