<template>
  <div class="table-responsive mx-5 mt-5">
    <table class="table mx-5">
      <tbody>
      <tr>
        <th>Title</th>
        <th class="text-center">Source</th>
        <th class="text-center">TS Number</th>
        <th class="text-center">TS Length</th>
      </tr>
      <tr v-for="dataset in datasets" :key="dataset.name">
        <td>
          <RouterLink :to="`/display/${dataset.id}`">{{ dataset.title }}</RouterLink>
        </td>
        <td class="text-center">
          <a :href="dataset.link" target="_blank">
            {{ dataset.source }}
          </a>
        </td>
        <td class="text-center">{{ dataset.timeSeries }}</td>
        <td class="text-center">{{ dataset.timeSeriesLength }}</td>
      </tr>
      </tbody>
      <div style="margin-top:60px;" >
        <label for="fileInput" style="margin-left:-9px;"><i>Upload a dataset : </i></label><br />
        <input type="file" id="fileInput" ref="fileInput" style="width:100px;" >
      </div>
    </table>


  </div>
</template>

<script lang="ts">
import {defineComponent} from 'vue'

export default defineComponent({
  setup() {
    const datasets = [
      {id: 'batch10_eighth', title: 'Drift', source: 'University of California, ChemoSignals', link: 'https://archive.ics.uci.edu/dataset/270/gas+sensor+array+drift+dataset+at+different+concentrations', timeSeries: '100', timeSeriesLength : "1000"},
      {id: 'BAFU_onetwentyeigth', title: 'BAFU', source: 'Swiss Federal Office for the Environment (FOEN)', link: 'https://www.hydrodaten.admin.ch/en', timeSeries: '10', timeSeriesLength : "50000"},
      {id: 'cl2fullLarge_eighth', title: 'Chlorine', source: 'United States Environmental Protection Agency (EPANET)', link: 'https://www.epa.gov/research', timeSeries: '50', timeSeriesLength : "1000"},
      {id: 'climate_eighth', title: 'Climate', source: 'University of South Carolina', link: 'https://viterbi-web.usc.edu/~liu32/data.html', timeSeries: '10', timeSeriesLength : "5000"},
      {id: 'meteo_total_eighth', title: 'Meteo', source: 'Swiss Federal Office of Meteorology and Climatology', link: 'http://meteoswiss.admin.ch', timeSeries: '10', timeSeriesLength : "10000"},
      {id: 'tmp_1', title: 'Electricity', source: 'Elergone, NORTE-07-0202-FEDER-038564', link: 'https://archive.ics.uci.edu/ml/datasets/ElectricityLoadDiagrams20112014', timeSeries: '20', timeSeriesLength : "5000"},
      {id: 'tmp_2', title: 'Air', source: 'National Agency for New Technologies, Energy and Sustainable Economic Development', link: 'https://archive.ics.uci.edu/ml/datasets/Air+Quality', timeSeries: '10', timeSeriesLength : "1000"}
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
