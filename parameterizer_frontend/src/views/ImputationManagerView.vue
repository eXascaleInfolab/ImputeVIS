<template>
  <main>
    <div v-if="loadingResults" class="d-flex justify-content-center mt-3">
      <div class="alert alert-info d-flex align-items-center">
        <div class="spinner-border text-primary me-3" role="status"></div>
        Loading...
      </div>
    </div>

    <form ref="ref_reload" @submit.prevent="submitForm">
      <div class="justify-content-right" style="padding: 10px; position: absolute; z-index: 100; right: 0;">
        <normalization-toggle v-model="normalizationMode"></normalization-toggle>
      </div>
    </form>

    <div class="mb-auto">
      <div class="col-lg-12">
        <div class="row me-1">
          <div class="col-lg-10">
            <highcharts v-if="imputedData" class="mb-3 pb-3" :options="chartOptionsImputed"></highcharts>
            <highcharts v-if="!imputedData" class="mb-3 pb-3" :options="chartOptionsOriginal"></highcharts>



            <div v-if="metricsCDRec || metricsIIM || metricsMRNN || metricsSTMVL" style="margin-left: 20%; margin-right: 20%; margin-top: 5%; width:60%; text-align:center;">
              <kiviat-display v-if="imputedData" :metrics="{
                CDRec :{rmse_1: rmseCDRec, mae_1: maeCDRec, mi_1: miCDRec, corr_1: corrCDRec },
                IIM :{ rmse_2: rmseIIM, mae_2: maeIIM, mi_2: miIIM, corr_2: corrIIM },
                MRNN :{ rmse_3: rmseMRNN, mae_3: maeMRNN, mi_3: miMRNN, corr_3: corrMRNN },
                STMVL :{ rmse_4: rmseSTMVL, mae_4: maeSTMVL, mi_4: miSTMVL, corr_4: corrSTMVL }
                }" />


              <div v-if="metricsCDRec || metricsIIM || metricsMRNN || metricsSTMVL || imputedData" class="mt-4" style="margin: 3%;">
                <div class="row">
                  <table class="table">
                    <thead>
                    <tr>
                      <th scope="col"></th>
                      <th scope="col" v-if="metricsCDRec">CDRec</th>
                      <th scope="col" v-if="metricsIIM">IIM</th>
                      <th scope="col" v-if="metricsMRNN">M-RNN</th>
                      <th scope="col" v-if="metricsSTMVL">ST-MVL</th>
                    </tr>
                    </thead>
                    <tbody>
                    <!-- Metrics Rows -->
                    <tr>
                      <th scope="row" v-if="rmseCDRec !== null && rmseCDRec !== ''">RMSE</th>
                      <td v-if="metricsCDRec">{{ rmseCDRec }}</td>
                      <td v-if="metricsIIM">{{ rmseIIM }}</td>
                      <td v-if="metricsMRNN">{{ rmseMRNN }}</td>
                      <td v-if="metricsSTMVL">{{ rmseSTMVL }}</td>
                    </tr>
                    <tr>
                      <th scope="row" v-if="maeCDRec !== null && maeCDRec !== ''">MAE</th>
                      <td v-if="metricsCDRec">{{ maeCDRec }}</td>
                      <td v-if="metricsIIM">{{ maeIIM }}</td>
                      <td v-if="metricsMRNN">{{ maeMRNN }}</td>
                      <td v-if="metricsSTMVL">{{ maeSTMVL }}</td>
                    </tr>
                    <tr>
                      <th scope="row" v-if="miCDRec !== null && miCDRec !== ''">MI</th>
                      <td v-if="metricsCDRec">{{ miCDRec }}</td>
                      <td v-if="metricsIIM">{{ miIIM }}</td>
                      <td v-if="metricsMRNN">{{ miMRNN }}</td>
                      <td v-if="metricsSTMVL">{{ miSTMVL }}</td>
                    </tr>
                    <tr>
                      <th scope="row" v-if="corrCDRec !== null && corrCDRec !== ''">CORR</th>
                      <td v-if="metricsCDRec">{{ corrCDRec }}</td>
                      <td v-if="metricsIIM">{{ corrIIM }}</td>
                      <td v-if="metricsMRNN">{{ corrMRNN }}</td>
                      <td v-if="metricsSTMVL">{{ corrSTMVL }}</td>
                    </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>






          </div>
          <div class="col-lg-2" style="margin-top: 50px;">
            <div class="row me-5">
              <div class="">
                <form ref="ref_missingvalues" @submit.prevent="submitForm">
                  <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames"/><br />
                  <missing-rate v-model="missingRate"/><br />
                </form>
              </div>
            </div>



            <form ref="ref_algos" @submit.prevent="submitForm">
              <div class="mt-4 me-6">
                <label for="ref_algos" class="form-label">Imputation Family :</label>
              <div class="row ms-1">
                <div class="col form-check ">
                  <input class="form-check-input" type="checkbox" value="CDRec" id="CDRec" v-model="checkedNames" checked >
                  <label class="form-check-label" for="CDRec">Matrix-based</label>
                </div>
                <div class="col form-check ">
                  <input class="form-check-input" type="checkbox" value="ST-MVL" id="ST-MVL" v-model="checkedNames">
                  <label class="form-check-label" for="ST-MVL">Pattern-based</label>
                </div>
              </div>
              <div>
                <div class="row ms-1">
                  <div class="col form-check " v-if="nns_checked == true" >
                    <input class="form-check-input" type="checkbox" value="M-RNN" id="MRNN" v-model="checkedNames">
                    <label class="form-check-label" for="MRNN">NNs-based</label>
                  </div>
                  <div class="col form-check " v-if="reg_checked == true">
                    <input class="form-check-input" type="checkbox" value="IIM" id="IIM" v-model="checkedNames">
                    <label class="form-check-label" for="IIM">Regression-based</label>
                  </div>
                </div>
              </div>
                <button type="submit" id="upload_algo" class="btn btn-success" style="margin-top:6px; width:100px; ">Upload</button>
              </div>


              <!-- Parameter Options -->
              <div class="mb-3"  data-toggle="tooltip" data-placement="top" style="margin-top:36px;"
                   title="Also impacts run-time, amount depends on algorithm.">
                <label for="parametrization" class="form-label">Parametrization:</label>
                <div class="custom-select">
                  <select class="form-control" name="paramOption" v-model="selectedParamOption">
                    <option value="recommended">Auto-ML (recommended)</option>
                    <option value="default">Default Params</option>
                    <option value="bayesian_optimization">Bayesian Optimization</option>
                    <option value="pso_optimization">Particle Swarm Optimization</option>
                    <option value="succesive_halving">Successive Halving</option>
                  </select>
                </div>
              </div>

              <div class="d-flexs mt-4 me-10" >
                <button type="submit" id="alpha_run" class="btn btn-primary" style="margin-top:36px;  width:100px; ">Impute</button>
                <button type="submit" id="delta_reset" class="btn btn-danger" style="margin-top:36px; margin-left : 10%; width:100px; ">Reset</button>
              </div>

              <div class="popup" id="popup">
                <label><input type="checkbox" id="nns_based" >NNs-based</label><br>
                <label><input type="checkbox" id="reg_based" >Regression-based</label><br>

                <input type="file" ref="fileInput" @change="uploadFile" style="margin-top:30px; margin-bottom:20px; width:145px;  "><br />

                <button type="submit" id="validate" className="btn btn-success" style="margin-top:25px; width:100px; ">Validate</button>
              </div>

            </form>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<style>
  .popup {
    display: none;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: #fff;
    padding: 40px; /* Increase padding for larger popup */
    border: 2px solid #ccc; /* Increase border size for larger popup */
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.4); /* Increase shadow for larger popup */
    z-index: 9999;
    font-size: 25px; /* Increase font size */
  }

  /* Style for checkboxes */
  .popup input[type="checkbox"] {
    transform: scale(2); /* Increase size of checkboxes */
    margin: 30px; /* Increase margin between checkbox and label */
  }
</style>

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
  generateChartOptions, generateChartOptionsHeight,
  generateChartOptionsLarge
} from "@/views/thesisUtils/utils";
import Metrics2Display from "@/views/components/Metrics2Display.vue";
import KiviatDisplay from './components/KiviatDisplay.vue';

// HighchartsBoost(Highcharts)

export default {
  components: {
    Metrics2Display,
    KiviatDisplay,
    NormalizationToggle,
    highcharts: Chart,
    DataSelect,
    MissingRate
  }, setup() {
    const route = useRoute()
    const dataSelect = ref(route.params.datasetName || 'batch10_eighth') // Default data is BAFU
    const normalizationMode = ref('Normal')
    let currentSeriesNames = []; // Names of series currently displayed
    const fetchedData = reactive({});
    let loadingResults = ref(false);
    const selectedParamOption = ref('recommended'); // Default option


    //CDRec Parameters
    const missingRate = ref('0'); // Default missing rate
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
    let groundtruthMatrix = [];
    const checkedNames = ref([]);
    const imputedData = ref(false); // Whether imputation has been carried out
    const nns_checked = ref(false);
    const reg_checked = ref(false);


    const obfuscatedColors = ["#7cb5ec", "#2b908f", "#a6c96a", "#876d5d", "#8f10ba", "#f7a35c", "#434348", "#f15c80", "#910000", "#8085e9", "#365e0c", "#90ed7d"];

    const fetchData = async () => {

      if (dataSelect.value !== "upload") {

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
          groundtruthMatrix = response.data.groundtruth;
          obfuscatedMatrix.forEach((data: number[], index: number) => {
            if (currentSeriesNames.length > 0) {
              chartOptionsOriginal.value.series[index] = createSeries(
                  index,
                  data,
                  dataSelect.value,
                  currentSeriesNames[index],
                  obfuscatedColors[index]
              );
            } else {
              chartOptionsOriginal.value.series[index] = createSeries(
                  index,
                  data,
                  dataSelect.value,
                  undefined,
                  obfuscatedColors[index]
              );
            }
          });
          if (missingRate.value != "0") {
            // Adding ground truth series to the chart
            groundtruthMatrix.forEach((data: number[], index: number) => {
              chartOptionsOriginal.value.series.push(createSeries(
                  index,
                  data,
                  dataSelect.value,
                  currentSeriesNames[index] + " (MV)",
                  'dash',
                  1,
                  obfuscatedColors[index]
              ));
            });
          }

        } catch (error) {
          console.error(error);
        } finally {
          loadingResults.value = false;
        }
      }
    }

    const fetchParameters = async () => {
      if (dataSelect.value !== "upload") {
        if (selectedParamOption.value !== 'default') {
          try {
            const dataAbbreviation = getCategory(dataSelect.value);
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

    if (dataSelect.value !== "upload") {

      // Clear the existing series
      // chartOptionsImputed.value.series = [];
      loadingResults.value = true;
      imputedData.value = false;
      chartOptionsImputed.value.series.splice(0, chartOptionsImputed.value.series.length)
      chartOptionsOriginal.value.series.splice(0, chartOptionsOriginal.value.series.length)
      await fetchParameters();
      clearErrorMetrics();

      try {
        for (let checkedName of checkedNames.value) {
          const displayImputation = true
          let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;

          obfuscatedMatrix.forEach((data: number[], index: number) => {
            if (currentSeriesNames.length > 0) {
              chartOptionsImputed.value.series[index] = createSeries(
                  index,
                  data,
                  dataSelect.value,
                  currentSeriesNames[index],
                  obfuscatedColors[index]
              );
            } else {
              chartOptionsImputed.value.series[index] = createSeries(
                  index,
                  data,
                  dataSelect.value,
                  undefined,
                  obfuscatedColors[index]
              );
            }
          });
          // Adding ground truth series to the chart
          groundtruthMatrix.forEach((data: number[], index: number) => {
            chartOptionsImputed.value.series.push(createSeries(
                index,
                data,
                dataSelect.value,
                currentSeriesNames[index] + " (MV)",
                'dash',
                1,
                obfuscatedColors[index]
            ));
          });

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
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], groundtruthMatrix[index], chartOptionsImputed.value, dataSelect.value, "CDRec: " + currentSeriesNames[index]));
                } else {
                  chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value, "CDRec: " + currentSeriesNames[index]));
                }
              } else {
                if (displayImputation) {
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], groundtruthMatrix[index], chartOptionsImputed.value, dataSelect.value, "CDRec: " + index));
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
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], groundtruthMatrix[index], chartOptionsImputed.value, dataSelect.value, "IIM: " + currentSeriesNames[index]));
                } else {
                  chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value, "IIM: " + currentSeriesNames[index]));
                }
              } else {
                if (displayImputation) {
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], groundtruthMatrix[index], chartOptionsImputed.value, dataSelect.value, "IIM: " + index));
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
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], groundtruthMatrix[index], chartOptionsImputed.value, dataSelect.value, "MRNN: " + currentSeriesNames[index]));
                } else {
                  chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value, "MRNN: " + currentSeriesNames[index]));
                }
              } else {
                if (displayImputation) {
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], groundtruthMatrix[index], chartOptionsImputed.value, dataSelect.value, "MRNN: " + index));
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
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], groundtruthMatrix[index], chartOptionsImputed.value, dataSelect.value, "ST-MVL: " + currentSeriesNames[index]));
                } else {
                  chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value, "ST-MVL: " + currentSeriesNames[index]));
                }
              } else {
                if (displayImputation) {
                  chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], groundtruthMatrix[index], chartOptionsImputed.value, dataSelect.value, "ST-MVL: " + index));
                } else {
                  chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value));
                }
              }
            });

            imputedData.value = true;
          }
        }


      } catch (error) {
        console.error(error);
      } finally {
        loadingResults.value = false;
      }
    }
    };

    const chartOptionsOriginal = ref(generateChartOptions('', 'Data'));
    const chartOptionsImputed = ref(generateChartOptions('', 'Data'));


    function showPopup()
    {
      document.getElementById('popup').style.display = 'block';
    }

    function closePopup()
    {
        document.getElementById('popup').style.display = 'none';
    }

    function printCheckedValues()
    {
        var nns_checkedv = document.getElementById('nns_based').checked;
        var reg_checkedv = document.getElementById('reg_based').checked;
        //var openFileChecked = document.getElementById('open_file_checkbox').checked;

        console.log("Pre-implemented checked nns_checked :", nns_checkedv);
        console.log("Pre-implemented checked reg_checked:", reg_checkedv);

        nns_checked.value = nns_checkedv
        reg_checked.value = reg_checkedv

    }


    function clearFetchedData()
    {
      for (let key in fetchedData)
      {
        delete fetchedData[key];
      }
    }

    function getCategory(dataSelectValue: string): string
    {
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

      if (document.activeElement.id === "alpha_run")
      {
        imputedData.value = false;
        clearFetchedData();
        clearErrorMetrics();
        await handleCheckboxChange();
      }
      else if (document.activeElement.id === "upload_algo")
      {
        showPopup();
      }
       else if (document.activeElement.id === "validate")
      {
        printCheckedValues();
        closePopup();
      }
      else if (document.activeElement.id === "delta_reset")
      {
        location.reload();
      }
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
      try
      {
        await fetchParameters();
        await submitForm();
      }
      catch (error)
      {
        console.error("Error handling parameter selection:", error);
      }
    }
      const handleNormalizationModeChange = () => {
      if (imputedData.value == true)
      {
          fetchData();
          submitForm();
      }
      else
      {
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
      loadingResults,
      nns_checked,
      reg_checked
    }
  }
}


</script>
<style scoped>
.sidebar {
  margin-left: 35px; /* Change this value to increase or decrease the margin */
}
</style>

