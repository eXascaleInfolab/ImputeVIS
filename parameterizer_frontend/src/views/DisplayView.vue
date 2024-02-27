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
          <div class="col-lg-12">
            <highcharts class="mb-5 pb-5" :options="chartOptionsOriginal" style="margin-top: 30px;"></highcharts>
          </div>
          <div class="col-lg-2" style="padding: 10px; position: absolute; z-index: 100; right: 150px; top:75px;">
            <form ref="ref_missingvalues" @submit.prevent="submitForm">
              <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames"/>
            </form>
          </div>
          <form ref="ref_missingvalues" @submit.prevent="submitForm">
            <div style="padding: 10px; position: absolute; z-index: 100; right: 0; top:100px;">
              <normalization-toggle v-model="normalizationMode"   ></normalization-toggle>
            </div>
          </form>

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
    let loadingResults = ref(false);
    const selectedParamOption = ref('recommended'); // Default option


    //CDRec Parameters
    const missingRate = ref('0'); // Default missing rate
    const scenarioMissingValues = ref('MCAR'); // Default scenarios

    let obfuscatedMatrix = [];
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

<script setup lang="ts">
</script>