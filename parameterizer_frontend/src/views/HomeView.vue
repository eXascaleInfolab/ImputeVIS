<template>
  <main>
  </main>
  <h1 class="mb-4 text-center">Compare Algorithms</h1>
  <h2 v-if="loadingResults">Determining resulting imputation...</h2>
  <div class="d-flex mb-auto">
    <div class="col-lg-12">
      <div class="row ms-5">
        <div class="col-lg-9">
          <highcharts v-if="imputedData" class="mb-5 pb-5" :options="chartOptionsImputed"></highcharts>
          <highcharts :options="chartOptionsOriginal"></highcharts>
        </div>
        <div class="col-lg-3">
          <div class="row">
            <div class="col-lg-6">
              <form @submit.prevent="submitForm">
                <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames"/>
                <missing-rate v-model="missingRate"/>
                <div class="d-flex justify-content-center mt-2">
                  <button type="submit" class="btn btn-primary align-center">Refresh</button>
                </div>
              </form>
            </div>
          </div>
          <div class="col-lg-8 mt-4">
            <h4>Select algorithm(s)</h4>
            <div class="row">
              <div class="col form-check ">
                <input class="form-check-input" type="checkbox" value="CDRec" id="CDRec" v-model="checkedNames"
                       @change="handleCheckboxChange">
                <label class="form-check-label" for="CDRec">
                  CDRec
                </label>
              </div>
              <div class="col form-check ">
                <input class="form-check-input" type="checkbox" value="IIM" id="IIM" v-model="checkedNames"
                       @change="handleCheckboxChange">
                <label class="form-check-label" for="IIM">
                  IIM
                </label>
              </div>
            </div>
            <div class="row">
              <div class="col form-check ">
                <input class="form-check-input" type="checkbox" value="MRNN" id="MRNN" v-model="checkedNames"
                       @change="handleCheckboxChange">
                <label class="form-check-label" for="MRNN">
                  MRNN
                </label>
              </div>
              <div class="col form-check ">
                <input class="form-check-input" type="checkbox" value="ST-MVL" id="ST-MVL" v-model="checkedNames"
                       @change="handleCheckboxChange">
                <label class="form-check-label" for="ST-MVL">
                  ST-MVL
                </label>
              </div>
            </div>

          </div>
          <div class="col-lg-8 mt-5">
            <div class="row">
              <div class="col-xs">
                <h6 v-if="rmseCDRec !== null && rmseCDRec !== ''"> CDRec RMSE: {{ rmseCDRec }}</h6>
                <h6 v-if="maeCDRec !== null && maeCDRec !== ''"> CDRec MAE: {{ maeCDRec }}</h6>
                <h6 v-if="miCDRec !== null && miCDRec !== ''"> CDRec MI: {{ miCDRec }}</h6>
                <h6 v-if="corrCDRec !== null && corrCDRec !== ''"> CDRec CORR: {{ corrCDRec }}</h6>
              </div>
            </div>
          </div>
          <div class="col-lg-8 mt-5">
            <div class="row">
              <div class="col-xs">
                <h6 v-if="rmseIIM !== null && rmseIIM !== ''"> IIM RMSE: {{ rmseIIM }}</h6>
                <h6 v-if="maeIIM !== null && maeIIM !== ''"> IIM MAE: {{ maeIIM }}</h6>
                <h6 v-if="miIIM !== null && miIIM !== ''"> IIM MI: {{ miIIM }}</h6>
                <h6 v-if="corrIIM !== null && corrIIM !== ''"> IIM CORR: {{ corrIIM }}</h6>
              </div>
            </div>
          </div>
          <div class="col-lg-8 mt-5">
            <div class="row">
              <div class="col-xs">
                <h6 v-if="rmseMRNN !== null && rmseMRNN !== ''"> M-RNN RMSE: {{ rmseMRNN }}</h6>
                <h6 v-if="maeMRNN !== null && maeMRNN !== ''"> M-RNN MAE: {{ maeMRNN }}</h6>
                <h6 v-if="miMRNN !== null && miMRNN !== ''"> M-RNN MI: {{ miMRNN }}</h6>
                <h6 v-if="corrMRNN !== null && corrMRNN !== ''"> M-RNN CORR: {{ corrMRNN }}</h6>
              </div>
            </div>
          </div>
          <div class="col-lg-8 mt-5">
            <div class="row">
              <div class="col-xs">
                <h6 v-if="rmseSTMVL !== null && rmseSTMVL !== ''"> ST-MVL RMSE: {{ rmseSTMVL }}</h6>
                <h6 v-if="maeSTMVL !== null && maeSTMVL !== ''"> ST-MVL MAE: {{ maeSTMVL }}</h6>
                <h6 v-if="miSTMVL !== null && miSTMVL !== ''"> ST-MVL MI: {{ miSTMVL }}</h6>
                <h6 v-if="corrSTMVL !== null && corrSTMVL !== ''"> ST-MVL CORR: {{ corrSTMVL }}</h6>
              </div>
            </div>
          </div>
        </div>
      </div>


    </div>
  </div>
</template>

<script lang="ts">
import {ref, watch, reactive, UnwrapNestedRefs} from 'vue';
import DataSelect from './components/DataSelect.vue';
import MissingRate from './components/MissingRate.vue';
import OptimizationSelect from './components/OptimizationSelect.vue';
import axios from 'axios';
import {Chart} from 'highcharts-vue'
import Highcharts from 'highcharts'
import HC_exporting from 'highcharts/modules/exporting'
import HC_exportData from 'highcharts/modules/export-data'
import HighchartsBoost from "highcharts/modules/boost";
import {createSeries, generateChartOptions, generateChartOptionsLarge} from "@/views/thesisUtils/utils";

// Initialize exporting modules
HC_exporting(Highcharts)
HC_exportData(Highcharts)
HighchartsBoost(Highcharts)

export default {
  components: {
    highcharts: Chart,
    DataSelect,
    MissingRate
  }, setup() {
    const dataSelect = ref('BAFU_quarter') // Default data is BAFU
    const currentSeriesNames = ref([]); // Names of series currently displayed
    const fetchedData = reactive({});
    let loadingResults = ref(false);

    //CDRec Parameters
    const missingRate = ref('1'); // Default missing rate is 1%
    const truncationRank = ref('1') // Default truncation rank is 1, 0 means detect truncation automatically
    const epsilon = ref('E-7'); // Default epsilon is E-7
    const iterations = ref(500); // Default number of iterations is 1000
    const rmseCDRec = ref(null);
    const maeCDRec = ref(null);
    const miCDRec = ref(null);
    const corrCDRec = ref(null);

    //IIM Parameters
    const numberSelect = ref(1); // Default selected learning neighbors is 1
    const typeSelect = ref(''); // Default selected type is "Normal", denoted by an empty string
    const rmseIIM = ref(null);
    const maeIIM = ref(null);
    const miIIM = ref(null);
    const corrIIM = ref(null);

    // M-RNN Parameters
    const learningRate = ref(0.01); // Default learning rate is 0.01
    const hiddenDim = ref(10); // Default hidden dimension size is 10
    const iterationsMRNN = ref(500); // Default number of iterations is 1000
    const keepProb = ref(0.5); // Default keep probability is 0.5
    const seqLen = ref(7); // Default sequence length is 7
    const rmseMRNN = ref(null);
    const maeMRNN = ref(null);
    const miMRNN = ref(null);
    const corrMRNN = ref(null);

    // ST-MVL Parameters
    const windowSize = ref('2'); // Default window size is 2
    const gamma = ref('0.5') // Default smoothing parameter gamma is 0.5, min 0.0, max 1.0
    const alpha = ref('2') // Default power for spatial weight (alpha) is 2, must be larger than 0.0
    const rmseSTMVL = ref(null);
    const maeSTMVL = ref(null);
    const miSTMVL = ref(null);
    const corrSTMVL = ref(null);


    const checkedNames = ref([]);
    const imputedData = ref(false); // Whether imputation has been carried out


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
        // chartOptionsImputed.value.series.splice(0, chartOptionsImputed.value.series.length);
        clearErrorMetrics();
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


    function clearErrorMetrics() {
      rmseCDRec.value = null;
      maeCDRec.value = null;
      miCDRec.value = null;
      corrCDRec.value = null;

      rmseIIM.value = null;
      maeIIM.value = null;
      miIIM.value = null;
      corrIIM.value = null;

      rmseMRNN.value = null;
      maeMRNN.value = null;
      miMRNN.value = null;
      corrMRNN.value = null;

      rmseSTMVL.value = null;
      maeSTMVL.value = null;
      miSTMVL.value = null;
      corrSTMVL.value = null;
    }

    const handleCheckboxChange = async () => {
      // Clear the existing series
      // chartOptionsImputed.value.series = [];
      loadingResults.value = true;
      imputedData.value = false;
      chartOptionsImputed.value.series.splice(0, chartOptionsImputed.value.series.length)
      clearErrorMetrics();

      try {
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
            rmseCDRec.value = fetchedData[checkedName].rmse.toFixed(3);
            maeCDRec.value = fetchedData[checkedName].mae.toFixed(3);
            miCDRec.value = fetchedData[checkedName].mi.toFixed(3);
            corrCDRec.value = fetchedData[checkedName].corr.toFixed(3);
            fetchedData[checkedName].matrix_imputed.forEach((data: number[], index: number) => {
              //The push should theoretically ensure that we are just adding
              chartOptionsImputed.value.series.push(createSeries(index, data, 'CDRec: Series'));
            });
            imputedData.value = true;
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
            rmseIIM.value = fetchedData[checkedName].rmse.toFixed(3);
            maeIIM.value = fetchedData[checkedName].mae.toFixed(3);
            miIIM.value = fetchedData[checkedName].mi.toFixed(3);
            corrIIM.value = fetchedData[checkedName].corr.toFixed(3);
            fetchedData[checkedName].matrix_imputed.forEach((data: number[], index: number) => {
              chartOptionsImputed.value.series.push(createSeries(index, data, 'IIM: Series'));
            });
            imputedData.value = true;
          } else if (checkedName.toLowerCase() === 'mrnn') {
            if (!fetchedData[checkedName]) {
              const response = await axios.post('http://localhost:8000/api/mrnn/',
                  {
                    data_set: dataSet,
                    hidden_dim: hiddenDim.value,
                    learning_rate: learningRate.value,
                    iterations: iterationsMRNN.value,
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
            rmseMRNN.value = fetchedData[checkedName].rmse.toFixed(3);
            maeMRNN.value = fetchedData[checkedName].mae.toFixed(3);
            miMRNN.value = fetchedData[checkedName].mi.toFixed(3);
            corrMRNN.value = fetchedData[checkedName].corr.toFixed(3);
            fetchedData[checkedName].matrix_imputed.forEach((data: number[], index: number) => {
              chartOptionsImputed.value.series.push(createSeries(index, data, 'MRNN: Series'));
            });
            imputedData.value = true;
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
            rmseSTMVL.value = fetchedData[checkedName].rmse.toFixed(3);
            maeSTMVL.value = fetchedData[checkedName].mae.toFixed(3);
            miSTMVL.value = fetchedData[checkedName].mi.toFixed(3);
            corrSTMVL.value = fetchedData[checkedName].corr.toFixed(3);
            fetchedData[checkedName].matrix_imputed.forEach((data: number[], index: number) => {
              chartOptionsImputed.value.series.push(createSeries(index, data, 'ST-MVL: Series'));
            });
            imputedData.value = true;
          }
        }
      } catch (error) {
        console.log(error);
      } finally {
        loadingResults.value = false;
      }
    };

    const chartOptionsOriginal = ref(generateChartOptionsLarge('Original Data', 'Data'));
    const chartOptionsImputed = ref(generateChartOptionsLarge('Imputed Data', 'Data'));


    function clearFetchedData() {
      for (let key in fetchedData) {
        delete fetchedData[key];
      }
    }

    const submitForm = async () => {
      imputedData.value = false;
      clearFetchedData();
      await handleCheckboxChange();
    }


    // Define a new function that calls fetchData
    const handleDataSelectChange = () => {
      imputedData.value = false;
      clearFetchedData();
      fetchData();
    }
    // Watch for changes and call fetchData when it changes
    watch(dataSelect, handleDataSelectChange, {immediate: true});
    // TODO Missingness display
    // watch(missingRate, handleDataSelectChange, { immediate: true });

    return {
      submitForm,
      // Error Metrics
      rmseCDRec,
      maeCDRec,
      miCDRec,
      corrCDRec,
      rmseIIM,
      maeIIM,
      miIIM,
      corrIIM,
      rmseMRNN,
      maeMRNN,
      miMRNN,
      corrMRNN,
      rmseSTMVL,
      maeSTMVL,
      miSTMVL,
      corrSTMVL,
      // End Error Metrics
      chartOptionsOriginal,
      chartOptionsImputed,
      dataSelect,
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

