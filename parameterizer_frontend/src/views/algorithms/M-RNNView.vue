<template>
  <h1 class="mb-4 text-center">M-RNN Detail</h1>
  <div class="d-flex">
    <div class="col-lg-8">
      <h2 v-if="rmse !== null && rmse !== ''"> RMSE: {{ rmse }}</h2>
      <h2 v-if="mae !== null && mae !== ''"> MAE: {{ mae }}</h2>
      <h2 v-if="mi !== null && mi !== ''"> MI: {{ mi }}</h2>
      <h2 v-if="corr !== null && corr !== ''"> Correlation: {{ corr }}</h2>
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
            <option value="1">1%</option>
            <option value="5">5%</option>
            <option value="10">10%</option>
            <option value="20">20%</option>
            <option value="40">40%</option>
            <option value="60">60%</option>
<!--            <option value="80">80%</option>-->
          </select>
        </div>
        <!-- Learning Rate -->
        <div class="mb-3">
          <label for="learningRate" class="form-label">Learning Rate: {{ learningRate }}</label>
          <input id="learningRate" v-model.number="learningRate" type="range" min="0.001" max="0.1" step="0.005" class="form-control">
        </div>

        <!-- Sequence Length -->
        <div class="mb-3">
          <label for="seq_len" class="form-label">Sequence Length: {{ seqLen }}</label>
          <input id="seq_len" v-model.number="seqLen" type="range" min="1" max="100" step="1" class="form-control">
        </div>

        <!-- Hidden Dimension Size -->
        <div class="mb-3">
          <label for="hidden_dim" class="form-label">Hidden Dimension Size: {{ hiddenDim }}</label>
          <input id="hidden_dim" v-model.number="hiddenDim" type="range" min="1" max="20" step="1" class="form-control">
        </div>

        <!-- Number of Iterations -->
        <div class="mb-3">
          <label for="iterations" class="form-label">Number of Iterations: {{ iterations }}</label>
          <input id="iterations" v-model.number="iterations" type="range" min="100" max="2000" step="100" class="form-control">
        </div>

        <!-- Keep Rate -->
        <div class="mb-3">
          <label for="keepProb" class="form-label">Keep Rate: {{ keepProb }}</label>
          <input id="keepProb" v-model.number="keepProb" type="range" min="0" max="1" step="0.1" class="form-control">
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import {ref} from 'vue';
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
    highcharts: Chart
  },
  setup() {
    const dataSelect = ref('BAFU_tiny') // Default data is BAFU
    const missingRate = ref('1'); // Default missing rate is 1%
    const learningRate = ref(0.01); // Default learning rate is 0.01
    const hiddenDim = ref(10); // Default hidden dimension size is 10
    const iterations = ref(500); // Default number of iterations is 1000
    const keepProb = ref(0.5); // Default keep probability is 0.5
    const seqLen = ref(7); // Default sequence length is 7
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

    const submitForm = async () => {
      try {
        let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
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
        chartOptions.value.series.splice(0, chartOptions.value.series.length);
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
      mae,
      mi,
      corr,
      chartOptions,
      dataSelect,
      learningRate,
      hiddenDim,
      iterations,
      keepProb,
      missingRate,
      seqLen
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px;  /* Change this value to increase or decrease the margin */
}
</style>