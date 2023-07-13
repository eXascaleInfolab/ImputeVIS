<template>
  <h1 class="mb-4 text-center">IIM Optimization WIP</h1>
  <div class="d-flex mb-auto">
    <div class="col-lg-8">
      <h2 v-if="loadingResults">Determining resulting imputation...</h2>
      <div class="row">
        <div class="col-sm-4">
          <h2 v-if="rmse !== null && rmse !== ''"> RMSE: {{ rmse }}</h2>
          <h2 v-if="mae !== null && mae !== ''"> MAE: {{ mae }}</h2>
        </div>
        <div class="col-sm-4">
          <h2 v-if="mi !== null && mi !== ''"> MI: {{ mi }}</h2>
          <h2 v-if="corr !== null && corr !== ''"> CORR: {{ corr }}</h2>
        </div>
      </div>
      <highcharts v-if="imputedData" :options="chartOptionsImputed"></highcharts>
      <h2 class="text-center" v-if="loadingParameters">Determining optimal parameters...</h2>
      <form v-if="optimalParametersDetermined" @submit.prevent="submitFormCustom"
            class="sidebar col-lg-7 align-items-center text-center">
        <h2>Optimal Parameters</h2>
        <data-select v-model="dataSelect"/>
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
        <data-select v-model="dataSelect"/>
        <!--        <missing-rate v-model="missingRate" />-->

        <button type="submit" class="btn btn-primary">Find Optimal Parameters</button>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, watch} from 'vue';
import DataSelect from '../components/DataSelect.vue';
import MissingRate from '../components/MissingRate.vue';
import OptimizationSelect from '../components/OptimizationSelect.vue';
import axios from 'axios';
import {Chart} from 'highcharts-vue'
import Highcharts from 'highcharts'
import HC_exporting from 'highcharts/modules/exporting'
import HC_exportData from 'highcharts/modules/export-data'

// Initialize exporting modules
HC_exporting(Highcharts)
HC_exportData(Highcharts)

export default {
  components: {
    DataSelect,
    highcharts: Chart,
    MissingRate,
    OptimizationSelect
  },
  setup() {
    const optimizationParameters = ref({}); // To store the optimization parameters received from the child component
    const dataSelect = ref('BAFU_tiny') // Default data is BAFU
    const missingRate = ref('1'); // Default missing rate is 1%
    const numberSelect = ref(1); // Default selected learning neighbors is 1
    const typeSelect = ref(''); // Default selected type is "Normal", denoted by an empty string
    const imputedData = ref(false); // Whether imputation has been carried out
    const rmse = ref(null);
    const mae = ref(null);
    const mi = ref(null);
    const corr = ref(null);
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
        console.log(dataSet);
        const response = await axios.post('http://localhost:8000/api/optimization/iim/',
            {
              ...optimizationParameters.value, // Spread the optimization parameters into the post body
              data_set: dataSet,
              algorithm: 'iim'
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
        );
        console.log(response.data);
        optimalResponse = response;
        numberSelect.value = response.data.best_params.learning_neighbours;
        chartOptionsImputed.value.series.splice(0, chartOptionsImputed.value.series.length);
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
        const formattedAlgCode = `iim ${numberSelect.value}${typeSelect.value}`;
        let dataSet = `${dataSelect.value}_obfuscated_10`;
        const response = await axios.post('http://localhost:8000/api/iim/',
            {
              alg_code: formattedAlgCode,
              data_set: dataSet
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

    const createSeries = (index: number, data: number[]) => ({
      name: `Imputed Data: Series ${index + 1}`,
      data,
      pointStart: Date.UTC(2010, 1, 1),
      pointInterval: 1000 * 60 * 30, // Granularity of 30 minutes
      tooltip: {
        valueDecimals: 2
      }
    });

    const generateChartOptions = (title, seriesName) => ({
      credits: {
        enabled: false
      },
      title: {
        text: title
      },
      xAxis: {
        type: 'datetime'
      },
      chart: {
        type: 'line',
        zoomType: 'x',
        panning: true,
        panKey: 'shift'
      },
      rangeSelector: {
        x: 0,
        // floating: true,
        style: {
          color: 'black',
          fontWeight: 'bold',
          position: 'relative',
          "font-family": "Arial"
        },
        enabled: true,
        inputEnabled: false,
        // inputDateFormat: '%y',
        // inputEditDateFormat: '%y',
        buttons: [{
          type: 'hour',
          count: 1,
          text: 'H'
        },
          {
            type: 'day',
            count: 1,
            text: 'D'
          },

          {
            type: 'month',
            count: 1,
            text: 'M'
          },
          {
            type: 'year',
            count: 1,
            text: 'Y'
          },

          {
            type: 'all',
            text: 'All',
            align: 'right',
            x: 1000,
            y: 100,
          }],
      },
      series: [{
        name: seriesName,
        data: Uint32Array.from({length: 10000}, () => Math.floor(Math.random() * 0)),
        pointStart: Date.UTC(2010, 1, 1),
        pointInterval: 1000 * 60 * 30, // Granularity of 30 minutes
        tooltip: {
          valueDecimals: 2
        }
      }],
      // plotOptions: {
      //   series: {
      //     pointStart: Date.UTC(2010, 0, 1),
      //     pointInterval: 100000 * 1000 // one day
      //   }
      // },
    });

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
        numberSelect.value = optimalResponse.data.best_params.learning_neighbours;
      }
    }

    return {
      submitForm,
      rmse,
      mae,
      mi,
      corr,
      chartOptionsOriginal,
      chartOptionsImputed,
      numberSelect,
      typeSelect,
      dataSelect,
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

