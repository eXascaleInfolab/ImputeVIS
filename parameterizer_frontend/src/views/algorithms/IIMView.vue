<template>
  <h1 class="mb-4 text-center">IIM Detail</h1>
  <div class="d-flex">
    <div class="col-lg-8 ps-4">
      <p class="lead">
        BAFU dataset provided by the BundesAmt Für Umwelt (the Swiss Federal Office for the Environment).
        <br>
      This dataset contains water discharge time series of 12 different Swiss rivers recorded every 30 min during
      2010 – 2015 resulting in 80k records per time series.
      </p>
      <h2> RMSE: {{ rmse }}</h2>
      <highcharts :options="chartOptions"></highcharts>
    </div>
    <div class="col-lg-4">
      <form @submit.prevent="submitForm" class="position-fixed sidebar">
        <div class="mb-3">
          <label for="dataSelect" class="form-label">Data Used for Imputation:</label>
          <select id="dataSelect" v-model="dataSelect" class="form-control">
            <option value="Bafu_small">BAFU 1/2 Size</option>
            <option value="Bafu_tiny">Bafu 1/4 Size</option>
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
            <option value="a">Adaptive</option>
          </select>
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import {ref} from 'vue';
import axios from 'axios';
import {Chart, StockChart, MapChart, ChartCompositionApi} from 'highcharts-vue'
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
    stockChart: StockChart,
    mapChart: MapChart,
    chartCompositionApi: ChartCompositionApi
  },
  setup() {
    const dataSelect = ref('Bafu_tiny') // Default data is BAFU
    const numberSelect = ref(1); // Default selected learning neighbors is 1
    const typeSelect = ref(''); // Default selected type is "Normal", denoted by an empty string
    const rmse = ref(null);

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

    const submitForm = async () => {
      try {
        const formattedAlgCode = `iim ${numberSelect.value}${typeSelect.value}`;
        const response = await axios.post('http://localhost:8000/api/iim/',
            {
              alg_code: formattedAlgCode,
              data_set: dataSelect.value
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
        );
        rmse.value = response.data.rmse;
        response.data.matrix_imputed.forEach((data: number[], index: number) => {
          chartOptions.value.series[index] = createSeries(index, data);
        });
      } catch (error) {
        console.error(error);
      }
    }

    const createSeries = (index: number, data: number[]) => ({
      name: `Imputed Data: Station ${index + 1}`,
      data,
      pointStart: Date.UTC(2010, 1, 1),
      pointInterval: 1000 * 60 * 30, // Granularity of 30 minutes
      tooltip: {
        valueDecimals: 2
      }
    });

    return {
      submitForm,
      rmse,
      chartOptions,
      numberSelect,
      typeSelect,
      dataSelect
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px;  /* Change this value to increase or decrease the margin */
}
</style>

