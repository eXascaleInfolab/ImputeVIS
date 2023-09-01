<template>
  <h3 class="mb-4 text-center">IIM Detail</h3>
  <div v-if="loadingResults" class="d-flex justify-content-center mt-3">
    <div class="alert alert-info d-flex align-items-center">
      <div class="spinner-border text-primary me-3" role="status"></div>
      Determining resulting imputation...
    </div>
  </div>
  <div class="d-flex mb-auto">
    <div class="col-lg-10 ps-4">
      <highcharts v-if="imputedData" :options="chartOptionsImputed"></highcharts>
      <highcharts :options="chartOptionsOriginal"></highcharts>
    </div>
    <div class="col-lg-2">
      <form @submit.prevent="submitForm" class="sidebar me-3">
        <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames"/>
        <normalization-toggle v-model="normalizationMode"></normalization-toggle>
        <missing-rate v-model="missingRate"/>

        <div class="mb-3">
          <label for="numberSelect" class="form-label">Select Learning Neighbors:</label>
          <br/>
          <div class="select-wrapper ">
            <select id="numberSelect" v-model="numberSelect" class="form-control me-5 pe-5">
              <option v-for="number in Array.from({ length: 100 }, (_, i) => i + 1)" :key="number">{{ number }}</option>
            </select>
          </div>
        </div>
        <!--        <div class="mb-3">-->
        <!--          <label for="typeSelect" class="form-label">Learning Type:</label>-->
        <!--          <select id="typeSelect" v-model="typeSelect" class="form-control">-->
        <!--            <option value="">Normal</option>-->
        <!--            <option value="a">Adaptive (High Processing Cost)</option>-->
        <!--          </select>-->
        <!--        </div>-->
        <button type="submit" class="btn btn-primary">Impute</button>
        <div class="mt-3">
          <metrics-display v-if="imputedData" :metrics="metrics"></metrics-display>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, watch, computed} from 'vue';
import DataSelect from '../components/DataSelect.vue';
import MetricsDisplay from '../components/MetricsDisplay.vue';
import MissingRate from '../components/MissingRate.vue';
import NormalizationToggle from '../components/NormalizationToggle.vue'
import axios from 'axios';
import {Chart} from 'highcharts-vue'
import Highcharts from 'highcharts'
import HighchartsBoost from 'highcharts/modules/boost'
import {
  createSegmentedSeries,
  createSeries,
  generateChartOptions,
  generateChartOptionsLarge
} from "@/views/thesisUtils/utils";

// HighchartsBoost(Highcharts)

export default {
  components: {
    DataSelect,
    highcharts: Chart,
    MetricsDisplay,
    MissingRate,
    NormalizationToggle,
  },
  setup() {
    const dataSelect = ref('climate_eighth') // Default data
    const normalizationMode = ref('Normal')
    let currentSeriesNames = []; // Names of series currently displayed
    const missingRate = ref('1'); // Default missing rate is 1%
    const numberSelect = ref(1); // Default selected learning neighbors is 1
    const typeSelect = ref(''); // Default selected type is "Normal", denoted by an empty string
    const imputedData = ref(false); // Whether imputation has been carried out
    const rmse = ref(null);
    const mae = ref(null);
    const mi = ref(null);
    const corr = ref(null);
    let loadingResults = ref(false);

    let obfuscatedMatrix = [];
    const metrics = computed(() => ({rmse: rmse.value, mae: mae.value, mi: mi.value, corr: corr.value}));

    const fetchData = async () => {
      try {
        imputedData.value = false;
        let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
        const response = await axios.post('http://localhost:8000/api/fetchData/',
            {
              data_set: dataSet,
              normalization: normalizationMode.value,
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
        );
        chartOptionsOriginal.value.series.splice(0, chartOptionsOriginal.value.series.length);

        obfuscatedMatrix = response.data.matrix;
        response.data.matrix.forEach((data: number[], index: number) => {
          // Replace NaN with 0
          const cleanData = data.map(value => isNaN(value) ? 0 : value);
          if (currentSeriesNames.length > 0) {
            chartOptionsOriginal.value.series[index] = createSeries(index, cleanData, currentSeriesNames[index]);
          } else {
            chartOptionsOriginal.value.series[index] = createSeries(index, cleanData);
          }
        });
      } catch (error) {
        console.error(error);
      }
    }

    const submitForm = async () => {
      let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
      loadingResults.value = true;
      imputedData.value = false;
      try {
        const formattedAlgCode = `iim ${numberSelect.value}${typeSelect.value}`;
        const response = await axios.post('http://localhost:8000/api/iim/',
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
        rmse.value = response.data.rmse.toFixed(3);
        mae.value = response.data.mae.toFixed(3);
        mi.value = response.data.mi.toFixed(3);
        corr.value = response.data.corr.toFixed(3);
        chartOptionsImputed.value.series.length = 0;
        // Create a new array for the new series data
        const newSeriesData = [];

        const displayImputation = missingRate.value != '40' && missingRate.value != '60' && missingRate.value != '80'
        response.data.matrix_imputed.forEach((data: number[], index: number) => {
          if (currentSeriesNames.length > 0 && missingRate) {
            if (displayImputation) {
              newSeriesData.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value, currentSeriesNames[index]));
            } else {
              newSeriesData.push(createSeries(index, data, currentSeriesNames[index]));
            }
          } else {
            if (displayImputation) {
              newSeriesData.push(...createSegmentedSeries(index, data, obfuscatedMatrix[index], chartOptionsImputed.value));
            } else {
              newSeriesData.push(createSeries(index, data))
            }
          }
        });
        // Directly modify the existing object without deep cloning
        chartOptionsImputed.value.series = newSeriesData;
        imputedData.value = true;
      } catch (error) {
        console.error(error);
      } finally {
        loadingResults.value = false;
      }
    }

    const chartOptionsOriginal = ref(generateChartOptions('Original Data', 'Data'));
    const chartOptionsImputed = ref(generateChartOptionsLarge('Imputed Data', 'Data'));

    // Define a new function that calls fetchData
    const handleDataSelectChange = () => {
      chartOptionsImputed.value = generateChartOptionsLarge('Imputed Data', 'Data')
      fetchData();
    }

    const updateSeriesNames = (newSeriesNames) => {
      currentSeriesNames = newSeriesNames;
    };

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


    return {
      submitForm,
      metrics,
      chartOptionsOriginal,
      chartOptionsImputed,
      updateSeriesNames,
      numberSelect,
      typeSelect,
      dataSelect,
      normalizationMode,
      missingRate,
      loadingResults,
      imputedData
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px; /* Change this value to increase or decrease the margin */
}
</style>

