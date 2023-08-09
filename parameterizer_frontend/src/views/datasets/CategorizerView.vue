<template>
  <div class="d-flex mb-auto container mt-5">
    <div class="col-lg-8">
      <div v-if="loading" class="d-flex justify-content-center mt-3">
        <div class="alert alert-info d-flex align-items-center">
          <div class="spinner-border text-primary me-3" role="status"></div>
          Loading, please wait...
        </div>
      </div>

      <div v-else-if="error" class="mt-3 alert alert-danger">
        {{ error }}
      </div>

      <div v-else class="mt-3">
        <!-- Geometry Table -->
        <div v-if="loadedResults && categoryExists('Geometry')" class="mb-4">
          <h4>Geometry</h4>
          <table class="table">
            <thead>
            <tr>
              <th>Feature Name</th>
              <th>Value</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(value, key) in categorizedFeatures['Geometry']" :key="key">
              <td>{{ key }}</td>
              <td>{{ value.toFixed(4) }}</td>
            </tr>
            </tbody>
          </table>
        </div>

        <!-- Correlation Table -->
        <div v-if="loadedResults && categoryExists('Correlation')" class="mb-4">
          <h4>Correlation</h4>
          <table class="table">
            <thead>
            <tr>
              <th>Feature Name</th>
              <th>Value</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(value, key) in categorizedFeatures['Correlation']" :key="key">
              <td>{{ key }}</td>
              <td>{{ value.toFixed(4) }}</td>
            </tr>
            </tbody>
          </table>
        </div>

        <!-- Transformation Table -->
        <div v-if="loadedResults && categoryExists('Transformation')" class="mb-4">
          <h4>Transformation</h4>
          <table class="table">
            <thead>
            <tr>
              <th>Feature Name</th>
              <th>Value</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(value, key) in categorizedFeatures['Transformation']" :key="key">
              <td>{{ key }}</td>
              <td>{{ value.toFixed(4) }}</td>
            </tr>
            </tbody>
          </table>
        </div>

        <!-- Trend Table -->
        <div v-if="loadedResults && categoryExists('Trend')" class="mb-4">
          <h4>Trend</h4>
          <table class="table">
            <thead>
            <tr>
              <th>Feature Name</th>
              <th>Value</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(value, key) in categorizedFeatures['Trend']" :key="key">
              <td>{{ key }}</td>
              <td>{{ value.toFixed(4) }}</td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
      <highcharts :options="chartOptionsOriginal"></highcharts>
    </div>
    <div class="col-lg-4">
      <div class="sidebar col-lg-5">
        <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames"/>
        <button type="submit" class="btn btn-primary mt-5" @click="fetchDataFeatures">Get Features</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, watch, computed} from 'vue';
import DataSelect from '../components/DataSelect.vue';
import MetricsDisplay from '../components/MetricsDisplay.vue';
import MissingRate from '../components/MissingRate.vue';
import axios from 'axios';
import {Chart} from 'highcharts-vue'
import Highcharts from 'highcharts'
import HighchartsBoost from 'highcharts/modules/boost'
import {createSeries, generateChartOptions, generateChartOptionsLarge} from "@/views/thesisUtils/utils";

// Initialize exporting modules
HighchartsBoost(Highcharts)

export default {
  components: {
    DataSelect,
    highcharts: Chart,
    MetricsDisplay,
    MissingRate
  }, setup() {
    const dataSelect = ref('climate_eighth');
    let currentSeriesNames = []; // Names of series currently displayed
    const features = ref<Record<string, number>>({});
    const loading = ref(false)
    const error = ref("");
    const loadedResults = ref(false);
    const chartOptionsOriginal = ref(generateChartOptions('Data', 'Data'));
    const categorizedFeatures = ref({});

    // Define the features for each category
    const CATEGORIES = {
      'Geometry': [
        'SB_BinaryStats_mean_longstretch1',
        'SB_BinaryStats_diff_longstretch0',
        'SB_TransitionMatrix_3ac_sumdiagcov',
        'MD_hrv_classic_pnn40',
        'DN_HistogramMode_5',
        'DN_HistogramMode_10',
        'DN_OutlierInclude_p_001_mdrmd',
        'DN_OutlierInclude_n_001_mdrmd',
        'CO_Embed2_Dist_tau_d_expfit_meandiff',
        'SC_FluctAnal_2_dfa_50_1_2_logi_prop_r1',
        'SC_FluctAnal_2_rsrangefit_50_1_logi_prop_r1'
      ],
      'Correlation': [
        'CO_f1ecac',
        'CO_FirstMin_ac',
        'CO_trev_1_num',
        'CO_HistogramAMI_even_2_5',
        'IN_AutoMutualInfoStats_40_gaussian_fmmi',
        'FC_LocalSimple_mean1_tauresrat'
      ],
      'Transformation': [
        'SP_Summaries_welch_rect_area_5_1',
        'SP_Summaries_welch_rect_centroid'
      ],
      'Trend': [
        'PD_PeriodicityWang_th0_01',
        'FC_LocalSimple_mean3_stderr',
        'SB_MotifThree_quantile_hh'
      ]
    };
    type FeatureMap = { [key: string]: any };

    function categorizeFeatures(features: FeatureMap): { [category: string]: FeatureMap } {
      const tempCategorizedFeatures: { [category: string]: FeatureMap } = {};

      for (const category in CATEGORIES) {
        tempCategorizedFeatures[category] = {};
        for (const featureKey of CATEGORIES[category]) {
          if (features[featureKey] !== undefined) {
            tempCategorizedFeatures[category][featureKey] = features[featureKey];
          }
        }
      }
      return tempCategorizedFeatures;
    }

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

    function categoryExists(category: string): boolean {
      return categorizedFeatures.value[category] && Object.keys(categorizedFeatures.value[category]).length > 0;
    }

    const fetchDataFeatures = async () => {
      loading.value = true;
      error.value = "";
      loadedResults.value = false;
      try {
        let dataSet = `${dataSelect.value}_obfuscated_${missingRate.value}`;
        const response = await axios.post('http://localhost:8000/api/categorizeData/',
            {
              data_set: dataSet

            },
            {
              headers: {
                'Content-Type': 'application/text',
              }
            }
        );
        features.value = response.data;
        // features.value = await response.json();
        categorizedFeatures.value = categorizeFeatures(response.data);
        loadedResults.value = true;

      } catch (error) {
        error.value = `Error: ${error.message}`;
        console.error(error);
      } finally {
        loading.value = false;
      }
    }

    // Define a new function that calls fetchData
    const handleDataSelectChange = () => {
      fetchData();
    }

    const updateSeriesNames = (newSeriesNames) => {
      currentSeriesNames = newSeriesNames;
    };

    watch(dataSelect, handleDataSelectChange, {immediate: true});

    return {
      dataSelect,
      updateSeriesNames,
      features,
      loading,
      error,
      loadedResults,
      fetchDataFeatures,
      chartOptionsOriginal,
      categorizedFeatures,
      categoryExists
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px; /* Change this value to increase or decrease the margin */
}
</style>
