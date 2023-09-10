<template>
  <main>
    <!--  <h3 class="mb-4 text-center">Compare Algorithms</h3>-->

    <div v-if="loadingResults" class="d-flex justify-content-center mt-3">
      <div class="alert alert-info d-flex align-items-center">
        <div class="spinner-border text-primary me-3" role="status"></div>
        Loading...
      </div>
    </div>

    <div class="mb-auto">
      <div class="col-lg-12">
        <div class="row me-1">
          <div class="col-lg-10">
            <highcharts v-if="imputedData" class="mb-5 pb-5" :options="chartOptionsImputed"></highcharts>
            <highcharts v-if="!imputedData" :options="chartOptionsOriginal"></highcharts>
          </div>
          <div class="col-lg-2">
            <div class="row me-5">
              <div class="">
                <form @submit.prevent="submitForm">
                  <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames"/>
                  <normalization-toggle v-model="normalizationMode"></normalization-toggle>
                  <missing-rate v-model="missingRate"/>
                </form>
              </div>
            </div>
            <form @submit.prevent="submitForm">
              <div class="mt-4 me-5">
                <h4>Select algorithm(s)</h4>
                <div class="row ms-2">
                  <div class="col form-check ">
                    <input class="form-check-input" type="checkbox" value="CDRec" id="CDRec" v-model="checkedNames">
<!--                           @change="handleCheckboxChange"-->
                    <label class="form-check-label" for="CDRec">
                      CDRec
                    </label>
                  </div>
                  <div class="col form-check ">
                    <input class="form-check-input" type="checkbox" value="IIM" id="IIM" v-model="checkedNames">
<!--                           @change="handleCheckboxChange"-->
                    <label class="form-check-label" for="IIM">
                      IIM
                    </label>
                  </div>
                </div>
                <div class="row ms-2">
                  <div class="col form-check ">
                    <input class="form-check-input" type="checkbox" value="M-RNN" id="MRNN" v-model="checkedNames">
<!--                           @change="handleCheckboxChange"-->
                    <label class="form-check-label" for="MRNN">
                      M-RNN
                    </label>
                  </div>
                  <div class="col form-check ">
                    <input class="form-check-input" type="checkbox" value="ST-MVL" id="ST-MVL" v-model="checkedNames">
<!--                           @change="handleCheckboxChange"-->
                    <label class="form-check-label" for="ST-MVL">
                      ST-MVL
                    </label>
                  </div>
                </div>

              </div>
              <!-- Parameter Options -->
              <div class="mt-4 me-5">
                <h4>Parametrization</h4>
                <select class="form-control" name="paramOption" v-model="selectedParamOption">
                  <option value="recommended">Recommended</option>
                  <option value="default">Default</option>
                  <option value="bayesian_optimization">Bayesian Optimization</option>
                  <option value="pso_optimization">Particle Swarm Optimization</option>
                  <option value="succesive_halving">Successive Halving</option>
                </select>
              </div>
              <div class="d-flex justify-content-center mt-4 me-5">
                <button type="submit" class="btn btn-primary align-center">Impute</button>
              </div>
            </form>
            <div v-if="metricsCDRec" class="mt-4">
              <div class="row">
                <div class="col-xs">
                  <h6 v-if="rmseCDRec !== null && rmseCDRec !== ''"> CDRec RMSE: {{ rmseCDRec }}</h6>
                  <h6 v-if="maeCDRec !== null && maeCDRec !== ''"> CDRec MAE: {{ maeCDRec }}</h6>
                  <h6 v-if="miCDRec !== null && miCDRec !== ''"> CDRec MI: {{ miCDRec }}</h6>
                  <h6 v-if="corrCDRec !== null && corrCDRec !== ''"> CDRec CORR: {{ corrCDRec }}</h6>
                </div>
              </div>
            </div>
            <div v-if="metricsIIM" class="mt-4">
              <div class="row">
                <div class="col-xs">
                  <h6 v-if="rmseIIM !== null && rmseIIM !== ''"> IIM RMSE: {{ rmseIIM }}</h6>
                  <h6 v-if="maeIIM !== null && maeIIM !== ''"> IIM MAE: {{ maeIIM }}</h6>
                  <h6 v-if="miIIM !== null && miIIM !== ''"> IIM MI: {{ miIIM }}</h6>
                  <h6 v-if="corrIIM !== null && corrIIM !== ''"> IIM CORR: {{ corrIIM }}</h6>
                </div>
              </div>
            </div>
            <div v-if="metricsMRNN" class="mt-4">
              <div class="row">
                <div class="col-xs">
                  <h6 v-if="rmseMRNN !== null && rmseMRNN !== ''"> M-RNN RMSE: {{ rmseMRNN }}</h6>
                  <h6 v-if="maeMRNN !== null && maeMRNN !== ''"> M-RNN MAE: {{ maeMRNN }}</h6>
                  <h6 v-if="miMRNN !== null && miMRNN !== ''"> M-RNN MI: {{ miMRNN }}</h6>
                  <h6 v-if="corrMRNN !== null && corrMRNN !== ''"> M-RNN CORR: {{ corrMRNN }}</h6>
                </div>
              </div>
            </div>
            <div v-if="metricsSTMVL" class="mt-4">
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
  </main>
</template>

<script lang="ts">
import {ref, watch, reactive, shallowReactive} from 'vue';
import { useRoute } from 'vue-router'
import DataSelect from './components/DataSelect.vue';
import MissingRate from './components/MissingRate.vue';
import NormalizationToggle from './components/NormalizationToggle.vue'
import axios from 'axios';
import {Chart} from 'highcharts-vue'
import Highcharts from 'highcharts'
import HighchartsBoost from "highcharts/modules/boost";
import {IIM_DEFAULTS, CDREC_DEFAULTS, MRNN_DEFAULTS, STMVL_DEFAULTS} from './thesisUtils/defaultParameters';
import {
  createSegmentedSeries,
  createSeries,
  generateChartOptions,
  generateChartOptionsLarge
} from "@/views/thesisUtils/utils";

// HighchartsBoost(Highcharts)

export default {
  components: {
    NormalizationToggle,
    highcharts: Chart,
    DataSelect,
    MissingRate
  }, setup() {
    const route = useRoute()
    const dataSelect = ref(route.params.datasetName || 'climate_eighth') // Default data is BAFU
    const normalizationMode = ref('Normal')
    let currentSeriesNames = []; // Names of series currently displayed
    const fetchedData = reactive({});
    let loadingResults = ref(false);
    const selectedParamOption = ref('recommended'); // Default option


    //CDRec Parameters
    const missingRate = ref('10'); // Default missing rate
    let truncationRank = '1' // Default truncation rank is 1, 0 means detect truncation automatically
    let epsilon = 'E-6'; // Default epsilon is E-6
    let iterations = (500); // Default number of iterations is 1000
    const rmseCDRec = ref(null);
    const maeCDRec = ref(null);
    const miCDRec = ref(null);
    const corrCDRec = ref(null);
    const metricsCDRec = ref(false);

    //IIM Parameters
    let numberSelect = 1; // Default selected learning neighbors is 1
    let typeSelect = ''; // Default selected type is "Normal", denoted by an empty string
    const rmseIIM = ref(null);
    const maeIIM = ref(null);
    const miIIM = ref(null);
    const corrIIM = ref(null);
    const metricsIIM = ref(false);

    // M-RNN Parameters
    let learningRate = 0.01; // Default learning rate is 0.01
    let hiddenDim = 10; // Default hidden dimension size is 10
    let iterationsMRNN = 500; // Default number of iterations is 1000
    let keepProb = 0.5; // Default keep probability is 0.5
    let seqLen = 7; // Default sequence length is 7
    const rmseMRNN = ref(null);
    const maeMRNN = ref(null);
    const miMRNN = ref(null);
    const corrMRNN = ref(null);
    const metricsMRNN = ref(false);

    // ST-MVL Parameters
    let windowSize = '2'; // Default window size is 2
    let gamma = '0.5' // Default smoothing parameter gamma is 0.5, min 0.0, max 1.0
    let alpha = '2' // Default power for spatial weight (alpha) is 2, must be larger than 0.0
    const rmseSTMVL = ref(null);
    const maeSTMVL = ref(null);
    const miSTMVL = ref(null);
    const corrSTMVL = ref(null);
    const metricsSTMVL = ref(false);

    let obfuscatedMatrix = [];
    const checkedNames = ref([]);
    const imputedData = ref(false); // Whether imputation has been carried out


    const fetchData = async () => {
      try {
        loadingResults.value = true;
        let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
        const response = await axios.post('http://localhost:8000/api/fetchData/',
            {
              data_set: dataSet,
              normalization: normalizationMode.value
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

        obfuscatedMatrix = response.data.matrix;
        response.data.matrix.forEach((data: number[], index: number) => {
          if (currentSeriesNames.length > 0) {
            chartOptionsOriginal.value.series[index] = createSeries(index, data, dataSelect.value, currentSeriesNames[index]);
          } else {
            chartOptionsOriginal.value.series[index] = createSeries(index, data, dataSelect.value);
          }
        });
      } catch (error) {
        console.error(error);
      } finally {
        loadingResults.value = false;
      }
    }

    const fetchParameters = async () => {
      if (selectedParamOption.value !== 'Default') {
        try {
          const dataAbbreviation = getCategory(dataSelect.value);
          console.log("dataAbbreviation: ", dataAbbreviation)
          let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
          const response = await axios.post('http://localhost:8000/api/fetchParameters/',
              {
                data_set: dataAbbreviation,
                normalization: normalizationMode.value,
                param_options: selectedParamOption.value
              },
              {
                headers: {
                  'Content-Type': 'application/text',
                }
              }
          );
          const parameters = response.data.params;

          // CDRec Parameters
          truncationRank = parameters['cdrec'][dataAbbreviation].best_params.rank || truncationRank;
          epsilon = parameters['cdrec'][dataAbbreviation].best_params.eps || epsilon;
          iterations = parameters['cdrec'][dataAbbreviation].best_params.iters || iterations;

          // IIM Parameters
          numberSelect = parameters['iim'][dataAbbreviation].best_params.learning_neighbours || numberSelect;
          // typeSelect = parameters['iim'][dataAbbreviation].best_params.type_select || typeSelect;

          // M-RNN Parameters
          learningRate = parameters['mrnn'][dataAbbreviation].best_params.learning_rate || learningRate;
          hiddenDim = parameters['mrnn'][dataAbbreviation].best_params.hidden_dim || hiddenDim;
          iterationsMRNN = parameters['mrnn'][dataAbbreviation].best_params.iterations || iterationsMRNN;
          keepProb = parameters['mrnn'][dataAbbreviation].best_params.keep_prob || keepProb;
          // seqLen = parameters['iim'][dataAbbreviation].best_params.seq_len || seqLen;

          // ST-MVL Parameters
          windowSize = parameters['stmvl'][dataAbbreviation].best_params.window_size || windowSize;
          gamma = parameters['stmvl'][dataAbbreviation].best_params.gamma || gamma;
          alpha = parameters['stmvl'][dataAbbreviation].best_params.alpha || alpha;

          // }
        } catch (error) {
          console.error(error);
        }
      } else {
        // Set parameters to default (author's choice)
        truncationRank = String(CDREC_DEFAULTS.reductionValue);
        epsilon = String(CDREC_DEFAULTS.epsilon);
        iterations = CDREC_DEFAULTS.iterations;

        // IIM Parameters
        numberSelect = IIM_DEFAULTS.learningNeighbors;
        // typeSelect.value = 'mean';

        // M-RNN Parameters
        learningRate = MRNN_DEFAULTS.learningRate;
        hiddenDim = MRNN_DEFAULTS.hiddenDim;
        iterationsMRNN = MRNN_DEFAULTS.iterations;
        keepProb = MRNN_DEFAULTS.keepProb;
        // seqLen.value = 7;

        // ST-MVL Parameters
        windowSize = String(STMVL_DEFAULTS.windowSize);
        gamma = String(STMVL_DEFAULTS.gamma);
        alpha = String(STMVL_DEFAULTS.alpha);
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
      await fetchParameters();
      clearErrorMetrics();

      try {
        for (let checkedName of checkedNames.value) {
          // TODO Using displayImputation = false as when using multiple algorithms, performance is really, really slow.
          const displayImputation =  missingRate.value != '60' && missingRate.value != '80'
          let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
          if (checkedName.toLowerCase() === 'cdrec') {
            if (!fetchedData[checkedName]) {
              const response = await axios.post('http://localhost:8000/api/cdrec/',
                  {
                    data_set: dataSet,
                    normalization: normalizationMode.value,
                    truncation_rank: truncationRank,
                    epsilon: epsilon,
                    iterations: iterations,
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
            metricsCDRec.value = true;

            // Create a new array for the new series data
            const newSeriesData = [];
            fetchedData[checkedName].matrix_imputed.forEach((data: number[], index: number) => {
              //The push should theoretically ensure that we are just adding
              if (currentSeriesNames.length > 0 && currentSeriesNames[index]) {
                if (displayImputation) {
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value, dataSelect.value, "CDRec: " + currentSeriesNames[index]));
                } else {
                  chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value, "CDRec: " + currentSeriesNames[index]));
                }
              } else {
                if (displayImputation) {
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value, dataSelect.value, "CDRec: " + index));
                } else {
                  chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value));
                }
              }
            });
            imputedData.value = true;
          } else if (checkedName.toLowerCase() == 'iim') {
            if (!fetchedData[checkedName]) {
              const formattedAlgCode = `iim ${numberSelect}${typeSelect}`;
              const response = await axios.post('http://localhost:8000/api/iim/',
                  {
                    data_set: dataSet,
                    normalization: normalizationMode.value,
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
            metricsIIM.value = true;

            fetchedData[checkedName].matrix_imputed.forEach((data: number[], index: number) => {
              if (currentSeriesNames.length > 0 && currentSeriesNames[index]) {
                if (displayImputation) {
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value, dataSelect.value, "IIM: " + currentSeriesNames[index]));
                } else {
                  chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value, "IIM: " + currentSeriesNames[index]));
                }
              } else {
                if (displayImputation) {
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value, dataSelect.value, "IIM: " + index));
                } else {
                  chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value));
                }
              }
            });
            imputedData.value = true;
          } else if (checkedName.toLowerCase() === 'm-rnn') {
            if (!fetchedData[checkedName]) {
              const response = await axios.post('http://localhost:8000/api/mrnn/',
                  {
                    data_set: dataSet,
                    normalization: normalizationMode.value,
                    hidden_dim: hiddenDim,
                    learning_rate: learningRate,
                    iterations: iterationsMRNN,
                    keep_prob: keepProb,
                    seq_len: seqLen
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
            metricsMRNN.value = true;

            fetchedData[checkedName].matrix_imputed.forEach((data: number[], index: number) => {
              if (currentSeriesNames.length > 0 && currentSeriesNames[index]) {
                if (displayImputation) {
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value, dataSelect.value, "MRNN: " + currentSeriesNames[index]));
                } else {
                  chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value, "MRNN: " + currentSeriesNames[index]));
                }
              } else {
                if (displayImputation) {
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value, dataSelect.value, "MRNN: " + index));
                } else {
                  chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value));
                }
              }
            });
            imputedData.value = true;
          } else if (checkedName.toLowerCase() === 'st-mvl') {
            if (!fetchedData[checkedName]) {
              const response = await axios.post('http://localhost:8000/api/stmvl/',
                  {
                    data_set: dataSet,
                    normalization: normalizationMode.value,
                    window_size: windowSize,
                    gamma: gamma,
                    alpha: alpha,
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
            metricsSTMVL.value = true;

            fetchedData[checkedName].matrix_imputed.forEach((data: number[], index: number) => {
              if (currentSeriesNames.length > 0 && currentSeriesNames[index]) {
                if (displayImputation) {
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value, dataSelect.value, "ST-MVL: " + currentSeriesNames[index]));
                } else {
                  chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value, "ST-MVL: " + currentSeriesNames[index]));
                }
              } else {
                if (displayImputation) {
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value, dataSelect.value, "ST-MVL: " + index));
                } else {
                  chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value));
                }
              }
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

    function getCategory(dataSelectValue: string): string {
      if (dataSelectValue.startsWith('BAFU')) {
        return 'bafu';
      } else if (dataSelectValue.startsWith('cl2fullLarge')) {
        return 'chlorine';
      } else if (dataSelectValue.startsWith('climate')) {
        return 'climate';
      } else if (dataSelectValue.startsWith('batch10')) {
        return 'drift';
      } else if (dataSelectValue.startsWith('meteo')) {
        return 'meteo';
      } else {
        // If no match is found, return a default value (bafu) or throw an error
        return 'bafu';
      }
    }

    const submitForm = async () => {
      imputedData.value = false;
      clearFetchedData();
      await handleCheckboxChange();
    }


    // Define a new function that calls fetchData
    const handleDataSelectChange = async () => {
      try {
        imputedData.value = false;
        // TODO Function to get the parameters for selected algorithm
        clearFetchedData();
        await fetchData();
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    }

    const updateSeriesNames = (newSeriesNames) => {
      currentSeriesNames = newSeriesNames;
    };

    const handleParamSelectChange = async () => {
      try {
        await fetchParameters();
        await submitForm();
      } catch (error) {
        console.error("Error handling parameter selection:", error);
      }
    }
      const handleNormalizationModeChange = () => {
      if (imputedData.value == true) {
          submitForm();
      } else {
          handleDataSelectChange();
      }
    }

    // Watch for changes and call fetchData when it changes
    watch([dataSelect, missingRate], handleDataSelectChange, {immediate: true});
        watch(normalizationMode, handleNormalizationModeChange, {immediate: true});
    // Watch for changes and call fetchData when it changes
    // watch(selectedParamOption, handleParamSelectChange, {immediate: true});


    return {
      submitForm,
      // Error Metrics
      rmseCDRec,
      maeCDRec,
      miCDRec,
      corrCDRec,
      metricsCDRec,
      rmseIIM,
      maeIIM,
      miIIM,
      corrIIM,
      metricsIIM,
      rmseMRNN,
      maeMRNN,
      miMRNN,
      corrMRNN,
      metricsMRNN,
      rmseSTMVL,
      maeSTMVL,
      miSTMVL,
      corrSTMVL,
      metricsSTMVL,
      // End Error Metrics
      chartOptionsOriginal,
      chartOptionsImputed,
      dataSelect,
      normalizationMode,
      updateSeriesNames,
      missingRate,
      imputedData,
      checkedNames,
      handleCheckboxChange,
      // handleParamSelectChange,
      selectedParamOption,
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

