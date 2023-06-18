<template>
  <h1 class="mb-4 text-center">IIM Detail</h1>
  <div class="d-flex">
    <div class="col-lg-8">
      <h2> RMSE: {{ rmse }}</h2>
      <highcharts :options="chartOptions"></highcharts>
    </div>
    <div class="col-lg-4">
      <form @submit.prevent="submitForm" class="position-fixed sidebar">
        <div class="mb-3">
          <label for="dataSelect" class="form-label">Data Used for Imputation:</label>
          <select id="dataSelect" v-model="dataSelect" class="form-control">
            <option value="Bafu">Bafu</option>
            <option value="TODO">Other Data</option>
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
    const dataSelect = ref('Bafu') // Default data is BAFU
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
      rangeSelector: {
            x: 0,
            // floating: true,
            style: {
                color: 'black',
                fontWeight: 'bold',
                position: 'relative',
                "font-family": "Arial"
            },
            // inputDateParser: function (value) {
            //     value = value.split(/[:\.]/);
            //     return 1
            // },
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
        data: [
          [Date.UTC(2023, 0, 1), 1],
          [Date.UTC(2023, 0, 2), 2],
          [Date.UTC(2023, 0, 3), 3],
          [Date.UTC(2023, 0, 4), 4],
          [Date.UTC(2023, 0, 5), 5],
          //... more data points
        ],
        name: 'Original Data',
        showInLegend: true
      }],
      plotOptions: {
        series: {
          pointStart: Date.UTC(2010, 0, 1),
          pointInterval: 100000 * 1000 // one day
        }
      },
    //  TODO Range selector
    });

    const submitForm = async () => {
      try {
        const formattedAlgCode = `iim ${numberSelect.value}${typeSelect.value}`;
        const response = await axios.post('http://localhost:8000/api/iim/',
            {
              alg_code: formattedAlgCode,
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
        );
        rmse.value = response.data.rmse;
        console.log(response.data);
        chartOptions.value.series[0].data = [[Date.UTC(2024, 0, 1), 11],
          [Date.UTC(2024, 0, 2), 20],
          [Date.UTC(2024, 0, 3), 33],
          [Date.UTC(2024, 0, 4), 44],
          [Date.UTC(2024, 0, 5), 55],];
        chartOptions.value.title.text = response.data.title;
        chartOptions.value.series[1] = {
          data: [
            [Date.UTC(2024, 0, 1), 11],
            [Date.UTC(2024, 0, 2), 202],
            [Date.UTC(2024, 0, 3), 333],
            [Date.UTC(2024, 0, 4), 444],
            [Date.UTC(2024, 0, 5), 555],],
          name: 'Imputed Data',
          showInLegend: true
        };
      } catch (error) {
        console.error(error);
      }
    }

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

