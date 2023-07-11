<template>
  <h1 class="mb-4 text-center">STMVL Detail WIP</h1>
  <div class="d-flex mb-auto">
    <div class="col-lg-8">
      <h2 v-if="rmse !== null && rmse !== ''"> RMSE: {{ rmse }}</h2>
      <h2 v-if="mae !== null && mae !== ''"> MAE: {{ mae }}</h2>
      <h2 v-if="mi !== null && mi !== ''"> MI: {{ mi }}</h2>
      <h2 v-if="corr !== null && corr !== ''"> CORR: {{ corr }}</h2>
      <highcharts :options="chartOptions"></highcharts>
    </div>
    <div class="col-lg-4">
      <form @submit.prevent="submitForm" class="sidebar col-lg-5">
        <data-select v-model="dataSelect" />
        <div class="mb-3">
          <label for="missingRate" class="form-label">Missing Rates</label>
          <select id="missingRate" v-model="missingRate" class="form-control">
            <option value="0">0%</option>
            <option value="1">1%</option>
            <option value="5">5%</option>
            <option value="10">10%</option>
            <option value="20">20%</option>
            <option value="40">40%</option>
            <option value="60">60%</option>
            <option value="80">80%</option>
          </select>
        </div>
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

        <button type="submit" class="btn btn-primary">Submit</button>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, watch} from 'vue';
import DataSelect from '../components/DataSelect.vue';
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
    highcharts: Chart,
    DataSelect
  },
  setup() {
    const dataSelect = ref('BAFU_tiny') // Default data is BAFU
    const missingRate = ref('0'); // Default missing rate is 0%
    const windowSize = ref('2'); // Default window size is 2
    const gamma = ref('0.5') // Default smoothing parameter gamma is 0.5, min 0.0, max 1.0
    const alpha = ref('2') // Default power for spatial weight (alpha) is 2, must be larger than 0.0
    const rmse = ref(null);
    const mae = ref(null);
    const mi = ref(null);
    const corr = ref(null);


    const chartOptions = ref({
      credits: {
        enabled: false
      },
      title: {
        text: 'Time-series Data'
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
          name: 'Original Data',
          data: Uint32Array.from({length: 10000}, () => Math.floor(Math.random()*0)),
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
        chartOptions.value.series.splice(0, chartOptions.value.series.length);
        response.data.matrix.forEach((data: number[], index: number) => {
          chartOptions.value.series[index] = createSeries(index, data);
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
        chartOptions.value.series.splice(0, chartOptions.value.series.length);
        response.data.matrix_imputed.forEach((data: number[], index: number) => {
          chartOptions.value.series[index] = createSeries(index, data);
        });
      } catch (error) {
        console.error(error);
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
    function resetMissingRate() {
      missingRate.value = '0';
    }
    // Define a new function that calls both resetMissingRate and fetchData
    const handleDataSelectChange = () => {
      resetMissingRate();
      fetchData();
    }
    // Watch for changes and call fetchData when it changes
    watch(dataSelect, handleDataSelectChange, { immediate: true });
    // TODO Missingness display
    // watch(missingRate, fetchData, { immediate: true });

    return {
      submitForm,
      rmse,
      mae,
      mi,
      corr,
      chartOptions,
      dataSelect,
      windowSize,
      gamma,
      alpha,
      missingRate,
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px;  /* Change this value to increase or decrease the margin */
}
</style>