<template>
  <h1 class="mb-4 text-center">M-RNN Detail</h1>
  <div class="d-flex mb-auto">
    <div class="col-lg-8">
      <h2 v-if="rmse !== null && rmse !== ''"> RMSE: {{ rmse }}</h2>
      <h2 v-if="mae !== null && mae !== ''"> MAE: {{ mae }}</h2>
      <h2 v-if="mi !== null && mi !== ''"> MI: {{ mi }}</h2>
      <h2 v-if="corr !== null && corr !== ''"> CORR: {{ corr }}</h2>
      <highcharts v-if="imputedData" :options="chartOptionsImputed"></highcharts>
      <highcharts :options="chartOptionsOriginal"></highcharts>
    </div>
    <div class="col-lg-4">
      <form @submit.prevent="submitForm" class="sidebar col-lg-5">
        <data-select v-model="dataSelect" />
        <missing-rate v-model="missingRate" />
        <!-- Learning Rate -->
        <div class="mb-3">
          <label for="learningRate" class="form-label">Learning Rate: {{ learningRate }}</label>
          <input id="learningRate" v-model.number="learningRate" type="range" min="0.001" max="0.1" step="0.005" class="form-control">
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
          <input id="iterations" v-model.number="iterations" type="range" min="100" max="2000" step="100" class="form-control">
        </div>

        <!-- Keep Rate -->
        <div class="mb-3">
          <label for="keepProb" class="form-label">Keep Rate: {{ keepProb }}</label>
          <input id="keepProb" v-model.number="keepProb" type="range" min="0" max="1" step="0.1" class="form-control">
        </div>
        <button type="submit" class="btn btn-primary">Impute</button>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, watch} from 'vue';
import DataSelect from '../components/DataSelect.vue';
import MissingRate from '../components/MissingRate.vue';
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
    MissingRate
  },
  setup() {
    const dataSelect = ref('BAFU_tiny') // Default data is BAFU
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
      } catch(error) {
        console.error(error);
      }
    }

    const submitForm = async () => {
      try {
        let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
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
    watch(dataSelect, handleDataSelectChange, { immediate: true });
    // TODO Missingness display
    // watch(missingRate, fetchData, { immediate: true });

    return {
      submitForm,
      rmse,
      mae,
      mi,
      corr,
      chartOptionsOriginal,
      chartOptionsImputed,
      dataSelect,
      learningRate,
      hiddenDim,
      iterations,
      keepProb,
      missingRate,
      seqLen,
      imputedData
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px;  /* Change this value to increase or decrease the margin */
}
</style>