<template>
  <h1 class="mb-4 text-center">STMVL Detail</h1>
  <div class="d-flex mb-auto">
    <div class="col-lg-8">
      <metrics-display :metrics="metrics"></metrics-display>
      <highcharts v-if="imputedData" :options="chartOptionsImputed"></highcharts>
      <highcharts :options="chartOptionsOriginal"></highcharts>
    </div>
    <div class="col-lg-4">
      <form @submit.prevent="submitForm" class="sidebar col-lg-5">
        <data-select v-model="dataSelect" />
        <missing-rate v-model="missingRate" />
        <!--Window Size-->
        <div class="mb-3">
          <label for="windowSize" class="form-label">Window Size: {{ windowSize }}</label>
          <input id="windowSize" v-model.number="windowSize" type="range" min="2" max="100" step="1" class="form-control">
        </div>

        <!--Smoothing Parameter Gamma-->
        <div class="mb-3">
          <label for="gamma" class="form-label">Smoothing Parameter Gamma: {{ gamma }}</label>
          <input id="gamma" v-model.number="gamma" type="range" min="0.05" max="0.99" step="0.05" class="form-control">
        </div>

        <!-- Power for Spatial Weight (Alpha) -->
        <div class="mb-3">
          <label for="alpha" class="form-label">Power for Spatial Weight (alpha): {{ alpha }}</label>
          <input id="alpha" v-model.number="alpha" type="range" min="0.5" max="20" step="0.5" class="form-control">
        </div>

        <button type="submit" class="btn btn-primary">Impute</button>
      </form>
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
  },
  setup() {
    const dataSelect = ref('BAFU_quarter') // Default data is BAFU
    const missingRate = ref('1'); // Default missing rate is 1%
    const windowSize = ref('2'); // Default window size is 2
    const gamma = ref('0.5') // Default smoothing parameter gamma is 0.5, min 0.0, max 1.0
    const alpha = ref('2') // Default power for spatial weight (alpha) is 2, must be larger than 0.0
    const imputedData = ref(false); // Whether imputation has been carried out
    const rmse = ref(null);
    const mae = ref(null);
    const mi = ref(null);
    const corr = ref(null);

    const metrics = computed(() => ({ rmse: rmse.value, mae: mae.value, mi: mi.value, corr: corr.value }));

    const fetchData = async () => {
      try {
        let dataSet = `${dataSelect.value}_obfuscated_0`;
        const response = await axios.post('http://localhost:8000/api/fetchData/',
          {
            data_set: dataSet

          },
          {
            headers: {
              'Content-Type': 'application/json',
            }
          }
        );
        chartOptionsOriginal.value.series.splice(0, chartOptionsOriginal.value.series.length);
        response.data.matrix.forEach((data: number[], index: number) => {
          chartOptionsOriginal.value.series[index] = createSeries(index, data);
        });
      } catch(error) {
        console.error(error);
      }
    }

    const submitForm = async () => {
      try {
        let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
        console.log(dataSet);
        const response = await axios.post('http://localhost:8000/api/stmvl/',
            {
              data_set: dataSet,
              window_size: windowSize.value,
              gamma: gamma.value,
              alpha: alpha.value,
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
        );
        rmse.value = response.data.rmse.toFixed(3);
        mae.value = response.data.mae.toFixed(3);
        mi.value = response.data.mi.toFixed(3);
        corr.value = response.data.corr.toFixed(3);
        chartOptionsImputed.value.series.splice(0, chartOptionsImputed.value.series.length);
        response.data.matrix_imputed.forEach((data: number[], index: number) => {
          chartOptionsImputed.value.series[index] = createSeries(index, data);
        });
        imputedData.value = true;
      } catch (error) {
        console.error(error);
      }
    }
    const chartOptionsOriginal = ref(generateChartOptions('Original Data', 'Data'));
    const chartOptionsImputed = ref(generateChartOptions('Imputed Data', 'Data'));

    // Define a new function that calls fetchData
    const handleDataSelectChange = () => {
      fetchData();
    }

    // Watch for changes and call fetchData when it changes
    watch(dataSelect, handleDataSelectChange, { immediate: true });
    // TODO Missingness display
    // watch(missingRate, fetchData, { immediate: true });

    return {
      submitForm,
      metrics,
      chartOptionsOriginal,
      chartOptionsImputed,
      dataSelect,
      windowSize,
      gamma,
      alpha,
      missingRate,
      imputedData
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px;  /* Change this value to increase or decrease the margin */
}
</style>