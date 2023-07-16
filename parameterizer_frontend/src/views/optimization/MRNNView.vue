<template>
  <h1 class="mb-4 text-center">M-RNN Optimization</h1>
  <div class="d-flex mb-auto">
    <div class="col-lg-8">
      <h2 v-if="loadingResults">Determining resulting imputation...</h2>
      <metrics-display :metrics="metrics"></metrics-display>

      <highcharts v-if="imputedData" :options="chartOptionsImputed"></highcharts>
      <h2 class="text-center" v-if="loadingParameters">Determining optimal parameters...</h2>
      <form v-if="optimalParametersDetermined" @submit.prevent="submitFormCustom"
            class="sidebar col-lg-7 align-items-center text-center">
        <h2>Optimal Parameters</h2>
        <data-select v-model="dataSelect"/>

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
        <div class="mb-3">
          <label for="iterations" class="form-label">Number of Iterations: {{ iterations }}</label>
          <input id="iterations" v-model.number="iterations" type="range" min="100" max="2000" step="100"
                 class="form-control">
        </div>

        <!-- Keep Rate -->
        <div class="mb-3">
          <label for="keepProb" class="form-label">Keep Rate: {{ keepProb }}</label>
          <input id="keepProb" v-model.number="keepProb" type="range" min="0" max="1" step="0.1" class="form-control">
        </div>

        <button type="submit" class="btn btn-primary mr-3">Impute</button>
        <button type="button" class="btn btn-secondary ml-3" @click="resetToOptimalParameters">Reset to Determined
          Parameters
        </button>

      </form>
      <highcharts :options="chartOptionsOriginal"></highcharts>
    </div>
    <div class="col-lg-4">
      <form @submit.prevent="submitForm" class="sidebar col-lg-5">
        <optimization-select v-model="optimizationSelect" @parametersChanged="handleParametersChanged"/>
        <data-select v-model="dataSelect"/>
        <!--        <missing-rate v-model="missingRate" />-->

        <button type="submit" class="btn btn-primary">Find Optimal Parameters</button>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, watch, computed} from 'vue';
import DataSelect from '../components/DataSelect.vue';
import MetricsDisplay from '../components/MetricsDisplay.vue';
import MissingRate from '../components/MissingRate.vue';
import OptimizationSelect from '../components/OptimizationSelect.vue';
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
    MissingRate,
    OptimizationSelect
  },
  setup() {
    const optimizationParameters = ref({}); // To store the optimization parameters received from the child component
    const dataSelect = ref('BAFU_quarter') // Default data is BAFU
    const missingRate = ref('1'); // Default missing rate is 1%
    const learningRate = ref(0.01); // Default learning rate is 0.01
    const hiddenDim = ref(10); // Default hidden dimension size is 10
    const iterations = ref(500); // Default number of iterations is 1000
    const keepProb = ref(0.5); // Default keep probability is 0.5
    const seqLen = ref(7); // Default sequence length is 7
    const imputedData = ref(false); // Whether imputation has been carried out
    const rmse = ref(null);
    const mae = ref(null);
    const mi = ref(null);
    const corr = ref(null);
    const metrics = computed(() => ({rmse: rmse.value, mae: mae.value, mi: mi.value, corr: corr.value}));
    let optimalResponse: axios.AxiosResponse<any>;
    let optimalParametersDetermined = ref(false);
    let loadingParameters = ref(false);
    let loadingResults = ref(false);

    const handleParametersChanged = (newParams: any) => {
      optimizationParameters.value = newParams; // Update the optimization parameters
    };

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
      } catch (error) {
        console.error(error);
      }
    }

    const submitForm = async () => {
      try {
        let dataSet = `${dataSelect.value}_obfuscated_10`;
        loadingParameters.value = true;
        const response = await axios.post('http://localhost:8000/api/optimization/mrnn/',
            {
              ...optimizationParameters.value, // Spread the optimization parameters into the post body
              data_set: dataSet,
              algorithm: 'mrnn'
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
        );
        optimalResponse = response;
        hiddenDim.value = response.data.best_params.hidden_dim;
        learningRate.value = response.data.best_params.learning_rate;
        iterations.value = response.data.best_params.iterations;
        keepProb.value = response.data.best_params.keep_prob;
        optimalParametersDetermined.value = true;
        loadingParameters.value = false;
        await submitFormCustom();
      } catch (error) {
        console.error(error);
      } finally {
        loadingParameters.value = false;
      }
    }

    const submitFormCustom = async () => {
      try {
        loadingResults.value = true;
        let dataSet = `${dataSelect.value}_obfuscated_10`;
        console.log(dataSet);
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
          chartOptionsImputed.value.series[index] = createSeries(index, data);
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

    // Watch for changes and call fetchData when it changes
    watch(dataSelect, handleDataSelectChange, {immediate: true});
    // TODO Missingness display
    // watch(missingRate, fetchData, { immediate: true });

    const resetToOptimalParameters = () => {
      if (optimalResponse) {
        hiddenDim.value = optimalResponse.data.best_params.hidden_dim;
        learningRate.value = optimalResponse.data.best_params.learning_rate;
        iterations.value = optimalResponse.data.best_params.iterations;
        keepProb.value = optimalResponse.data.best_params.keep_prob;
      }
    }

    return {
      submitForm,
      submitFormCustom,
      metrics,
      chartOptionsOriginal,
      chartOptionsImputed,
      dataSelect,
      learningRate,
      hiddenDim,
      iterations,
      keepProb,
      missingRate,
      seqLen,
      optimizationParameters,
      handleParametersChanged,
      optimalParametersDetermined,
      loadingParameters,
      resetToOptimalParameters,
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