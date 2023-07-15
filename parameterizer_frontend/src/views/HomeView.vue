<template>
  <main>
    <h2>Here you will be able to compare algorithms to each other, using recommended parameters.</h2>

    <h3>TODO: Add table of datasets </h3>


  </main>
  <h1 class="mb-4 text-center">Compare Algorithms</h1>
  <h2 v-if="loadingResults">Determining resulting imputation...</h2>
  <div class="d-flex mb-auto">
    <div class="col-lg-10">
      <div class="d-flex justify-content-between">
        <div class="form-check px-5 mx-5">
          <input class="form-check-input" type="checkbox" value="CDRec" id="CDRec" v-model="checkedNames"
                 @change="handleCheckboxChange">
          <label class="form-check-label" for="CDRec">
            CDRec
          </label>
        </div>

        <div class="form-check px-5 mx-5">
          <input class="form-check-input" type="checkbox" value="IIM" id="IIM" v-model="checkedNames"
                 @change="handleCheckboxChange">
          <label class="form-check-label" for="IIM">
            IIM
          </label>
        </div>

        <div class="form-check px-5 mx-5">
          <input class="form-check-input" type="checkbox" value="MRNN" id="MRNN" v-model="checkedNames"
                 @change="handleCheckboxChange">
          <label class="form-check-label" for="MRNN">
            MRNN
          </label>
        </div>

        <div class="form-check px-5 mx-5">
          <input class="form-check-input" type="checkbox" value="ST-MVL" id="ST-MVL" v-model="checkedNames"
                 @change="handleCheckboxChange">
          <label class="form-check-label" for="ST-MVL">
            ST-MVL
          </label>
        </div>
      </div>

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
      <highcharts :options="chartOptionsOriginal"></highcharts>
    </div>
    <div class="col-lg-4">
      <form @submit.prevent="submitForm" class="sidebar col-lg-5">
        <data-select v-model="dataSelect"/>
        <missing-rate v-model="missingRate"/>
        <!-- Learning Rate -->
        <button type="submit" class="btn btn-primary">Impute</button>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, watch, reactive} from 'vue';
import DataSelect from './components/DataSelect.vue';
import MissingRate from './components/MissingRate.vue';
import OptimizationSelect from './components/OptimizationSelect.vue';
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
    DataSelect,
    MissingRate
  },
  setup() {
    const dataSelect = ref('BAFU_quarter') // Default data is BAFU
    const fetchedData = reactive({});
    let loadingResults = ref(false);
    //CDRec Parameters
    const missingRate = ref('1'); // Default missing rate is 1%
    const truncationRank = ref('1') // Default truncation rank is 1, 0 means detect truncation automatically
    const epsilon = ref('E-7'); // Default epsilon is E-7
    const iterations = ref(500); // Default number of iterations is 1000

    //IIM Parameters
    const numberSelect = ref(1); // Default selected learning neighbors is 1
    const typeSelect = ref(''); // Default selected type is "Normal", denoted by an empty string

    // M-RNN Parameters
    const learningRate = ref(0.01); // Default learning rate is 0.01
    const hiddenDim = ref(10); // Default hidden dimension size is 10
    const iterationsMRNN = ref(500); // Default number of iterations is 1000
    const keepProb = ref(0.5); // Default keep probability is 0.5
    const seqLen = ref(7); // Default sequence length is 7

    // ST-MVL Parameters
    const windowSize = ref('2'); // Default window size is 2
    const gamma = ref('0.5') // Default smoothing parameter gamma is 0.5, min 0.0, max 1.0
    const alpha = ref('2') // Default power for spatial weight (alpha) is 2, must be larger than 0.0


    const checkedNames = ref([]);
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
                'Content-Type': 'application/text',
              }
            }
        );
        chartOptionsOriginal.value.series.splice(0, chartOptionsOriginal.value.series.length);

        response.data.matrix.forEach((data: number[], index: number) => {
          // Replace NaN with 0
          const cleanData = data.map(value => isNaN(value) ? 0 : value);
          chartOptionsOriginal.value.series[index] = createSeries(index, cleanData);
        });
      } catch (error) {
        console.error(error);
      }
    }

    const submitForm = async () => {
      // TODO Reset probably
    }

    const createSeries = (index: number, data: number[]) => ({
      name: `Imputed Data: Series ${index + 1}`,
      data,
      pointStart: Date.UTC(2010, 1, 1),
      pointInterval: 1000 * 60 * 30, // Granularity of 30 minutes
      // visible: true,
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
        height: 900,
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
        buttons: [
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

    const handleCheckboxChange = async () => {
      // Clear the existing series
      // chartOptionsImputed.value.series = [];
      loadingResults.value = true;
      chartOptionsImputed.value.series.splice(0, chartOptionsImputed.value.series.length)

      for (let checkedName of checkedNames.value) {
        let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
        if (checkedName.toLowerCase() === 'cdrec') {
          if (!fetchedData[checkedName]) {
            const response = await axios.post('http://localhost:8000/api/cdrec/',
                {
                  data_set: dataSet,
                  truncation_rank: truncationRank.value,
                  epsilon: epsilon.value,
                  iterations: iterations.value,
                },
                {
                  headers: {
                    'Content-Type': 'application/json',
                  }
                }
            );
            fetchedData[checkedName] = response.data;
          }
          fetchedData[checkedName].matrix_imputed.forEach((data: number[], index: number) => {
            //The push should theoretically ensure that we are just adding
            chartOptionsImputed.value.series.push(createSeries(index, data));
          });
        } else if (checkedName.toLowerCase() == 'iim') {
          if (!fetchedData[checkedName]) {
            const formattedAlgCode = `iim ${numberSelect.value}${typeSelect.value}`;
            const response = await axios.post('http://localhost:8000/api/iim/',
                {
                  data_set: dataSet,
                  alg_code: formattedAlgCode,
                },
                {
                  headers: {
                    'Content-Type': 'application/json',
                  }
                }
            );
            fetchedData[checkedName] = response.data;
          }
          fetchedData[checkedName].matrix_imputed.forEach((data: number[], index: number) => {
            chartOptionsImputed.value.series.push(createSeries(index, data));
          });
        } else if (checkedName.toLowerCase() === 'mrnn') {
          if (!fetchedData[checkedName]) {
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
            fetchedData[checkedName] = response.data;
          }
          fetchedData[checkedName].matrix_imputed.forEach((data: number[], index: number) => {
            chartOptionsImputed.value.series.push(createSeries(index, data));
          });
        } else if (checkedName.toLowerCase() === 'st-mvl') {
          if (!fetchedData[checkedName]) {
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
            fetchedData[checkedName] = response.data;
          }
          fetchedData[checkedName].matrix_imputed.forEach((data: number[], index: number) => {
            chartOptionsImputed.value.series.push(createSeries(index, data));
          });
        }
        loadingResults.value = false;
        imputedData.value = true;
      }
    };

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

    return {
      submitForm,
      rmse,
      mae,
      mi,
      corr,
      chartOptionsOriginal,
      chartOptionsImputed,
      dataSelect,
      truncationRank,
      epsilon,
      iterations,
      missingRate,
      imputedData,
      checkedNames,
      handleCheckboxChange,
      loadingResults
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px; /* Change this value to increase or decrease the margin */
}
</style>