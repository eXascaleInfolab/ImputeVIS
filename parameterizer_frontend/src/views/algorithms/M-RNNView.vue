<template>
  <h1 class="mb-4 text-center">M-RNN Detail</h1>
  <div v-if="loadingResults" class="d-flex justify-content-center mt-3">
    <div class="alert alert-info d-flex align-items-center">
      <div class="spinner-border text-primary me-3" role="status"></div>
      Determining resulting imputation...
    </div>
  </div>
  <div class="d-flex mb-auto">
    <div class="col-lg-8">
      <metrics-display :metrics="metrics"></metrics-display>
      <highcharts v-if="imputedData" :options="chartOptionsImputed"></highcharts>
      <highcharts :options="chartOptionsOriginal"></highcharts>
    </div>
    <div class="col-lg-4">
      <form @submit.prevent="submitForm" class="sidebar col-lg-5">
        <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames"/>
        <missing-rate v-model="missingRate"/>
        <!-- Learning Rate -->
        <div class="mb-3">
          <label for="learningRate" class="form-label">Learning Rate: {{ learningRate }}</label>
          <input id="learningRate" v-model.number="learningRate" type="range" min="0.001" max="0.1" step="0.005"
                 class="form-control">
        </div>

        <!-- Sequence Length -->
        <!--        <div class="mb-3">-->
        <!--          <label for="seq_len" class="form-label">Sequence Length: {{ seqLen }}</label>-->
        <!--          <input id="seq_len" v-model.number="seqLen" type="range" min="1" max="100" step="1" class="form-control">-->
        <!--        </div>-->

        <!-- Hidden Dimension Size -->
        <div class="mb-3">
          <label for="hidden_dim" class="form-label">Hidden Dimension Size: {{ hiddenDim }}</label>
          <input id="hidden_dim" v-model.number="hiddenDim" type="range" min="1" max="20" step="1" class="form-control">
        </div>

        <!-- Number of Iterations -->
        <div class="mb-3" data-toggle="tooltip" data-placement="top" title="Also impacts run-time proportionally.">
          <label for="iterations" class="form-label">Number of Iterations: {{ iterations }}</label>
          <input id="iterations" v-model.number="iterations" type="range" min="10" max="2000" step="10"
                 class="form-control">
        </div>

        <!-- Keep Rate -->
        <div class="mb-3">
          <label for="keepProb" class="form-label">Keep Rate: {{ keepProb }}</label>
          <input id="keepProb" v-model.number="keepProb" type="range" min="0" max="1" step="0.1" class="form-control">
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
    const dataSelect = ref('climate_eighth') // Default data
    const currentSeriesNames = ref([]); // Names of series currently displayed
    const missingRate = ref('1'); // Default missing rate is 1%
    const learningRate = ref(0.01); // Default learning rate is 0.01
    const hiddenDim = ref(5); // Default hidden dimension size is 5
    const iterations = ref(10); // Default number of iterations is 10
    const keepProb = ref(1.0); // Default keep probability is 0.5
    const seqLen = ref(7); // Default sequence length is 7
    const imputedData = ref(false); // Whether imputation has been carried out
    const rmse = ref(null);
    const mae = ref(null);
    const mi = ref(null);
    const corr = ref(null);
    let loadingResults = ref(false);

    const metrics = computed(() => ({rmse: rmse.value, mae: mae.value, mi: mi.value, corr: corr.value}));


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
        let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
        const response = await axios.post('http://localhost:8000/api/mrnn/',
            {
              data_set: dataSet,
              hidden_dim: hiddenDim.value,
              learning_rate: learningRate.value,
              iterations: iterations.value,
              keep_prob: keepProb.value,
              seq_len: seqLen.value
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
          if (currentSeriesNames.value.length > 0) {
            chartOptionsImputed.value.series[index] = createSeries(index, data, currentSeriesNames.value[index]);
          } else {
            chartOptionsImputed.value.series[index] = createSeries(index, data);
          }
        });
        imputedData.value = true;
      } catch (error) {
        console.error(error);
      } finally {
        loadingResults.value = false;
      }
    }

    const chartOptionsOriginal = ref(generateChartOptions('Original Data', 'Data'));
    const chartOptionsImputed = ref(generateChartOptions('Imputed Data', 'Data'));

    // Define a new function that calls fetchData
    const handleDataSelectChange = () => {
      fetchData();
    }

    const updateSeriesNames = (newSeriesNames) => {
      currentSeriesNames.value = newSeriesNames;
    };
    // Watch for changes and call fetchData when it changes
    watch(dataSelect, handleDataSelectChange, {immediate: true});
    // TODO Missingness display
    // watch(missingRate, fetchData, { immediate: true });

    return {
      submitForm,
      metrics,
      chartOptionsOriginal,
      chartOptionsImputed,
      currentSeriesNames,
      updateSeriesNames,
      dataSelect,
      learningRate,
      hiddenDim,
      iterations,
      keepProb,
      missingRate,
      seqLen,
      loadingResults,
      imputedData
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px; /* Change this value to increase or decrease the margin */
}
</style>