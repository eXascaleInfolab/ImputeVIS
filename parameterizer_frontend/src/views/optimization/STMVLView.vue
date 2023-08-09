<template>
  <h3 class="mb-4 text-center">ST-MVL Optimization</h3>
  <div class="d-flex mb-auto">
    <div class="col-lg-8">
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
      <form v-if="optimalParametersDetermined" @submit.prevent="submitFormCustom"
            class="sidebar col-lg-7 align-items-center text-center">
        <h5>Optimal Parameters</h5>
        <data-select-optimization v-model="dataSelect" @update:seriesNames="updateSeriesNames"/>

        <!--Window Size-->
        <div class="mb-3">
          <label for="windowSize" class="form-label">Window Size: {{ windowSize }}</label>
          <input id="windowSize" v-model.number="windowSize" type="range" min="2" max="100" step="1"
                 class="form-control">
        </div>

        <!--Smoothing Parameter Gamma-->
        <div class="mb-3">
          <label for="gamma" class="form-label">Smoothing Parameter Gamma: {{ parseFloat(gamma).toFixed(5) }}</label>
          <input id="gamma" v-model.number="gamma" type="range" min="0.05" max="0.99" step="0.0005"
                 class="form-control">
        </div>

        <!-- Power for Spatial Weight (Alpha) -->
        <div class="mb-3">
          <label for="alpha" class="form-label">Power for Spatial Weight (alpha): {{ alpha }}</label>
          <input id="alpha" v-model.number="alpha" type="range" min="0.5" max="20" step="0.5" class="form-control">
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
        <data-select-optimization v-model="dataSelect" @update:seriesNames="updateSeriesNames"/>
        <!--        <missing-rate v-model="missingRate" />-->

        <button type="submit" class="btn btn-primary">Find Optimal Parameters</button>
        <div class="mt-3">
          <metrics-display :metrics="metrics"></metrics-display>
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
import OptimizationSelect from '../components/OptimizationSelect.vue';
import axios from 'axios';
import {Chart} from 'highcharts-vue'
import Highcharts from 'highcharts'
import HighchartsBoost from 'highcharts/modules/boost'
import {createSeries, generateChartOptions, generateChartOptionsLarge} from "@/views/thesisUtils/utils";

// Initialize exporting modules
HighchartsBoost(Highcharts)

export default {
  components: {
    DataSelectOptimization,
    highcharts: Chart,
    MetricsDisplay,
    MissingRate,
    OptimizationSelect
  },
  setup() {
    const optimizationParameters = ref({}); // To store the optimization parameters received from the child component
    const dataSelect = ref('climate_eighth') // Default data
    let currentSeriesNames = []; // Names of series currently displayed
    const missingRate = ref('1'); // Default missing rate is 1%
    const windowSize = ref('2'); // Default window size is 2
    const gamma = ref('0.5') // Default smoothing parameter gamma is 0.5, min 0.0, max 1.0
    const alpha = ref('2') // Default power for spatial weight (alpha) is 2, must be larger than 0.0
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
        let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
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
        console.log(dataSet);
        const response = await axios.post('http://localhost:8000/api/optimization/stmvl/',
            {
              ...optimizationParameters.value, // Spread the optimization parameters into the post body
              data_set: dataSet,
              algorithm: 'stmvl'
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
        );
        console.log(response.data);
        optimalResponse = response;
        gamma.value = response.data.best_params.gamma;
        alpha.value = response.data.best_params.alpha;
        windowSize.value = response.data.best_params.window_size;
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
          if (currentSeriesNames.length > 0) {
            chartOptionsImputed.value.series[index] = createSeries(index, data, currentSeriesNames[index]);
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
    const chartOptionsImputed = ref(generateChartOptionsLarge('Imputed Data', 'Data'));

    // Define a new function that calls fetchData
    const handleDataSelectChange = () => {
      fetchData();
    }

    const updateSeriesNames = (newSeriesNames) => {
      currentSeriesNames = newSeriesNames;
    };

    // Watch for changes and call fetchData when it changes
    watch(dataSelect, handleDataSelectChange, {immediate: true});
    // Watch for changes to missingRate and call fetchData when it changes
    watch(missingRate, handleDataSelectChange, { immediate: true });

    const resetToOptimalParameters = () => {
      if (optimalResponse) {
        alpha.value = optimalResponse.data.best_params.alpha;
        gamma.value = optimalResponse.data.best_params.gamma;
        windowSize.value = optimalResponse.data.best_params.window_size;
      }
    }

    return {
      submitForm,
      submitFormCustom,
      metrics,
      chartOptionsOriginal,
      chartOptionsImputed,
      dataSelect,
      updateSeriesNames,
      windowSize,
      gamma,
      alpha,
      missingRate,
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