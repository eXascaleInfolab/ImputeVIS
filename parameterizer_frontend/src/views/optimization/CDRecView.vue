<template>
  <h1 class="mb-4 text-center">CDRec Optimization</h1>
  <div class="d-flex mb-auto">
    <div class="col-lg-8">
      <h2 v-if="loadingResults">Determining resulting imputation...</h2>
      <metrics-display :metrics="metrics"></metrics-display>
      <highcharts v-if="imputedData" :options="chartOptionsImputed"></highcharts>
      <h2 class="text-center" v-if="loadingParameters">Determining optimal parameters...</h2>
      <form v-if="optimalParametersDetermined" @submit.prevent="submitFormCustom"
            class="sidebar col-lg-7 align-items-center text-center">
        <h2>Optimal Parameters</h2>
        <data-select-optimization v-model="dataSelectOptimization" @update:seriesNames="updateSeriesNames"/>
        <!--        <missing-rate v-model="missingRate" />-->
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
        <div class="mb-3">
          <label for="iterations" class="form-label">Number of Iterations: {{ iterations }}</label>
          <input id="iterations" v-model.number="iterations" type="range" min="100" max="2000" step="100"
                 class="form-control">
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
        <data-select-optimization v-model="dataSelectOptimization" @update:seriesNames="updateSeriesNames"/>
        <!--        <missing-rate v-model="missingRate" />-->

        <button type="submit" class="btn btn-primary">Find Optimal Parameters</button>
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
    highcharts: Chart,
    DataSelectOptimization,
    MetricsDisplay,
    MissingRate,
    OptimizationSelect
  },
  setup() {
    const optimizationParameters = ref({}); // To store the optimization parameters received from the child component
    const dataSelect = ref('BAFU_eighth') // Default data is BAFU
    const currentSeriesNames = ref([]); // Names of series currently displayed
    const missingRate = ref('1'); // Default missing rate is 1%
    const truncationRank = ref('1') // Default truncation rank is 1, 0 means detect truncation automatically
    const epsilon = ref('E-7'); // Default epsilon is E-7
    const iterations = ref(500); // Default number of iterations is 1000
    const rmse = ref(null);
    const mae = ref(null);
    const mi = ref(null);
    const corr = ref(null);
    const metrics = computed(() => ({ rmse: rmse.value, mae: mae.value, mi: mi.value, corr: corr.value }));
    const imputedData = ref(false); // Whether imputation has been carried out
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
                'Content-Type': 'application/text',
              }
            }
        );
        chartOptionsOriginal.value.series.splice(0, chartOptionsOriginal.value.series.length);

        response.data.matrix.forEach((data: number[], index: number) => {
          // Replace NaN with 0
          const cleanData = data.map(value => isNaN(value) ? 0 : value);

          if (currentSeriesNames.value.length > 0 ) {
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
        let dataSet = `${dataSelect.value}_obfuscated_10`;
        loadingParameters.value = true;
        const response = await axios.post('http://localhost:8000/api/optimization/cdrec/',
            {
              ...optimizationParameters.value, // Spread the optimization parameters into the post body
              data_set: dataSet,
              algorithm: 'cdrec'
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
        );
        optimalResponse = response;
        truncationRank.value = response.data.best_params.rank;
        epsilon.value = response.data.best_params.eps.toFixed(5);
        iterations.value = response.data.best_params.iters;
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
        const response = await axios.post('http://localhost:8000/api/cdrec/',
            {
              data_set: dataSet,
              truncation_rank: truncationRank.value,
              //TODO Epsilon is not working
              epsilon: "E-2",
              iterations: iterations.value,
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
          if (currentSeriesNames.value.length > 0 ) {
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

    const resetToOptimalParameters = () => {
      if (optimalResponse) {
        truncationRank.value = optimalResponse.data.best_params.rank;
        epsilon.value = optimalResponse.data.best_params.eps;
        iterations.value = optimalResponse.data.best_params.iters;
      }
    }

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