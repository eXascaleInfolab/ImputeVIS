<template>
  <h3 class="mb-4 text-center">CDRec Detail</h3>
  <div v-if="loadingResults" class="d-flex justify-content-center mt-3">
    <div class="alert alert-info d-flex align-items-center">
      <div class="spinner-border text-primary me-3" role="status"></div>
      Determining resulting imputation...
    </div>
  </div>
  <div class="d-flex mb-auto">
    <div class="col-lg-8">
      <highcharts class="mb-5" v-if="imputedData" :options="chartOptionsImputed"></highcharts>
      <highcharts :options="chartOptionsOriginal"></highcharts>
    </div>
    <div class="col-lg-4">
      <form @submit.prevent="submitForm" class="sidebar col-lg-5">
        <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames"/>
        <missing-rate v-model="missingRate"/>
        <!-- Learning Rate -->
        <div class="mb-3">
          <!-- TODO: Add mouseover for truncation rank -->
          <label for="truncationRank" class="form-label">Truncation Rank: {{ truncationRank }}</label>
          <input id="truncationRank" v-model.number="truncationRank" type="range" min="0" max="10" step="1"
                 class="form-control">
        </div>

        <!-- Sequence Length -->
        <div class="mb-3">
          <label for="epsilon" class="form-label">Threshold for Difference: {{ epsilon }}</label>
          <select id="epsilon" v-model="epsilon" class="form-control">
            <option value="E-9">E-9</option>
            <option value="E-8">E-8</option>
            <option value="E-7">E-7</option>
            <option value="E-6">E-6</option>
            <option value="E-5">E-5</option>
            <option value="E-4">E-4</option>
            <option value="E-3">E-3</option>
          </select>
        </div>

        <!-- Number of Iterations -->
        <div class="mb-3" data-toggle="tooltip" data-placement="top" title="Also impacts run-time proportionally.">
          <label for="iterations" class="form-label">Number of Iterations: {{ iterations }}</label>
          <input id="iterations" v-model.number="iterations" type="range" min="100" max="2000" step="100"
                 class="form-control">
        </div>

        <button type="submit" class="btn btn-primary">Impute</button>
        <div class="mt-3">
          <metrics-display :metrics="metrics"></metrics-display>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, watch, computed, nextTick} from 'vue';
import DataSelect from '../components/DataSelect.vue';
import MetricsDisplay from '../components/MetricsDisplay.vue';
import MissingRate from '../components/MissingRate.vue';
import axios from 'axios';
import {Chart} from 'highcharts-vue'
import Highcharts from 'highcharts'
import HC_exporting from 'highcharts/modules/exporting'
import HC_exportData from 'highcharts/modules/export-data'
import HighchartsBoost from 'highcharts/modules/boost'
import {
  createSeries,
  createSegmentedSeries,
  generateChartOptions,
  generateChartOptionsLarge
} from "@/views/thesisUtils/utils";

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
    const dataSelect = ref('climate_eighth') // Default data
    const currentSeriesNames = ref([]); // Names of series currently displayed
    const missingRate = ref('1'); // Default missing rate is 1%
    const truncationRank = ref('1') // Default truncation rank is 1, 0 means detect truncation automatically
    const epsilon = ref('E-7'); // Default epsilon is E-7
    const iterations = ref(500); // Default number of iterations is 1000
    const imputedData = ref(false); // Whether imputation has been carried out
    const rmse = ref(null);
    const mae = ref(null);
    const mi = ref(null);
    const corr = ref(null);

    let obfuscatedMatrix = [];
    let loadingResults = ref(false);
    const metrics = computed(() => ({rmse: rmse.value, mae: mae.value, mi: mi.value, corr: corr.value}));

    const fetchData = async () => {
      try {
        imputedData.value = false;
        let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
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

        obfuscatedMatrix = response.data.matrix;
        response.data.matrix.forEach((data: number[], index: number) => {
          // Replace NaN with 0
          const cleanData = data.map(value => isNaN(value) ? 0 : value);
          if (currentSeriesNames.value.length > 0) {
            chartOptionsOriginal.value.series[index] = createSeries(index, cleanData, currentSeriesNames.value[index]);
          } else {
            chartOptionsOriginal.value.series[index] = createSeries(index, cleanData);
          }
        });
      } catch (error) {
        console.error(error);
      }
    }

    const submitForm = async () => {
      try {
        loadingResults.value = true;
        imputedData.value = false;
        let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
        const response = await axios.post('http://localhost:8000/api/cdrec/', {
          data_set: dataSet,
          truncation_rank: truncationRank.value,
          epsilon: epsilon.value,
          iterations: iterations.value,
        }, {
          headers: {
            'Content-Type': 'application/json',
          }
        });

        rmse.value = response.data.rmse.toFixed(3);
        mae.value = response.data.mae.toFixed(3);
        mi.value = response.data.mi.toFixed(3);
        corr.value = response.data.corr.toFixed(3);

        // Create a new array for the new series data
        const newSeriesData = [];
        // Deeply clear the old series
        deepClear(chartOptionsImputed.value.series);

        response.data.matrix_imputed.forEach((data: number[], index: number) => {
          if (currentSeriesNames.value.length > 0) {
            const segmentedSeries = createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value, currentSeriesNames.value[index]);
            newSeriesData.push(...segmentedSeries);
          } else {
            newSeriesData.push(createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value));
          }
        });

        // Deep clone the chart options and update the series
        const newChartOptions = JSON.parse(JSON.stringify(chartOptionsImputed.value));
        newChartOptions.series = newSeriesData;
        chartOptionsImputed.value = newChartOptions;
        // after updating reactive property...
        // await nextTick();
        // console.log("updated");
        imputedData.value = true;
      } catch (error) {
        console.error(error);
      } finally {
        loadingResults.value = false;
      }
    }

    const chartOptionsOriginal = ref(generateChartOptions('Original Data', 'Data'));
    const chartOptionsImputed = ref(generateChartOptionsLarge('Imputed Data', 'Data'));

    function deepClear(obj: any): void {
    if (Array.isArray(obj)) {
        for (let i = 0; i < obj.length; i++) {
            deepClear(obj[i]);
            obj[i] = null;
        }
        obj.length = 0;
    } else if (typeof obj === 'object' && obj !== null) {
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                deepClear(obj[key]);
                obj[key] = null;
            }
        }
    }
}

    // Define a new function that calls fetchData
    const handleDataSelectChange = () => {
      fetchData();
    }

    const updateSeriesNames = (newSeriesNames) => {
      currentSeriesNames.value = newSeriesNames;
    };
    // Watch for changes and call fetchData when it changes
    watch(dataSelect, handleDataSelectChange, {immediate: true});
    // Watch for changes to missingRate and call fetchData when it changes
    watch(missingRate, handleDataSelectChange, {immediate: true});

    return {
      submitForm,
      metrics,
      chartOptionsOriginal,
      chartOptionsImputed,
      dataSelect,
      currentSeriesNames,
      updateSeriesNames,
      truncationRank,
      epsilon,
      iterations,
      missingRate,
      imputedData,
      loadingResults
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px; /* Change this value to increase or decrease the margin */
}
</style>