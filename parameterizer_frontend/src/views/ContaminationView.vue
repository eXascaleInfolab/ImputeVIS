<template>
  <main>
    <div v-if="loadingResults" class="d-flex justify-content-center mt-3">
      <div class="alert alert-info d-flex align-items-center">
        <div class="spinner-border text-primary me-3" role="status"></div>
        Loading...
      </div>
    </div>
    <div class="mb-auto">
      <div class="col-lg-12">
        <div class="row me-1">
          <form ref="ref_reload" @submit.prevent="submitForm">
            <div class="justify-content-right" style="padding: 10px; position: absolute; z-index: 200; right: 60px; top: 55px;">
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
          <div class="col-lg-10">
            <highcharts class="mb-5 pb-5" :options="chartOptionsOriginal" style="margin-top: 30px;"></highcharts>
          </div>
          <div class="col-lg-2" style="margin-top: 60px;">
              <form ref="ref_missingvalues" @submit.prevent="submitForm">
                <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames" />
                <scenario-missing-values v-model="scenarioMissingValues" />

                <div v-for="series in mySeries" :key="series" class="form-check">
                  <input class="form-check-input" type="checkbox" :id="`checkbox-${series}`" :value="series" v-model="selectedSeries"/>
                  <label class="form-check-label" :for="`checkbox-${series}`">{{ series.substring(3) }}</label>
                </div>

                <missing-rate v-model="missingRate"/>
                <div class="d-flexs mt-4 me-5" >
                  <button type="submit" id="alpha_run" class="btn btn-primary" style="margin-top:36px;">Run</button>
                </div>
              </form>


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
import SeriesSelect from './components/SeriesSelect.vue';
import MissingRate from './components/MissingRate.vue';
import ScenarioMissingValues from './components/ScenarioMissingValues.vue';
import NormalizationToggle from './components/NormalizationToggle.vue'
import axios from 'axios';
import {Chart} from 'highcharts-vue'
import {
  createSeries,
  generateChartOptionsLarge
} from "@/views/thesisUtils/utils";

export default {

  components: {
    NormalizationToggle,
    highcharts: Chart,
    DataSelect,
    SeriesSelect,
    MissingRate,
    ScenarioMissingValues
  }, setup() {
    const route = useRoute()
    const dataSelect = ref(route.params.datasetName || 'chlorine') // Default data is BAFU
    const seriesSelect = ref('Series 1')
    const normalizationMode = ref('Normal')
    const scenarioMissingValues = ref('mcar')

    let currentSeriesNames = ["test"]; // Names of series currently displayed
    const mySeries = ref([]);
    const selectedSeries = ref([]);
    const fetchedData = reactive({});
    let loadingResults = ref(true);
    const selectedParamOption = ref('recommended'); // Default option


    //CDRec Parameters
    const missingRate = ref('0'); // Default missing rate

    let obfuscatedMatrix = [];
    let groundtruthMatrix = [];
    const checkedNames = ref([]);
    const imputedData = ref(false); // Whether imputation has been carried out

    const obfuscatedColors = ["#7cb5ec", "#2b908f", "#a6c96a", "#876d5d", "#8f10ba", "#f7a35c", "#434348", "#f15c80", "#910000", "#8085e9", "#365e0c", "#90ed7d"];




    const fetchData = async () => {

      if (dataSelect.value !== "upload")
      {
        try
        {
          loadingResults.value = true;

          let selection_series = ["-1:test"];

          if (selectedSeries.value.length > 0)
          {
              selection_series = selectedSeries.value;
          }

          const response = await axios.post('http://localhost:8000/api/fetchData/',
              {
                dataset: dataSelect.value,
                normalization : normalizationMode.value,
                scenario : scenarioMissingValues.value,
                missing_rate: missingRate.value,
                selected_series: selection_series
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
            if (currentSeriesNames.length > 0)
            {
              chartOptionsOriginal.value.series[index] = createSeries(
                  index,
                  data,
                  dataSelect.value,
                  currentSeriesNames[index],
                  obfuscatedColors[index]
              );
            }
            else
            {
              chartOptionsOriginal.value.series[index] = createSeries(
                  index,
                  data,
                  dataSelect.value,
                  undefined,
                  obfuscatedColors[index]
              );
            }

          });

          if (missingRate.value != "0")
          {
            // Adding ground truth series to the chart
            groundtruthMatrix.forEach((data: number[], index: number) => {

              if (selection_series.some(sel => sel.includes(currentSeriesNames[index].toString())))
              {
                chartOptionsOriginal.value.series.push(createSeries(
                    index,
                    data,
                    dataSelect.value,
                    currentSeriesNames[index] + "_MV",
                    'dash',
                    1,
                    obfuscatedColors[index]
                ));
              }
            });
            }

          mySeries.value = []
          for (let i = -1; i < currentSeriesNames.length && i < 4; i++)
          {
            mySeries.value.push(`${i + 1}: ${currentSeriesNames[i+1]}`);
          }

        } catch (error) {
          console.error(error);
        } finally {
          loadingResults.value = false;
        }
      }
    }



    const handleCheckboxChange = async () => {
      // Clear the existing series
      // chartOptionsImputed.value.series = [];
      loadingResults.value = true;
      imputedData.value = false;
      loadingResults.value = false;
    };

    const chartOptionsOriginal = ref(generateChartOptionsLarge('', 'Data Contamination'));


    const submitForm = async () => {

      if (document.activeElement.id === "alpha_run")
      {
        imputedData.value = false;
        await fetchData();
      }
      if (document.activeElement.id === "delta_reset")
      {
        location.reload();
      }
      await handleCheckboxChange();
    }


    // Define a new function that calls fetchData
    const handleDataSelectChange = async () => {
      try {
        imputedData.value = false;

        await fetchData();
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    }

        // Define a new function that calls fetchData
    const handleSeriesSelectChange = async () => {
      try {
        fetchData();
        submitForm();
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
        await submitForm();
      }
      catch (error)
      {
        console.error("Error handling parameter selection:", error);
      }
    }
    const handleNormalizationModeChange = () => {
      if (imputedData.value == true) {
        fetchData();
        submitForm();
      } else {
        handleDataSelectChange();
      }
    }

    const handleScenarioMissingValuesChange = () => {
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
    watch([dataSelect], handleDataSelectChange, {immediate: true});
    watch(normalizationMode, handleNormalizationModeChange, {immediate: true});
    watch(scenarioMissingValues, handleScenarioMissingValuesChange, {immediate: true});


    return {
      submitForm,
      chartOptionsOriginal,
      dataSelect,
      seriesSelect,
      normalizationMode,
      updateSeriesNames,
      missingRate,
      mySeries,
      selectedSeries,
      scenarioMissingValues,
      imputedData,
      checkedNames,
      handleCheckboxChange,
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

