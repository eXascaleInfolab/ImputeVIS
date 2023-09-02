<template>
  <h3 class="mb-4 text-center">M-RNN Optimization</h3>
  <div class="d-flex mb-auto">
    <div class="col-lg-10">
      <div v-if="loadingResults" class="d-flex justify-content-center mt-3">
        <div class="alert alert-info d-flex align-items-center">
          <div class="spinner-border text-primary me-3" role="status"></div>
          Determining resulting imputation...
        </div>
      </div>

      <highcharts v-if="imputedData" :options="chartOptionsImputed"></highcharts>
      <div v-if="loadingParameters" class="d-flex justify-content-center mt-3">
        <div class="alert alert-info d-flex align-items-center">
          <div class="spinner-border text-primary me-3" role="status"></div>
          Determining optimal parameters...
        </div>
      </div>
      <form v-if="optimalParametersDetermined && imputedData" @submit.prevent="submitFormCustom"
            class="sidebar col-lg-3 align-items-center text-center">
        <h5>Optimal Parameters</h5>
        <data-select-optimization v-model="dataSelect" @update:seriesNames="updateSeriesNames"/>

        <!-- Learning Rate -->
        <div class="mb-3">
          <label for="learningRate" class="form-label">Learning Rate: {{ parseFloat(learningRate).toFixed(6) }}</label>
          <input id="learningRate" v-model.number="learningRate" type="range" min="0" max="0.1" step="0.00005"
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
          <input id="iterations" v-model.number="iterations" type="range" min="100" max="2000" step="100"
                 class="form-control">
        </div>

        <!-- Keep Rate -->
        <div class="mb-3">
          <label for="keepProb" class="form-label">Keep Rate: {{ parseFloat(keepProb).toFixed(4) }}</label>
          <input id="keepProb" v-model.number="keepProb" type="range" min="0" max="1" step="0.1" class="form-control">
        </div>

        <button type="submit" class="btn btn-primary mr-3">Impute</button>
        <button type="button" class="btn btn-secondary ml-3" @click="resetToOptimalParameters">Reset to Determined
          Parameters
        </button>

      </form>
      <highcharts v-if="!imputedData" :options="chartOptionsOriginal"></highcharts>
    </div>
    <div class="col-lg-4">
      <form @submit.prevent="submitForm" class="sidebar col-lg-5">
        <optimization-select v-model="optimizationSelect" @parametersChanged="handleParametersChanged"/>
        <data-select-optimization v-model="dataSelect" @update:seriesNames="updateSeriesNames"/>
        <!--        <missing-rate v-model="missingRate" />-->
        <normalization-toggle v-model="normalizationMode"></normalization-toggle>

        <br/>
        <button type="submit" class="btn btn-primary">Find Optimal Parameters</button>
        <div class="mt-3">
          <metrics-display v-if="imputedData" :metrics="metrics"></metrics-display>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, watch, computed} from 'vue';
import DataSelectOptimization from '../components/DataSelectOptimization.vue';
import MetricsDisplay from '../components/MetricsDisplay.vue';
import MissingRate from '../components/MissingRate.vue';
import NormalizationToggle from '../components/NormalizationToggleOptimization.vue'
import OptimizationSelect from '../components/OptimizationSelect.vue';
import axios from 'axios';
import {Chart} from 'highcharts-vue'
import Highcharts from 'highcharts'
import HighchartsBoost from 'highcharts/modules/boost'
import {
  createSegmentedSeries,
  createSeries,
  generateChartOptions,
  generateChartOptionsLarge
} from "@/views/thesisUtils/utils";

// HighchartsBoost(Highcharts)

export default {
  components: {
    DataSelectOptimization,
    highcharts: Chart,
    MetricsDisplay,
    MissingRate,
    NormalizationToggle,
    OptimizationSelect
  },
  setup() {
    const optimizationParameters = ref({}); // To store the optimization parameters received from the child component
    const dataSelect = ref('climate_eighth') // Default data
    const normalizationMode = ref('Normal')
    let currentSeriesNames = []; // Names of series currently displayed
    const missingRate = ref('10'); // Default missing rate
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
    let obfuscatedMatrix = [];

    const handleParametersChanged = (newParams: any) => {
      optimizationParameters.value = newParams; // Update the optimization parameters
    };

    const fetchData = async () => {
      try {
        let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
        const response = await axios.post('http://localhost:8000/api/fetchData/',
            {
              data_set: dataSet,
              normalization: normalizationMode.value,
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
        );
        chartOptionsOriginal.value.series.splice(0, chartOptionsOriginal.value.series.length);
        obfuscatedMatrix = response.data.matrix;
        response.data.matrix.forEach((data: number[], index: number) => {
          // Replace NaN with 0
          const cleanData = data.map(value => isNaN(value) ? 0 : value);

          if (currentSeriesNames.length > 0) {
            chartOptionsOriginal.value.series[index] = createSeries(index, cleanData, currentSeriesNames[index]);
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
        let dataSet = `${dataSelect.value}_obfuscated_10`;
        loadingParameters.value = true;
        imputedData.value = false;
        const response = await axios.post('http://localhost:8000/api/optimization/mrnn/',
            {
              ...optimizationParameters.value, // Spread the optimization parameters into the post body
              data_set: dataSet,
              normalization: normalizationMode.value,
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
        imputedData.value = false;
        let dataSet = `${dataSelect.value}_obfuscated_10`;
        const response = await axios.post('http://localhost:8000/api/mrnn/',
            {
              data_set: dataSet,
              normalization: normalizationMode.value,
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
        chartOptionsImputed.value.series.length = 0;
        // Create a new array for the new series data
        const newSeriesData = [];

        const displayImputation = missingRate.value != '40' && missingRate.value != '60' && missingRate.value != '80'
        response.data.matrix_imputed.forEach((data: number[], index: number) => {
          if (currentSeriesNames.length > 0 && missingRate) {
            if (displayImputation) {
              newSeriesData.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value, currentSeriesNames[index]));
            } else {
              newSeriesData.push(createSeries(index, data, currentSeriesNames[index]));
            }
          } else {
            if (displayImputation) {
              newSeriesData.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value));
            } else {
              newSeriesData.push(createSeries(index, data))
            }
          }
        });
        chartOptionsImputed.value.series = newSeriesData;
        imputedData.value = true;
      } catch (error) {
        console.error(error);
      } finally {
        loadingResults.value = false;
      }
    }
    const chartOptionsOriginal = ref(generateChartOptions('Original Data', 'Data'));
    const chartOptionsImputed = ref(generateChartOptionsLarge('Imputed Data', 'Data'));

    // Define a new function that calls fetchData
    const handleDataSelectChange = () => {
      chartOptionsImputed.value = generateChartOptionsLarge('Imputed Data', 'Data')
      fetchData();
    }

    const updateSeriesNames = (newSeriesNames) => {
      currentSeriesNames = newSeriesNames;
    };

    const handleNormalizationModeChange = () => {
      if (imputedData.value == true) {
          submitFormCustom();
      } else {
          handleDataSelectChange();
      }
    }

    // Watch for changes and call fetchData when it changes
    watch([dataSelect, missingRate], handleDataSelectChange, {immediate: true});
    watch(normalizationMode, handleNormalizationModeChange, {immediate: true});

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
      normalizationMode,
      updateSeriesNames,
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