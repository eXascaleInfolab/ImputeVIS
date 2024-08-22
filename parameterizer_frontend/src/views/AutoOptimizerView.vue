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

      <h3 v-if="naterq_error" style="color : red; margin-left : 20%" >The current algorithm does not match with the current optimization, no feature available...</h3>

      <div class="row">
        <div class="col-md-12">
          <form v-if="optimalParametersDetermined && imputedData && algorithmChoice == 'cdrec'" @submit.prevent="submitFormCustom">
            <div class="row">
              <div class="col-md-6" style="padding: 20px; height: 100%;">
                <h5 style="text-align: center; margin-bottom: 20px;">Optimal Parameters</h5>
                <div class="row"  style="margin:5%;">
                  <div class="col-12" style="height: 100%;">
                    <table class="table table-bordered" style="width: 100%; height: 100%;">
                      <thead class="thead-dark">
                      <tr>
                        <th scope="col" style="width: 40%;">Parameter</th>
                        <th scope="col" style="width: 20%;">Optimal Value</th>
                        <th scope="col" style="width: 20%;">Default Value</th>
                      </tr>
                      </thead>
                      <tbody>
                      <tr>
                        <td>Reduction Rank</td>
                        <td>{{ truncationRank }}</td>
                        <td>{{ default_truncationRank }}</td>
                      </tr>
                      <tr>
                        <td>Threshold for Difference</td>
                        <td>{{ parseFloat(epsilon) }}</td>
                        <td>{{ parseFloat(default_epsilon) }}</td>
                      </tr>
                      <tr>
                        <td>Number of Iterations</td>
                        <td>{{ iterations }}</td>
                        <td>{{ default_iterations }}</td>
                      </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              <div class="col-md-5" style="padding: 20px; text-align: center; margin-left: 5%;">
                <h5 style="text-align: center; margin-bottom: 20px;">Metrics</h5>
                <metrics-3-display v-if="imputedData" :metrics="metrics" :default_values="metrics_default"></metrics-3-display>
              </div>
            </div>
          </form>
        </div>
      </div>








      <div class="row">
        <div class="col-md-12">
          <form v-if="optimalParametersDetermined && imputedData && algorithmChoice == 'stmvl'" @submit.prevent="submitFormCustom">
            <div class="row">
              <div class="col-md-6" style="padding: 20px; height: 100%;">
                <h5 style="text-align: center; margin-bottom: 20px;">Optimal Parameters</h5>
                <div class="row"  style="margin:5%;">
                  <div class="col-12" style="height: 100%;">
                    <table class="table table-bordered" style="width: 100%; height: 100%;">
                      <thead class="thead-dark">
                      <tr>
                        <th scope="col" style="width: 40%;">Parameter</th>
                        <th scope="col" style="width: 20%;">Optimal Value</th>
                        <th scope="col" style="width: 20%;">Default Value</th>
                      </tr>
                      </thead>
                      <tbody>
                      <tr>
                        <td>Window Size</td>
                        <td>{{ windowSize }}</td>
                        <td>{{ default_windowSize }}</td>
                      </tr>
                      <tr>
                        <td>Smoothing Parameter (γ)</td>
                        <td>{{ parseFloat(gamma).toFixed(5) }}</td>
                        <td>{{ default_gamma }}</td>
                      </tr>

                      <tr>
                        <td>Power for Spatial Weight (α)</td>
                        <td>{{ alpha }}</td>
                        <td>{{ default_alpha }}</td>
                      </tr>
                      </tbody>
                      <!-- https://paperswithcode.com/paper/st-mvl-filling-missing-values-in-geo-sensory -->
                    </table>
                  </div>
                </div>
              </div>
              <div class="col-md-5" style="padding: 20px; text-align: center; margin-left: 5%;">
                <h5 style="text-align: center; margin-bottom: 20px;">Metrics</h5>
                <metrics-3-display v-if="imputedData" :metrics="metrics" :default_values="metrics_default"></metrics-3-display>
              </div>
            </div>
          </form>
        </div>
      </div>

        <!--<div class="col-md-5" style="padding: 20px; text-align: center; margin-left: 5%;">
                <metrics2-kiviat-display v-if="imputedData" :metrics="metrics" style="height: 100%;"></metrics2-kiviat-display>
        </div>-->




      <div class="row">
        <div class="col-md-12">
          <form v-if="optimalParametersDetermined && imputedData && algorithmChoice == 'iim'" @submit.prevent="submitFormCustom">
             <div class="row">
              <div class="col-md-6" style="padding: 20px; height: 100%;">
                <h5 style="text-align: center; margin-bottom: 20px;">Optimal Parameters</h5>
                <div class="row"  style="margin:5%;">
                  <div class="col-12" style="height: 100%;">
                    <table class="table table-bordered" style="width: 100%; height: 100%;">
                      <thead class="thead-dark">
                      <tr>
                        <th scope="col" style="width: 40%;">Parameter</th>
                        <th scope="col" style="width: 20%;">Optimal Value</th>
                        <th scope="col" style="width: 20%;">Default Value</th>
                      </tr>
                      </thead>
                      <tbody>
                      <tr>
                        <td>Number of Neighbor</td>
                        <td>{{ numberSelect }}</td>
                        <td>{{ default_neighbor }}</td>
                      </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              <div class="col-md-5" style="padding: 20px; text-align: center; margin-left: 5%;">
                <h5 style="text-align: center; margin-bottom: 20px;">Metrics</h5>
                <metrics-3-display v-if="imputedData" :metrics="metrics" :default_values="metrics_default"></metrics-3-display>
              </div>
            </div>
          </form>
        </div>
      </div>





      <div class="row">
        <div class="col-md-12">
          <form v-if="optimalParametersDetermined && imputedData && algorithmChoice == 'mrnn'" @submit.prevent="submitFormCustom">
            <div class="row">
              <div class="col-md-6" style="padding: 20px; height: 100%;">
                <h5 style="text-align: center; margin-bottom: 20px;">Optimal Parameters</h5>
                <div class="row"  style="margin:5%;">
                  <div class="col-12" style="height: 100%;">
                    <table class="table table-bordered" style="width: 100%; height: 100%;">
                      <thead class="thead-dark">
                      <tr>
                        <th scope="col" style="width: 40%;">Parameter</th>
                        <th scope="col" style="width: 20%;">Optimal Value</th>
                        <th scope="col" style="width: 20%;">Default Value</th>
                      </tr>
                      </thead>
                      <tbody>
                      <tr>
                        <td>Learning Rate</td>
                        <td>{{ parseFloat(learningRate).toFixed(6) }}</td>
                        <td>{{ default_learningRate }}</td>
                      </tr>
                      <tr>
                        <td>Hidden Dimension Size</td>
                        <td>{{ hiddenDim }}</td>
                        <td>{{ default_hiddenDim }}</td>
                      </tr>
                      <tr>
                        <td>Number of Iterations</td>
                        <td>{{ iterations }}</td>
                        <td>{{ default_iterations_ml }}</td>
                      </tr>
                      <tr>
                        <td>Keep Rate</td>
                        <td>{{ parseFloat(keepProb).toFixed(4) }}</td>
                        <td>{{ default_keepProb }}</td>
                      </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              <div class="col-md-5" style="padding: 20px; text-align: center; margin-left: 5%;">
                <h5 style="text-align: center; margin-bottom: 20px;">Metrics</h5>
                <metrics-3-display v-if="imputedData" :metrics="metrics" :default_values="metrics_default"></metrics-3-display>
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
        <div class="d-flexs mt-4 me-10" >
          <button type="submit" id="alpha_run" class="btn btn-primary" style="margin-top:10px;  width:100px; ">Optimize</button>
          <button type="submit" id="delta_reset" class="btn btn-danger" style="margin-top:10px; margin-left : 10%; width:100px; ">Clear</button>
        </div>

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
import Metrics3Display from './components/Metrics3Display.vue';
import Metrics2KiviatDisplay from './components/Metrics2KiviatDisplay.vue';
import MissingRate from './components/MissingRate.vue';
import NormalizationToggle from './components/NormalizationToggleOptimization.vue'
import OptimizationSelect from './components/OptimizationSelect.vue';
import axios from 'axios';
import {Chart} from 'highcharts-vue'
import defaultConfig from'./../assets_naterq/default_values.json';


import {
  createSegmentedSeries,
  createSeries,
  generateChartOptionsHeight,
} from "@/views/thesisUtils/utils";
import ScenarioMissingValues from "@/views/components/ScenarioMissingValues.vue";
import optimizationSelect from "@/views/components/OptimizationSelect.vue";
import DataSelect from "@/views/components/DataSelect.vue";


export default {
  computed: {
    optimizationSelect() {
      return optimizationSelect
    }
  },
  components: {
    DataSelect,
    ScenarioMissingValues,
    highcharts: Chart,
    DataSelectOptimization,
    AlgorithmChoice,
    Metrics3Display,
    Metrics2KiviatDisplay,
    MissingRate,
    NormalizationToggle,
    OptimizationSelect
  },
  setup()
  {

    const default_truncationRank = ref(defaultConfig.cdrec.default_reduction_rank);
    const default_epsilon = ref(defaultConfig.cdrec.default_epsilon);
    const default_iterations = ref(defaultConfig.cdrec.default_iteration);

    const default_windowSize = ref(defaultConfig.stmvl.default_window_size);
    const default_gamma = ref(defaultConfig.stmvl.default_gamma);
    const default_alpha = ref(defaultConfig.stmvl.default_alpha);

    const default_learningRate = ref(defaultConfig.mrnn.default_learning_rate);
    const default_hiddenDim = ref(defaultConfig.mrnn.default_hidden_dim);
    const default_keepProb = ref(defaultConfig.mrnn.default_keep_prob);
    const default_seq = ref(defaultConfig.mrnn.default_sequence_length);
    const default_iterations_ml = ref(defaultConfig.mrnn.default_iterations);

    const default_neighbor = ref(defaultConfig.iim.default_neighbor);

    let currentSeriesNames = []; // Names of series currently displayed
    const optimizationParameters = ref({});
    const dataSelect = ref(defaultConfig.loading.load_dataset);
    const algorithmChoice = ref(defaultConfig.loading.load_algorithm);
    const normalizationMode = ref(defaultConfig.loading.load_normalization);
    const missingRate = ref(defaultConfig.loading.load_missing_rate);
    const scenarioMissingValues = ref(defaultConfig.loading.load_scenario);
    const selection_series =  ref(defaultConfig.loading.load_series);

    const nate_hidden = true;

    const truncationRank = ref(default_truncationRank.value) // Default truncation rank is 1, 0 means detect truncation automatically
    const epsilon = ref(default_epsilon.value); // Default epsilon is E-6
    const iterations = ref(default_iterations.value); // Default number of iterations is 1000

    const windowSize = ref(default_windowSize.value); // Default window size is 2
    const gamma = ref(default_gamma.value) // Default smoothing parameter gamma is 0.5, min 0.0, max 1.0
    const alpha = ref(default_alpha.value) // Default power for spatial weight (alpha) is 2, must be larger than 0.0

    const numberSelect = ref(default_neighbor.value); // Default selected learning neighbors is 1
    const typeSelect = ref(''); // Default selected type is "Normal", denoted by an empty string

    const learningRate = ref(default_learningRate.value); // Default learning rate is 0.01
    const hiddenDim = ref(default_hiddenDim.value); // Default hidden dimension size is 10
    const keepProb = ref(default_keepProb.value); // Default keep probability is 0.5
    const seqLen = ref(default_seq.value); // Default sequence length is 7

    const rmse = ref(null);
    const mae = ref(null);
    const mi = ref(null);
    const corr = ref(null);

    const rmse_default = ref(null);
    const mae_default = ref(null);
    const mi_default = ref(null);
    const corr_default = ref(null);

    const metrics = computed(() => ({rmse: rmse.value, mae: mae.value, mi: mi.value, corr: corr.value}));
    const metrics_default = computed(() => [
      rmse_default.value, // index 0
      mae_default.value,  // index 1
      mi_default.value,   // index 2
      corr_default.value  // index 3
    ]);
    const imputedData = ref(false); // Whether imputation has been carried out
    const naterq_error = ref(false); // Whether imputation has been carried out
    let optimalResponse: axios.AxiosResponse<any>;
    let optimalParametersDetermined = ref(false);
    let loadingParameters = ref(false);
    let loadingResults = ref(false);
    let obfuscatedMatrix = [];
    let groundtruthMatrix = [];

    const obfuscatedColors = defaultConfig.colors.chart;


    const handleParametersChanged = (newParams: any) => {
      optimizationParameters.value = newParams; // Update the optimization parameters
    };


    const fetchData = async () => {

      if (dataSelect.value !== "upload")
      {
        imputedData.value = false;

        try
        {
          const response = await axios.post('http://localhost:8000/api/fetchData/', {
                dataset: dataSelect.value,
                normalization : normalizationMode.value,
                scenario : scenarioMissingValues.value,
                missing_rate: missingRate.value,
                selected_series: selection_series.value
              },
              {
                headers: {
                  'Content-Type': 'application/text',
                }
              }
          );

          chartOptionsOriginal.value.series.splice(0, chartOptionsOriginal.value.series.length);
          chartOptionsImputed.value.series.splice(0, chartOptionsImputed.value.series.length);


          obfuscatedMatrix = response.data.matrix;
          groundtruthMatrix = response.data.groundtruth;

          obfuscatedMatrix.forEach((data: number[], index: number) => {
              chartOptionsOriginal.value.series[index] = createSeries(index, data, dataSelect.value, currentSeriesNames[index], 'line', 2, obfuscatedColors[index])
              chartOptionsImputed.value.series[index] = createSeries(index, data, dataSelect.value, currentSeriesNames[index], 'line', 1, obfuscatedColors[index]);
          });
          groundtruthMatrix.forEach((data: number[], index: number) => {
            if (index < 2) {
              chartOptionsOriginal.value.series.push(createSeries(index, data, dataSelect.value, currentSeriesNames[index] + "_MV", 'dash', 2, obfuscatedColors[index], true));
            }
          });

        }
        catch (error)
        {
          naterq_error.value = true;
          console.error(error);
        }
      }
    }

    const submitForm = async () => {

      if (document.activeElement.id === "delta_reset")
      {
        location.reload();
      }

      try
      {
        loadingParameters.value = true;
        imputedData.value = false;
        const response = await axios.post(`http://localhost:8000/api/optimization/${algorithmChoice.value}/`,
            {
              ...optimizationParameters.value, // Spread the optimization parameters into the post body
              dataset: dataSelect.value,
              normalization: normalizationMode.value,
              algorithm: algorithmChoice.value,
              scenario : scenarioMissingValues.value,
              missing_rate: missingRate.value,
              selected_series: selection_series.value
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
      }
      catch (error)
      {
        console.error(error);
        naterq_error.value = true;
      }
      finally
      {
        loadingParameters.value = false;
      }
    }

    const submitFormCustom = async () => {
      try
      {
        loadingResults.value = true;
        imputedData.value = false;

        let response = ""

        if(algorithmChoice.value == "cdrec")
        {
          response = await axios.post(`http://localhost:8000/api/${algorithmChoice.value}/`,
              {
                dataset: dataSelect.value,
                normalization: normalizationMode.value,
                scenario : scenarioMissingValues.value,
                missing_rate : missingRate.value,
                selected_series : selection_series.value,
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
        }
        else if(algorithmChoice.value == "stmvl")
        {
          response = await axios.post(`http://localhost:8000/api/${algorithmChoice.value}/`,
              {
                dataset: dataSelect.value,
                normalization: normalizationMode.value,
                scenario : scenarioMissingValues.value,
                missing_rate : missingRate.value,
                selected_series : selection_series.value,
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
                dataset: dataSelect.value,
                alg_code: formattedAlgCode,
                normalization: normalizationMode.value,
                scenario : scenarioMissingValues.value,
                missing_rate : missingRate.value,
                selected_series : selection_series.value
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
                dataset: dataSelect.value,
                normalization: normalizationMode.value,
                scenario : scenarioMissingValues.value,
                missing_rate : missingRate.value,
                selected_series : selection_series.value,
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

        const displayImputation = missingRate.value != '60' && missingRate.value != '80'

        groundtruthMatrix.forEach((data: number[], index: number) => {
          chartOptionsImputed.value.series.push(createSeries(index, data, dataSelect.value,currentSeriesNames[index] + "_MV", 'dash', 1, obfuscatedColors[index], false));
        });

        response.data.matrix_imputed.forEach((data: number[], index: number) =>
        {
            if (displayImputation)
            {
              chartOptionsImputed.value.series.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], null, chartOptionsImputed.value, dataSelect.value, currentSeriesNames[index]+"_imp"));
            }
        });

        imputedData.value = true;

        // DEFAULT RESULT ================================================================================================================
        if(algorithmChoice.value == "cdrec")
        {
          response = await axios.post(`http://localhost:8000/api/${algorithmChoice.value}/`,
              {
                dataset: dataSelect.value,
                normalization: normalizationMode.value,
                scenario : scenarioMissingValues.value,
                missing_rate : missingRate.value,
                selected_series : selection_series.value,
                truncation_rank: default_truncationRank.value,
                epsilon: default_epsilon.value,
                iterations: default_iterations.value,
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
                dataset: dataSelect.value,
                normalization: normalizationMode.value,
                scenario : scenarioMissingValues.value,
                missing_rate : missingRate.value,
                selected_series : selection_series.value,
                window_size: default_windowSize.value,
                gamma: default_gamma.value,
                alpha: default_alpha.value,
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
          const formattedAlgCode = `iim ${default_neighbor.value}${typeSelect.value}`;

          response = await axios.post(`http://localhost:8000/api/${algorithmChoice.value}/`,
              {
                dataset: dataSelect.value,
                alg_code: formattedAlgCode,
                normalization: normalizationMode.value,
                scenario : scenarioMissingValues.value,
                missing_rate : missingRate.value,
                selected_series : selection_series.value
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
                dataset: dataSelect.value,
                normalization: normalizationMode.value,
                scenario : scenarioMissingValues.value,
                missing_rate : missingRate.value,
                selected_series : selection_series.value,
                hidden_dim: default_hiddenDim.value,
                learning_rate: default_learningRate.value,
                iterations: default_iterations_ml.value,
                keep_prob: default_keepProb.value,
                seq_len: seqLen.value
              },
              {
                headers: {
                  'Content-Type': 'application/json',
                }
              }
          );
        }

        rmse_default.value = response.data.rmse.toFixed(3);
        mae_default.value = response.data.mae.toFixed(3);
        mi_default.value = response.data.mi.toFixed(3);
        corr_default.value = response.data.corr.toFixed(3);

      }
      catch (error)
      {
        console.error(error);
        naterq_error.value = true;
      }
      finally
      {
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
      metrics_default,
      chartOptionsOriginal,
      chartOptionsImputed,
      dataSelect,
      algorithmChoice,
      normalizationMode,
      updateSeriesNames,
      truncationRank,
      scenarioMissingValues,
      selection_series,

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
      naterq_error,

      nate_hidden,

      default_truncationRank,
      default_epsilon,
      default_iterations,

      default_windowSize,
      default_gamma,
      default_alpha,

      default_learningRate,
      default_hiddenDim,
      default_keepProb,
      default_seq,
      default_iterations_ml,

      default_neighbor
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px; /* Change this value to increase or decrease the margin */
}
</style>