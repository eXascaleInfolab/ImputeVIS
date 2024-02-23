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
            <div class="justify-content-right" style="padding: 10px; position: absolute; z-index: 100; right: 0;">
               <button type="submit" id="delta_reset" class="btn align-center" style="background-color: #f0f0f0; padding: 10px;">
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
                <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames"/>
                <normalization-toggle v-model="normalizationMode"></normalization-toggle>
                <scenario-missing-values v-model="scenarioMissingValues"/>
                <missing-rate v-model="missingRate"/>
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
    MissingRate,
    ScenarioMissingValues
  }, setup() {
    const route = useRoute()
    const dataSelect = ref(route.params.datasetName || 'climate_eighth') // Default data is BAFU
    const normalizationMode = ref('Normal')
    let currentSeriesNames = []; // Names of series currently displayed
    const fetchedData = reactive({});
    let loadingResults = ref(true);
    const selectedParamOption = ref('recommended'); // Default option


    //CDRec Parameters
    const missingRate = ref('0'); // Default missing rate
    const scenarioMissingValues = ref('MCAR'); // Default scenarios

    let obfuscatedMatrix = [];
    let groundtruthMatrix = [];
    const checkedNames = ref([]);
    const imputedData = ref(false); // Whether imputation has been carried out


    const fetchData = async () => {
      try
      {
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

        obfuscatedMatrix = response.data.matrix;
        groundtruthMatrix = response.data.groundtruth;

        obfuscatedMatrix.forEach((data: number[], index: number) => {
          if (currentSeriesNames.length > 0) {
            chartOptionsOriginal.value.series[index] = createSeries(
                index,
                data,
                dataSelect.value,
                currentSeriesNames[index]
            );
          } else {
            chartOptionsOriginal.value.series[index] = createSeries(
                index,
                data,
                dataSelect.value
            );
          }
        });

        if(missingRate.value != "0")
        {
          // Adding ground truth series to the chart
          groundtruthMatrix.forEach((data: number[], index: number) => {
            chartOptionsOriginal.value.series.push(createSeries(
                index,
                data,
                dataSelect.value,
                currentSeriesNames[index] + " Missing values",
                'dash'
            ));
          });
        }

      }
      catch (error)
      {
        console.error(error);
      }
      finally
      {
        loadingResults.value = false;
      }
    }



    const handleCheckboxChange = async () => {
      // Clear the existing series
      // chartOptionsImputed.value.series = [];
      loadingResults.value = true;
      imputedData.value = false;
      chartOptionsOriginal.value.series.splice(0, chartOptionsOriginal.value.series.length)
      loadingResults.value = false;
    };

    const chartOptionsOriginal = ref(generateChartOptionsLarge('', 'Data'));



    const submitForm = async () => {

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
    watch([dataSelect, missingRate, scenarioMissingValues], handleDataSelectChange, {immediate: true});
    watch(normalizationMode, handleNormalizationModeChange, {immediate: true});

    return {
      submitForm,
      chartOptionsOriginal,
      dataSelect,
      normalizationMode,
      updateSeriesNames,
      missingRate,
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

