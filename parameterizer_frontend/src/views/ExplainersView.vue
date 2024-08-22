<template>
  <h4 class="mb-4 text-center" style="margin-top:40px;margin-bottom:40px;">Data Explainer</h4>
  <div class="d-flex mb-auto">
    <div class="col-lg-10">
      <div v-if="loading" class="d-flex justify-content-center mt-3" style="margin-left : 320px;">
        <div class="alert alert-info d-flex align-items-center">
          <div class="spinner-border text-primary me-3" role="status"></div>
          Loading, building the model of the data explainer with SHAP...
        </div>
      </div>

      <div v-else-if="error" class="mt-3 alert alert-danger">
        {{ error }}
      </div>


      <div v-else class="mt-2 ms-5">

      <div style="margin-bottom:100px;">
        <h3>SHAP Explainer</h3>
        <template v-if="my_data !== '' && my_data !== undefined"  >
          <div>
             <template v-for="x in [my_path_agg]" >
                <img :src="x" style="width:100%; margin-bottom:100px;" />
             </template>
          </div>
        </template>

          <div>
            <h3 style="margin-bottom: 3%;">Details of the Explainer</h3>

             <template v-if="my_data !== '' && my_data !== undefined"  >
              <div >
                 <template v-for="x in [my_path]" >
                    <img :src="x" style="width:100%; margin-bottom:5%; text-align: center" />
                 </template>
              </div>
            </template>

            <table class="table" style="margin-bottom: 50px;">
              <thead>
                <tr>
                  <!--<th style="width: 20%;">Dataset</th>-->
                  <th style="width: 20%;">Algorithm</th>
                  <th style="width: 20%;">Features</th>
                  <th style="width: 20%;">Categories</th>
                  <th style="width: 20%;">Impact of the Feature</th>
                </tr>
              </thead>
              <tbody>
              <template v-for="(line, index) in shapValues" :key="index">
                  <tr  v-for="index in 22">
                      <!--<td>{{ line[index-1][0] }}</td> # Dataset -->
                      <td>{{ line[index-1][1] }}</td> <!-- Algorithm -->
                      <td>{{ line[index-1][3] }}</td> <!-- Description -->
                      <td>{{ line[index-1][5] }}</td> <!-- Categories -->
                      <td>{{ line[index-1][2] }}%</td> <!-- Results -->
                  </tr>
              </template>
              </tbody>
            </table>


          </div>
      </div>

      <hr style="margin-bottom: 5%">

        <!-- Geometry Table -->
        <div>
          <h4>Geometry</h4>

          <table class="table"  style="margin-bottom: 50px;">
            <thead>
            <tr>
              <th  style="width: 80%;" >Feature Name</th>
              <th  style="width: 10%;" >Value</th>
              <th  style="width: 10%;" >Impact</th>
            </tr>
            </thead>
            <tbody>
              <template v-for="(line, index) in shapValues" :key="index">
                <tr  v-for="index in 22" >
                  <template v-if="line[index-1][5] === 'Geometry'">
                      <td>{{ line[index-1][3] }}</td> <!-- Description -->
                      <td>{{ line[index-1][6].toFixed(4) }}</td> <!-- Mean values -->
                      <td>{{ line[index-1][2] }}%</td> <!-- Results -->
                  </template>
                </tr>
               </template>
            </tbody>
          </table>

          <template v-if="my_data !== '' && my_data !== undefined"  >
            <div style="text-align:center;">
               <template v-for="x in [my_path_geometry]" >
                  <img :src="x" style="width:95%; margin-bottom:10%" />
               </template>
            </div>
          </template>

        </div>

        <hr style="margin-bottom: 5%">

        <!-- Correlation Table -->
        <div>
          <h4>Correlation</h4>

          <table class="table"  style="margin-bottom: 50px;">
            <thead>
            <tr>
              <th style="width: 80%;" >Feature Name</th>
              <th style="width: 10%;" >Value</th>
              <th  style="width: 10%;" >Impact</th>
            </tr>
            </thead>
            <tbody>
              <template v-for="(line, index) in shapValues" :key="index">
                <tr  v-for="index in 22" >
                  <template v-if="line[index-1][5] === 'Correlation'">
                      <td>{{ line[index-1][3] }}</td> <!-- Description -->
                      <td>{{ line[index-1][6].toFixed(4) }}</td> <!-- Mean values -->
                      <td>{{ line[index-1][2] }}%</td> <!-- Results -->
                  </template>
                </tr>
               </template>
            </tbody>
          </table>

          <template v-if="my_data !== '' && my_data !== undefined"  >
            <div style="text-align:center;">
               <template v-for="x in [my_path_correlation]" >
                  <img :src="x" style="width:95%; margin-bottom:10%" />
               </template>
            </div>
          </template>
        </div>

        <hr style="margin-bottom: 5%">

        <!-- Transformation Table -->
        <div class="mb-4">
          <h4>Transformation</h4>

          <table class="table"  style="margin-bottom: 50px;">
            <thead>
            <tr>
              <th style="width: 80%;" >Feature Name</th>
              <th style="width: 10%;" >Value</th>
              <th  style="width: 10%;" >Impact</th>
            </tr>
            </thead>
            <tbody>
              <template v-for="(line, index) in shapValues" :key="index">
                <tr  v-for="index in 22" >
                  <template v-if="line[index-1][5] === 'Transformation'">
                      <td>{{ line[index-1][3] }}</td> <!-- Description -->
                      <td>{{ line[index-1][6].toFixed(4) }}</td> <!-- Mean values -->
                      <td>{{ line[index-1][2] }}%</td> <!-- Results -->
                  </template>
                </tr>
               </template>
            </tbody>
          </table>


          <template v-if="my_data !== '' && my_data !== undefined"  >
            <div style="text-align:center;">
               <template v-for="x in [my_path_transformation]" >
                  <img :src="x" style="width:95%; margin-bottom:10%" />
               </template>
            </div>
          </template>

        </div>

        <hr style="margin-bottom: 5%">

        <div>
          <h4>Trend</h4>

          <table class="table"  style="margin-bottom: 50px;">
            <thead>
            <tr>
              <th style="width: 80%;" >Feature Name</th>
              <th style="width: 10%;" >Value</th>
              <th  style="width: 10%;" >Impact</th>
            </tr>
            </thead>
            <tbody>
              <template v-for="(line, index) in shapValues" :key="index">
                <tr  v-for="index in 22" >
                  <template v-if="line[index-1][5] === 'Trend'">
                      <td>{{ line[index-1][3] }}</td> <!-- Description -->
                      <td>{{ line[index-1][6].toFixed(4) }}</td> <!-- Mean values -->
                      <td>{{ line[index-1][2] }}%</td> <!-- Results -->
                  </template>
                </tr>
               </template>
            </tbody>
          </table>

          <template v-if="my_data !== '' && my_data !== undefined"  >
            <div style="text-align:center;">
               <template v-for="x in [my_path_trend]" >
                  <img :src="x" style="width:95%; margin-bottom:10%"/>
               </template>
            </div>
          </template>

          </div>

          <hr style="margin-bottom: 5%">
                 <h2 style="margin-bottom: 10px;">Features by Series</h2>

                 <table class="table" style="margin-bottom: 10%;">
                    <thead>
                      <tr>
                        <th style="width: 25%;">Dataset</th>
                        <th style="width: 25%;">Series</th>
                        <th style="width: 25%;">Type</th>
                        <th style="width: 25%;">RMSE</th>
                      </tr>
                    </thead>
                    <tbody>

                    <template v-for="(line, index) in shapValues" :key="index">
                        <template  v-for="index in 1">
                            <tr v-for="(rmse, ind) in line[index-1][7]" >
                              <td>{{ dataSelect }}</td>
                              <td>{{ ind }}</td>
                              <td>
                                    <span v-if="ind < splitterValue">Train set</span>
                                    <span v-else-if="ind >= splitterValue">Test set</span>
                              </td>
                              <td>{{ rmse.toFixed(5) }}</td>
                            </tr>
                        </template>
                    </template>
                    </tbody>
                  </table>

                  <template v-if="my_data !== '' && my_data !== undefined"  >
                      <div style="text-align:center;">
                         <template v-for="x in [my_path_reverse_agg]" >
                            <img :src="x" style="width:95%; margin-bottom:10%"/>
                         </template>
                      </div>
                    </template>

                    <template v-if="my_data !== '' && my_data !== undefined"  >
                      <div style="text-align:center;">
                         <template v-for="x in [my_path_reverse]" >
                            <img :src="x" style="width:95%; margin-bottom:10%"/>
                         </template>
                      </div>
                    </template>
      </div>
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



    <div class="col-lg-2" style="margin-top: -10px;">
      <div class="sidebar me-5">
        <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames" class="mb-3"/>
        <algorithm-choice v-model="algorithmChoice"  @submit.prevent="submitFormCustom"  /><br />

        <!--
        <label style="margin-right : 10px;"  for="range">Number Series {{ rangeValue }} : </label>
        <input type="range" id="range" v-model="rangeValue" :min="10" :max="20" /><br /><br />

        <label style="margin-right : 10px;" for="range_splitter">Training Series {{ splitterValue }} : </label>
        <input type="range" id="range_splitter" v-model="splitterValue" :min="(rangeValue/2).toFixed(0)" :max="((rangeValue/3*2)+1).toFixed(0)" /><br />
        -->
        <button type="submit" class="btn btn-primary mt-5" @click="fetchDataFeatures">Explain</button>
      </div>
    </div>
  </div>

</template>

<script lang="ts">
import {ref, watch} from 'vue';
import { useRoute } from 'vue-router'
import DataSelect from './components/DataSelect.vue';
import MetricsDisplay from './components/MetricsDisplay.vue';
import MissingRate from './components/MissingRate.vue';
import NormalizationToggle from './components/NormalizationToggleOptimization.vue'
import axios from 'axios';
import {Chart} from 'highcharts-vue'
import Highcharts from 'highcharts'
import HighchartsBoost from 'highcharts/modules/boost'
import {createSeries, generateChartOptions, generateChartOptionsLarge} from "@/views/thesisUtils/utils";
import AlgorithmChoice from "@/views/components/AlgorithmChoice.vue";
import defaultConfig from'./../assets_naterq/default_values.json';


HighchartsBoost(Highcharts)


export default {
  components: {
    AlgorithmChoice,
    DataSelect,
    highcharts: Chart,
    MetricsDisplay,
    MissingRate,
    NormalizationToggle,
  }, setup() {
    const route = useRoute()
    const dataSelect = ref(route.params.datasetName || defaultConfig.loading.load_dataset);
    const normalizationMode = ref(defaultConfig.loading.load_normalization)
    const algorithmChoice = ref(defaultConfig.loading.load_algorithm)

    let currentSeriesNames = []; // Names of series currently displayed
    const features = ref<Record<string, number>>({});
    const loading = ref(false)
    const error = ref("");
    const loadedResults = ref(false);
    const chartOptionsOriginal = ref(generateChartOptions('Data', 'Data'));
    const categorizedFeatures = ref({});

    const shapValues = ref([]);

    const rangeValue = ref(defaultConfig.explainer.nbr_series)
    const splitterValue = ref(defaultConfig.explainer.splitter)

    const my_data = ref("");
    const my_data_set =ref("");
    const my_path =ref("");
    const my_path_agg =ref("");
    const my_path_geometry =ref("");
    const my_path_trend =ref("");
    const my_path_transformation =ref("");
    const my_path_correlation =ref("");
    const my_path_reverse =ref("");
    const my_path_reverse_agg =ref("");

    const fetchData = async () => {
      console.log("Welcome to SHAP EXPLAINER")
    }

    function categoryExists(category: string): boolean {
      return categorizedFeatures.value[category] && Object.keys(categorizedFeatures.value[category]).length > 0;
    }

    const fetchDataFeatures = async () => {
      if (dataSelect.value !== "upload") {
        loading.value = true;
        error.value = "";
        loadedResults.value = false;

        try
        {
          switch (dataSelect.value)
          {
            case "bafu":
              my_data.value = `bafu`;
              my_data_set.value = `BAFU`;
              break;
            case "chlorine":
              my_data.value = `chlorine`;
              my_data_set.value = `cl2fullLarge`;
              break;
            case "climate":
              my_data.value = `climate`;
              my_data_set.value = `climate`;
              break;
            case "drift":
              my_data.value = `drift`;
              my_data_set.value = `batch10`;
              break;
            case "meteo":
              my_data.value = `meteo`;
              my_data_set.value = `meteo_total`;
              break;
          }

          my_path.value = "src/assets_naterq/" + dataSelect.value + "_"+ algorithmChoice.value +"_shap_plot.png"
          my_path_agg.value = "src/assets_naterq/" + dataSelect.value + "_"+ algorithmChoice.value +"_shap_aggregate_plot.png"

          my_path_geometry.value = "src/assets_naterq/" + dataSelect.value  + "_"+ algorithmChoice.value +"_shap_geometry_plot.png"
          my_path_trend.value = "src/assets_naterq/" + dataSelect.value + "_"+ algorithmChoice.value +"_shap_trend_plot.png"
          my_path_transformation.value = "src/assets_naterq/" + dataSelect.value + "_"+ algorithmChoice.value +"_shap_transformation_plot.png"
          my_path_correlation.value = "src/assets_naterq/" + dataSelect.value + "_"+ algorithmChoice.value +"_shap_correlation_plot.png"

          my_path_reverse.value = "src/assets_naterq/" + dataSelect.value + "_"+ algorithmChoice.value +"_shap_reverse_plot.png"
          my_path_reverse_agg.value = "src/assets_naterq/" + dataSelect.value + "_"+ algorithmChoice.value +"_shap_aggregate_reverse_plot.png"

          const shap_results = await axios.post('http://localhost:8000/api/shapCallExplainers/',
              {
                dataset: dataSelect.value,
                algorithm : algorithmChoice.value,
                missing_values : 20,
                scenario : "blackout",
                selected_series : ["-2:all"],
                normalization : normalizationMode.value,
                limitation : rangeValue.value,
                splitter : splitterValue.value,
                cdrec_params : [defaultConfig.cdrec.default_reduction_rank, defaultConfig.cdrec.default_epsilon_str, defaultConfig.cdrec.default_iteration], // truncation_rank / epsilon / iterations
                stmvl_params : [defaultConfig.stmvl.default_window_size, defaultConfig.stmvl.default_gamma, defaultConfig.stmvl.default_alpha], // window_size / gamma / alpha
                iim_params : "iim " + defaultConfig.iim.default_neighbor,
                mrnn_params : [defaultConfig.mrnn.default_hidden_dim, defaultConfig.mrnn.default_learning_rate, defaultConfig.mrnn.default_iterations, defaultConfig.mrnn.default_keep_prob]// hidden_dim / learning_rate / iterations / seq_len

              },
              {
                headers: {
                  'Content-Type': 'application/text',
                }
              }
          );

          console.log("shap_results:", shap_results);
          shapValues.value = shap_results.data

          console.log("shapValues.value:", shapValues.value);

        }
        catch (error)
        {
          error.value = `Error: ${error.message}`;
          console.error(error);
        }
        finally
        {
          loading.value = false;
        }
      }
    }

    const submitForm = async () => {
      if (document.activeElement.id === "delta_reset")
      {
        location.reload();
      }
    }

    // Define a new function that calls fetchData
    const handleDataSelectChange = () =>
    {
      fetchData();
    }

    const updateSeriesNames = (newSeriesNames) => {
      currentSeriesNames = newSeriesNames;
    };

    watch([dataSelect, normalizationMode], handleDataSelectChange, {immediate: true});

    return {
      dataSelect,
      normalizationMode,
      updateSeriesNames,
      features,
      loading,
      error,
      loadedResults,
      fetchDataFeatures,
      chartOptionsOriginal,
      categorizedFeatures,
      categoryExists,
      submitForm,
      shapValues,
      rangeValue,
      splitterValue,
      my_data,
      my_data_set,
      my_path,
      my_path_agg,
      my_path_geometry,
      my_path_trend,
      my_path_transformation,
      my_path_correlation,
      my_path_reverse,
      my_path_reverse_agg,
      algorithmChoice
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 55px; /* Change this value to increase or decrease the margin */
}
</style>