<template>
  <div class="d-flex mb-auto container mt-5">
    <div class="col-lg-8">
      <div v-if="loading" class="mt-3">
        Loading...
      </div>

      <div v-else-if="error" class="mt-3 alert alert-danger">
        {{ error }}
      </div>

      <div v-else class="mt-3">
        <table v-if="loadedResults" class="table">
          <thead>
          <tr>
            <th>Feature Name</th>
            <th>Value</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="(value, key) in features" :key="key">
            <td>{{ key }}</td>
            <td>{{ value }}</td>
          </tr>
          </tbody>
        </table>
      </div>
      <highcharts :options="chartOptionsOriginal"></highcharts>
    </div>
    <div class="col-lg-4">
      <div class="sidebar col-lg-5">
        <data-select v-model="dataSelect"/>
        <button type="submit" class="btn btn-primary mt-5" @click="fetchDataFeatures">Get Features</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, watch, computed} from 'vue';
import DataSelect from '../components/DataSelect.vue';
import MetricsDisplay from '../components/MetricsDisplay.vue';
import MissingRate from '../components/MissingRate.vue';
import axios from 'axios';
import {Chart} from 'highcharts-vue'
import Highcharts from 'highcharts'
import HC_exporting from 'highcharts/modules/exporting'
import HC_exportData from 'highcharts/modules/export-data'
import HighchartsBoost from 'highcharts/modules/boost'
import {createSeries, generateChartOptions} from "@/views/thesisUtils/utils";

// Initialize exporting modules
HC_exporting(Highcharts)
HC_exportData(Highcharts)
HighchartsBoost(Highcharts)

export default {
  components: {
    DataSelect,
    highcharts: Chart,
    MetricsDisplay,
    MissingRate
  }, setup() {
    const dataSelect = ref('BAFU_quarter');
    const features = ref<Record<string, number>>({});
    const loading = ref(false)
    const error = ref("");
    const loadedResults = ref(false);
    const chartOptionsOriginal = ref(generateChartOptions('Data', 'Data'));

    const fetchData = async () => {
      try {
        let dataSet = `${dataSelect.value}_obfuscated_0`;
        const response = await axios.post('http://localhost:8000/api/fetchData/',
            {
              data_set: dataSet

            },
            {
              headers: {
                'Content-Type': 'application/text',
              }
            }
        );
        chartOptionsOriginal.value.series.splice(0, chartOptionsOriginal.value.series.length);

        response.data.matrix.forEach((data: number[], index: number) => {
          // Replace NaN with 0
          const cleanData = data.map(value => isNaN(value) ? 0 : value);
          chartOptionsOriginal.value.series[index] = createSeries(index, cleanData);
        });
      } catch (error) {
        console.error(error);
      }
    }

    const fetchDataFeatures = async () => {
      loading.value = true;
      error.value = "";
      loadedResults.value = false;
      try {
        let dataSet = `${dataSelect.value}_obfuscated_0`;
        const response = await axios.post('http://localhost:8000/api/categorizeData/',
            {
              data_set: dataSet

            },
            {
              headers: {
                'Content-Type': 'application/text',
              }
            }
        );
        features.value = response.data;
        // features.value = await response.json();
        loadedResults.value = true;

      } catch (error) {
        error.value = `Error: ${error.message}`;
        console.error(error);
      } finally {
        loading.value = false;
      }
    }

    // Define a new function that calls fetchData
    const handleDataSelectChange = () => {
      fetchData();
    }
    watch(dataSelect, fetchData, {immediate: true});

    return {
      dataSelect,
      features,
      loading,
      error,
      loadedResults,
      fetchDataFeatures,
      chartOptionsOriginal
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px; /* Change this value to increase or decrease the margin */
}
</style>
