<template>
  <h1 class="mb-4 text-center">IIM Detail</h1>
  <div class="d-flex">
    <div class="col-lg-8 ps-4">
<!--      <p class="lead">-->
<!--        BAFU dataset provided by the BundesAmt Für Umwelt (the Swiss Federal Office for the Environment).-->
<!--        <br>-->
<!--      This dataset contains water discharge time series of 12 different Swiss rivers recorded every 30 min during-->
<!--      2010 – 2015 resulting in 80k records per time series.-->
<!--      </p>-->
      <h2 v-if="rmse !== null && rmse !== ''"> RMSE: {{ rmse }}</h2>
      <h2 v-if="mae !== null && mae !== ''"> MAE: {{ mae }}</h2>
      <h2 v-if="mi !== null && mi !== ''"> MI: {{ mi }}</h2>
      <h2 v-if="corr !== null && corr !== ''"> CORR: {{ corr }}</h2>
      <highcharts :options="chartOptions"></highcharts>
    </div>
    <div class="col-lg-4">
      <form @submit.prevent="submitForm" class="position-fixed sidebar">
        <div class="mb-3">
          <label for="dataSelect" class="form-label">Data Used for Imputation:</label>
          <select id="dataSelect" v-model="dataSelect" class="form-control">
            <option value="BAFU">BAFU</option>
            <option value="BAFU_small">BAFU 1/2 Size</option>
            <option value="BAFU_tiny">BAFU 1/4 Size</option>
            <option value="cl2fullLarge">Chlorine</option>
            <option value="cl2fullLarge_half">Chlorine 1/2 Size</option>
            <option value="cl2fullLarge_quarter">Chlorine 1/4 Size</option>
            <option value="climate">Climate</option>
            <option value="climate_half">Climate 1/2 Size</option>
            <option value="climate_quarter">Climate 1/4 Size</option>
            <option value="meteo_total">Meteo</option>
            <option value="meteo_total_half">Meteo 1/2 Size</option>
            <option value="meteo_total_quarter">Meteo 1/4 Size</option>
          </select>
        </div>
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
        <div class="mb-3">
          <label for="numberSelect" class="form-label">Select Learning Neighbors:</label>
          <select id="numberSelect" v-model="numberSelect" class="form-control">
            <option v-for="number in Array.from({ length: 100 }, (_, i) => i + 1)" :key="number">{{ number }}</option>
          </select>
        </div>
        <div class="mb-3">
          <label for="typeSelect" class="form-label">Learning Type:</label>
          <select id="typeSelect" v-model="typeSelect" class="form-control">
            <option value="">Normal</option>
            <option value="a">Adaptive (High Processing Cost)</option>
          </select>
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, watch} from 'vue';
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
    chart: Chart,
  },
  setup() {
    const dataSelect = ref('BAFU_tiny') // Default data is BAFU
    const missingRate = ref('0'); // Default missing rate is 0%
    const numberSelect = ref(1); // Default selected learning neighbors is 1
    const typeSelect = ref(''); // Default selected type is "Normal", denoted by an empty string
    const rmse = ref(null);
    const mae = ref(null);
    const mi = ref(null);
    const corr = ref(null);

    //TODO Improve tooltip
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
      let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
      try {
        const formattedAlgCode = `iim ${numberSelect.value}${typeSelect.value}`;
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
      numberSelect,
      typeSelect,
      dataSelect,
      missingRate
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px;  /* Change this value to increase or decrease the margin */
}
</style>

