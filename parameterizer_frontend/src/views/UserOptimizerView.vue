<template>
  <!-- <h3 class="mb-4 text-center">User-Defined Optimizer</h3> -->

  <div class="d-flex mb-auto">
    <div class="col-lg-10">

      <div v-if="loadingResults" class="d-flex justify-content-center mt-3">
        <div class="alert alert-info d-flex align-items-center">
          <div class="spinner-border text-primary me-3" role="status"></div>
          Determining resulting imputation...
        </div>
      </div>

      <highcharts v-if="imputedData" :options="chartOptionsImputed"></highcharts>

      <div v-if="loadingParameters" class="d-flex justify-content-center mt-3">
        <div class="alert alert-info d-flex align-items-center">
          <div class="spinner-border text-primary me-3" role="status"></div>
          Determining optimal parameters...
        </div>
      </div>

      <br />

      <div class="row">
        <div class="col-md-12">
          <form v-if="optimalParametersDetermined && imputedData && algorithmChoice == 'cdrec'" @submit.prevent="submitFormCustom">
            <div class="row">
              <div class="col-md-6" style="padding: 20px; height: 100%;">
                <h5 style="text-align: center; margin-bottom: 20px;">Optimal Parameters</h5>
                <div class="row"  style="margin:5%;">
                  <div class="col-12" style="height: 100%;">
                    <!-- 1st table taking 100% width and matching the kiviat height -->
                    <table class="table table-bordered" style="width: 100%; height: 100%;">
                      <thead class="thead-dark">
                      <tr>
                        <th scope="col" style="width: 50%;">Parameter</th>
                        <th scope="col" style="width: 50%;">Value</th>
                      </tr>
                      </thead>
                      <tbody>
                      <tr>
                        <td>Reduction Rank</td>
                        <td>{{ truncationRank }}</td>
                      </tr>
                      <tr>
                        <td>Threshold for Difference</td>
                        <td>{{ epsilon }}</td>
                      </tr>
                      <tr>
                        <td>Number of Iterations</td>
                        <td>{{ iterations }}</td>
                      </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              <div class="col-md-5" style="padding: 20px; text-align: center; margin-left: 5%;">
                <h5 style="text-align: center; margin-bottom: 20px;">Metrics</h5>
                <metrics-2-display v-if="imputedData" :metrics="metrics"></metrics-2-display>
              </div>
            </div>
          </form>
        </div>
      </div>








      <div class="row">
        <div class="col-md-12">
          <form v-if="optimalParametersDetermined && imputedData && algorithmChoice == 'stmvl'" @submit.prevent="submitFormCustom">
            <div class="row">
              <div class="col-md-6" style="padding: 20px; height: 100%; margin-top:100px;">
                <h5 style="text-align: center; margin-bottom: 20px;">Optimal Parameters</h5>
                <div class="row"  style="margin:5%;">
                  <div class="col-12" style="height: 100%;">
                    <!-- 1st table taking 100% width and matching the kiviat height -->
                    <table class="table table-bordered">
                      <thead class="thead-dark">
                      <tr>
                        <th scope="col" style="width: 50%">Parameter</th>
                        <th scope="col" style="width: 50%">Value</th>
                      </tr>
                      </thead>
                      <tbody>
                      <tr>
                        <td>Window Size</td>
                        <td>{{ windowSize }}</td>
                      </tr>
                      <tr>
                        <td>Smoothing Parameter (γ)</td>
                        <td>{{ parseFloat(gamma).toFixed(5) }}</td>
                      </tr>

                      <tr>
                        <td>Power for Spatial Weight (α)</td>
                        <td>{{ alpha }}</td>
                      </tr>
                      </tbody>
                    </table>
                  </div>
                  <div class="col-12" style="margin-top: 120px;;">
                    <h5 style="text-align: center; margin-bottom: 20px;">Metrics</h5>
                    <metrics-2-display v-if="imputedData" :metrics="metrics"></metrics-2-display>
                  </div>
                </div>
              </div>
              <div class="col-md-5" style="padding: 20px; text-align: center; margin-left: 5%;">
                <metrics2-kiviat-display v-if="imputedData" :metrics="metrics" style="height: 100%;"></metrics2-kiviat-display>
              </div>
            </div>
          </form>
        </div>
      </div>






      <div class="row">
        <div class="col-md-12">
          <form v-if="optimalParametersDetermined && imputedData && algorithmChoice == 'iim'" @submit.prevent="submitFormCustom">
            <div class="row">
              <div class="col-md-6" style="padding: 20px; height: 100%; margin-top:100px;">
                <h5 style="text-align: center; margin-bottom: 20px;">Optimal Parameters</h5>
                <div class="row"  style="margin:5%;">
                  <div class="col-12" style="height: 100%;">
                    <!-- 1st table taking 100% width and matching the kiviat height -->
                    <table class="table table-bordered">
                      <thead class="thead-dark">
                      <tr>
                        <th scope="col" style="width: 50%">Parameter</th>
                        <th scope="col" style="width: 50%">Value</th>
                      </tr>
                      </thead>
                      <tbody>
                      <tr>
                        <td>Number of Iterations</td>
                        <td>{{ numberSelect }}</td>
                      </tr>
                      </tbody>
                    </table>
                  </div>
                  <div class="col-12" style="margin-top: 120px;;">
                    <h5 style="text-align: center; margin-bottom: 20px;">Metrics</h5>
                    <metrics-2-display v-if="imputedData" :metrics="metrics"></metrics-2-display>
                  </div>
                </div>
              </div>
              <div class="col-md-5" style="padding: 20px; text-align: center; margin-left: 5%;">
                <metrics2-kiviat-display v-if="imputedData" :metrics="metrics" style="height: 100%;"></metrics2-kiviat-display>
              </div>
            </div>
          </form>
        </div>
      </div>




      <div class="row">
        <div class="col-md-12">
          <form v-if="optimalParametersDetermined && imputedData && algorithmChoice == 'mrnn'" @submit.prevent="submitFormCustom">
            <div class="row">
              <div class="col-md-6" style="padding: 20px; height: 100%; margin-top:100px;">
                <h5 style="text-align: center; margin-bottom: 20px;">Optimal Parameters</h5>
                <div class="row"  style="margin:5%;">
                  <div class="col-12" style="height: 100%;">
                    <!-- 1st table taking 100% width and matching the kiviat height -->
                    <table class="table table-bordered">
                      <thead class="thead-dark">
                      <tr>
                        <th scope="col" style="width: 50%">Parameter</th>
                        <th scope="col" style="width: 50%">Value</th>
                      </tr>
                      </thead>
                      <tbody>
                      <tr>
                        <td>Learning Rate</td>
                        <td>{{ parseFloat(learningRate).toFixed(6) }}</td>
                      </tr>
                      <tr>
                        <td>Hidden Dimension Size</td>
                        <td>{{ hiddenDim }}</td>
                      </tr>
                      <tr>
                        <td>Number of Iterations</td>
                        <td>{{ iterations }}</td>
                      </tr>
                      <tr>
                        <td>Keep Rate</td>
                        <td>{{ parseFloat(keepProb).toFixed(4) }}</td>
                      </tr>
                      </tbody>
                    </table>
                  </div>
                  <div class="col-12" style="margin-top: 120px;;">
                    <h5 style="text-align: center; margin-bottom: 20px;">Metrics</h5>
                    <metrics-2-display v-if="imputedData" :metrics="metrics"></metrics-2-display>
                  </div>
                </div>
              </div>
              <div class="col-md-5" style="padding: 20px; text-align: center; margin-left: 5%;">
                <metrics2-kiviat-display v-if="imputedData" :metrics="metrics" style="height: 100%;"></metrics2-kiviat-display>
              </div>
            </div>
          </form>
        </div>
      </div>



      <highcharts v-if="!imputedData"  :options="chartOptionsOriginal"></highcharts>

    </div>
    <div class="col-lg-2" style="margin-top: 80px">
      <form @submit.prevent="submitForm" class="sidebar me-3">

        <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames"/>
        <algorithm-choice v-model="algorithmChoice"  @submit.prevent="submitFormCustom"  />

        <optimization-select v-model="optimizationSelect" :natehidden=nate_hidden @parametersChanged="handleParametersChanged"/>


        <br/>
        <button type="submit" class="btn btn-primary">Optimize</button>
      </form>
    </div>


    <form ref="ref_reload" @submit.prevent="submitForm">
      <div class="justify-content-right" style="padding: 10px; position: absolute; z-index: 200; right: 60px; top: 68px;">
        <normalization-toggle v-model="normalizationMode" ></normalization-toggle>
      </div>
      <div class="justify-content-right" style="padding: 10px; position: absolute; z-index: 100; right: 0px; top: 63px;">
        <button type="submit" id="delta_reset" class="btn align-center" style="background-color: #f0f0f0; padding: 6px;">
          <svg xmlns="http://www.w3.org/2000/svg" width="1.5em" height="1.5em" viewBox="-2 0 24 24" style="margin-top: -2px; margin-right: 4px;">
            <path fill="currentColor" d="M2 12a9 9 0 0 0 9 9c2.39 0 4.68-.94 6.4-2.6l-1.5-1.5A6.706 6.706 0 0 1 11 19c-6.24 0-9.36-7.54-4.95-11.95C10.46 2.64 18 5.77 18 12h-3l4 4h.1l3.9-4h-3a9 9 0 0 0-18 0"/>
          </svg>
        </button>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import {ref, watch, computed} from 'vue';
import DataSelectOptimization from './components/DataSelectOptimization.vue';
import AlgorithmChoice from './components/AlgorithmChoice.vue';
import Metrics2Display from './components/Metrics2Display.vue';
import MissingRate from './components/MissingRate.vue';
import NormalizationToggle from './components/NormalizationToggleOptimization.vue'
import OptimizationSelect from './components/OptimizationSelect.vue';
import axios from 'axios';
import {Chart} from 'highcharts-vue'

import {
  createSegmentedSeries,
  createSeries,
  generateChartOptions, generateChartOptionsHeight,
  generateChartOptionsLarge
} from "@/views/thesisUtils/utils";
import ScenarioMissingValues from "@/views/components/ScenarioMissingValues.vue";
import optimizationSelect from "@/views/components/OptimizationSelect.vue";
import DataSelect from "@/views/components/DataSelect.vue";
import Metrics2KiviatDisplay from "@/views/components/Metrics2KiviatDisplay.vue";

// HighchartsBoost(Highcharts)

export default {
  computed: {
    optimizationSelect() {
      return optimizationSelect
    }
  },
  components: {
    Metrics2KiviatDisplay,
    DataSelect,
    ScenarioMissingValues,
    highcharts: Chart,
    DataSelectOptimization,
    AlgorithmChoice,
    Metrics2Display,
    MissingRate,
    NormalizationToggle,
    OptimizationSelect
  },
  setup() {
    const optimizationParameters = ref({}); // To store the optimization parameters received from the child component
    const dataSelect = ref('batch10_eighth') // Default data
    const algorithmChoice = ref('cdrec')
    const normalizationMode = ref('Normal')
    let currentSeriesNames = []; // Names of series currently displayed
    const missingRate = ref('10'); // Default missing rate

    const truncationRank = ref('1') // Default truncation rank is 1, 0 means detect truncation automatically
    const epsilon = ref('E-6'); // Default epsilon is E-6
    const iterations = ref(500); // Default number of iterations is 1000

    const windowSize = ref('2'); // Default window size is 2
    const gamma = ref('0.5') // Default smoothing parameter gamma is 0.5, min 0.0, max 1.0
    const alpha = ref('2') // Default power for spatial weight (alpha) is 2, must be larger than 0.0

    const numberSelect = ref(1); // Default selected learning neighbors is 1
    const typeSelect = ref(''); // Default selected type is "Normal", denoted by an empty string

    const nate_hidden = false;

    const learningRate = ref(0.01); // Default learning rate is 0.01
    const hiddenDim = ref(10); // Default hidden dimension size is 10
    const keepProb = ref(0.5); // Default keep probability is 0.5
    const seqLen = ref(7); // Default sequence length is 7

    const rmse = ref(null);
    const mae = ref(null);
    const mi = ref(null);
    const corr = ref(null);
    const metrics = computed(() => ({rmse: rmse.value, mae: mae.value, mi: mi.value, corr: corr.value}));
    const imputedData = ref(false); // Whether imputation has been carried out
    let optimalResponse: axios.AxiosResponse<any>;
    let optimalParametersDetermined = ref(false);
    let loadingParameters = ref(false);
    let loadingResults = ref(false);
    let obfuscatedMatrix = [];
    let groundtruthMatrix = [];

    const handleParametersChanged = (newParams: any) => {
      optimizationParameters.value = newParams; // Update the optimization parameters
    };

    const obfuscatedColors = ["#7cb5ec", "#2b908f", "#a6c96a", "#876d5d", "#8f10ba", "#f7a35c", "#434348", "#f15c80", "#910000", "#8085e9", "#365e0c", "#90ed7d"];

    const fetchData = async () => {
      if (dataSelect.value !== "upload") {
        imputedData.value = false;
        try {
          let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
          const response = await axios.post('http://localhost:8000/api/fetchData/',
              {
                data_set: dataSet,
                normalization: normalizationMode.value,
              },
              {
                headers: {
                  'Content-Type': 'application/text',
                }
              }
          );
          chartOptionsOriginal.value.series.splice(0, chartOptionsOriginal.value.series.length);

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
        }
      }
    }

    const submitForm = async () => {

      if (document.activeElement.id === "delta_reset")
      {
        location.reload();
      }

      try {
        let dataSet = `${dataSelect.value}_obfuscated_10`;
        loadingParameters.value = true;
        imputedData.value = false;
        const response = await axios.post(`http://localhost:8000/api/optimization/${algorithmChoice.value}/`,
            {
              ...optimizationParameters.value, // Spread the optimization parameters into the post body
              data_set: dataSet,
              normalization: normalizationMode.value,
              algorithm: algorithmChoice.value
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
        );

        optimalResponse = response;

        if(algorithmChoice.value == "cdrec")
        {
          truncationRank.value = response.data.best_params.rank;
          epsilon.value = response.data.best_params.eps.toFixed(5);
          iterations.value = response.data.best_params.iters;
          loadingParameters.value = false;
        }
        else if(algorithmChoice.value == "stmvl")
        {
          gamma.value = response.data.best_params.gamma;
          alpha.value = response.data.best_params.alpha;
          windowSize.value = response.data.best_params.window_size;
        }
        else if(algorithmChoice.value == "iim")
        {
          numberSelect.value = response.data.best_params.learning_neighbours;
          chartOptionsImputed.value.series.splice(0, chartOptionsImputed.value.series.length);
          loadingParameters.value = false;

        }
        else if(algorithmChoice.value == "mrnn")
        {
          hiddenDim.value = response.data.best_params.hidden_dim;
          learningRate.value = response.data.best_params.learning_rate;
          iterations.value = response.data.best_params.iterations;
          keepProb.value = response.data.best_params.keep_prob;
          loadingParameters.value = false;
        }

        optimalParametersDetermined.value = true;


        await submitFormCustom();
      } catch (error) {
        console.error(error);
      } finally {
        loadingParameters.value = false;
      }
    }

    const submitFormCustom = async () => {
      try {
        loadingResults.value = true;
        imputedData.value = false;
        let dataSet = `${dataSelect.value}_obfuscated_10`;

        let response = ""
        if(algorithmChoice.value == "cdrec")
        {
          response = await axios.post(`http://localhost:8000/api/${algorithmChoice.value}/`,
              {
                data_set: dataSet,
                normalization: normalizationMode.value,
                truncation_rank: truncationRank.value,
                epsilon: "E-2",
                iterations: iterations.value,
              },
              {
                headers: {
                  'Content-Type': 'application/json',
                }
              }
          );
        }
        else if(algorithmChoice.value == "stmvl")
        {
          response = await axios.post(`http://localhost:8000/api/${algorithmChoice.value}/`,
              {
                data_set: dataSet,
                normalization: normalizationMode.value,
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
        }
        else if(algorithmChoice.value == "iim")
        {
          const formattedAlgCode = `iim ${numberSelect.value}${typeSelect.value}`;

          response = await axios.post(`http://localhost:8000/api/${algorithmChoice.value}/`,
              {
                alg_code: formattedAlgCode,
                data_set: dataSet,
                normalization: normalizationMode.value,
              },
              {
                headers: {
                  'Content-Type': 'application/json',
                }
              }
          );
        }
        else if(algorithmChoice.value == "mrnn")
        {
          response = await axios.post(`http://localhost:8000/api/${algorithmChoice.value}/`,
              {
                data_set: dataSet,
                normalization: normalizationMode.value,
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
        }

        rmse.value = response.data.rmse.toFixed(3);
        mae.value = response.data.mae.toFixed(3);
        mi.value = response.data.mi.toFixed(3);
        corr.value = response.data.corr.toFixed(3);
        chartOptionsImputed.value.series.length = 0;
        // Create a new array for the new series data
        const newSeriesData = [];

        const displayImputation = missingRate.value != '60' && missingRate.value != '80'
        response.data.matrix_imputed.forEach((data: number[], index: number) => {
          if (currentSeriesNames.length > 0 && missingRate) {
            if (displayImputation) {
              newSeriesData.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], groundtruthMatrix[index], chartOptionsImputed.value, dataSelect.value, currentSeriesNames[index]));
            } else {
              newSeriesData.push(createSeries(index, data, dataSelect.value, currentSeriesNames[index]));
            }
          } else {
            if (displayImputation) {
              newSeriesData.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], groundtruthMatrix[index], chartOptionsImputed.value, dataSelect.value));
            } else {
              newSeriesData.push(createSeries(index, data, dataSelect.value))
            }
          }
        });
        chartOptionsImputed.value.series = newSeriesData;
        imputedData.value = true;
      } catch (error) {
        console.error(error);
      } finally {
        loadingResults.value = false;
      }
    }

    const chartOptionsOriginal = ref(generateChartOptionsHeight('', 'Data'));
    const chartOptionsImputed = ref(generateChartOptionsHeight('', 'Data'));

    // Define a new function that calls fetchData
    const handleDataSelectChange = () => {
      chartOptionsImputed.value = generateChartOptionsHeight('Simulate Recovery', 'Data')
      fetchData();
    }

    const updateSeriesNames = (newSeriesNames) => {
      currentSeriesNames = newSeriesNames;
    };

    const handleNormalizationModeChange = () => {
      if (imputedData.value == true) {
          fetchData();
          submitFormCustom();
      } else {
          handleDataSelectChange();
      }
    }

    // Watch for changes and call fetchData when it changes
    watch([dataSelect, missingRate], handleDataSelectChange, {immediate: true});
    watch(normalizationMode, handleNormalizationModeChange, {immediate: true});

    const resetToOptimalParameters = () => {
      if (optimalResponse && algorithmChoice.value == "cdrec")
      {
        truncationRank.value = optimalResponse.data.best_params.rank;
        epsilon.value = optimalResponse.data.best_params.eps;
        iterations.value = optimalResponse.data.best_params.iters;
      }
      else if (optimalResponse && algorithmChoice.value == "stmvl" )
      {
        alpha.value = optimalResponse.data.best_params.alpha;
        gamma.value = optimalResponse.data.best_params.gamma;
        windowSize.value = optimalResponse.data.best_params.window_size;
      }
      else if (optimalResponse && algorithmChoice.value == "iim" )
      {
        numberSelect.value = optimalResponse.data.best_params.learning_neighbours;
      }
      else if (optimalResponse && algorithmChoice.value == "mrnn" )
      {
        hiddenDim.value = optimalResponse.data.best_params.hidden_dim;
        learningRate.value = optimalResponse.data.best_params.learning_rate;
        iterations.value = optimalResponse.data.best_params.iterations;
        keepProb.value = optimalResponse.data.best_params.keep_prob;
      }
    }

    return {
      submitForm,
      submitFormCustom,
      metrics,
      chartOptionsOriginal,
      chartOptionsImputed,
      dataSelect,
      algorithmChoice,
      normalizationMode,
      updateSeriesNames,
      truncationRank,

      epsilon,
      iterations,

      windowSize,
      gamma,
      alpha,

      numberSelect,
      typeSelect,

      learningRate,
      hiddenDim,
      keepProb,
      seqLen,

      missingRate,

      optimizationParameters,
      handleParametersChanged,
      optimalParametersDetermined,
      loadingParameters,
      resetToOptimalParameters,
      loadingResults,
      imputedData,

      nate_hidden
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px; /* Change this value to increase or decrease the margin */
}
</style>