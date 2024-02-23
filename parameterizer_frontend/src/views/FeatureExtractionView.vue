<template>
  <h4 class="mb-4 text-center" style="margin-top:40px;margin-bottom:40px;">Dataset Feature Extractor</h4>
  <div class="d-flex mb-auto">
    <div class="col-lg-10">
      <div v-if="loading" class="d-flex justify-content-center mt-3">
        <div class="alert alert-info d-flex align-items-center">
          <div class="spinner-border text-primary me-3" role="status"></div>
          Loading, please wait...
        </div>
      </div>

      <div v-else-if="error" class="mt-3 alert alert-danger">
        {{ error }}
      </div>


      <div v-else class="mt-2 ms-5">
        <!-- Geometry Table -->
        <div>
          <h4>Geometry</h4>
          <table class="table"  style="margin-bottom: 50px;">
            <thead>
            <tr>
              <th  style="width: 90%;" >Feature Name</th>
              <th  style="width: 10%;" >Value</th>
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
        <div>
          <h4>Correlation</h4>
          <table class="table"  style="margin-bottom: 50px;">
            <thead>
            <tr>
              <th style="width: 90%;" >Feature Name</th>
              <th style="width: 10%;" >Value</th>
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
        <div class="mb-4">
          <h4>Transformation</h4>
          <table class="table"  style="margin-bottom: 50px;">
            <thead>
            <tr>
              <th style="width: 90%;">Feature Name</th>
              <th style="width: 10%;" >Value</th>
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

        <!-- Trend Table <div v-if="loadedResults && categoryExists('Trend')" class="mb-4">
 -->
        <div>
          <h4>Trend</h4>
          <table class="table"  style="margin-bottom: 50px;">
            <thead>
            <tr>
              <th style="width: 90%;">Feature Name</th>
              <th style="width: 10%;">Value</th>
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
    </div>



    <form ref="ref_reload" @submit.prevent="submitForm">
      <div class="justify-content-right" style="padding: 10px; position: absolute; z-index: 100; right: 0; top: 60px;">
        <button type="submit" id="delta_reset" class="btn align-center" style="background-color: #f0f0f0; padding: 10px;">
          <svg xmlns="http://www.w3.org/2000/svg" width="1.5em" height="1.5em" viewBox="-2 0 24 24" style="margin-top: -2px; margin-right: 4px;">
            <path fill="currentColor" d="M2 12a9 9 0 0 0 9 9c2.39 0 4.68-.94 6.4-2.6l-1.5-1.5A6.706 6.706 0 0 1 11 19c-6.24 0-9.36-7.54-4.95-11.95C10.46 2.64 18 5.77 18 12h-3l4 4h.1l3.9-4h-3a9 9 0 0 0-18 0"/>
          </svg>
        </button>
      </div>
    </form>


    <div class="col-lg-2" style="margin-top: 10px;">
      <div class="sidebar me-5">
        <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames" class="mb-5"/>
        Impacts only data display <br/>
        <normalization-toggle v-model="normalizationMode"></normalization-toggle>
        <br/>
        <button type="submit" class="btn btn-primary mt-5" @click="fetchDataFeatures">Extract Features</button>
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

HighchartsBoost(Highcharts)

export default {
  components: {
    DataSelect,
    highcharts: Chart,
    MetricsDisplay,
    MissingRate,
    NormalizationToggle
  }, setup() {
    const route = useRoute()
    const dataSelect = ref(route.params.datasetName || 'climate_eighth');
    const normalizationMode = ref('Normal')
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

    const featureDescriptionMapper: { [key: string]: string } = {
      "DN_HistogramMode_5": "5-bin histogram mode",
      "DN_HistogramMode_10": "10-bin histogram mode",
      "DN_OutlierInclude_p_001_mdrmd": "Positive outlier timing",
      "DN_OutlierInclude_n_001_mdrmd": "Negative outlier timing",
      "CO_f1ecac": "First 1/e crossing of the ACF",
      "CO_FirstMin_ac": "First minimum of the ACF",
      "SP_Summaries_welch_rect_area_5_1": "Power in the lowest 20% of frequencies",
      "SP_Summaries_welch_rect_centroid": "Centroid frequency",
      "FC_LocalSimple_mean3_stderr": "Error of 3-point rolling mean forecast",
      "FC_LocalSimple_mean1_tauresrat": "Change in autocorrelation timescale after incremental differencing",
      "MD_hrv_classic_pnn40": "Proportion of high incremental changes in the series",
      "SB_BinaryStats_mean_longstretch1": "Longest stretch of above-mean values",
      "SB_BinaryStats_diff_longstretch0": "Longest stretch of decreasing values",
      "SB_MotifThree_quantile_hh": "Entropy of successive pairs in symbolized series",
      "CO_HistogramAMI_even_2_5": "Histogram-based automutual information (lag 2, 5 bins)",
      "CO_trev_1_num": "Time reversibility",
      "IN_AutoMutualInfoStats_40_gaussian_fmmi": "First minimum of the AMI function",
      "SB_TransitionMatrix_3ac_sumdiagcov": "Transition matrix column variance",
      "PD_PeriodicityWang_th0_01": "Wang's periodicity metric",
      "CO_Embed2_Dist_tau_d_expfit_meandiff": "Goodness of exponential fit to embedding distance distribution",
      "SC_FluctAnal_2_rsrangeﬁt_50_1_logi_prop_r1": "Rescaled range fluctuation analysis (low-scale scaling)",
      "SC_FluctAnal_2_dfa_50_1_2_logi_prop_r1": "Detrended fluctuation analysis (low-scale scaling)",
      "mean": "Mean",
      "DN_Spread_Std": "Standard deviation"
    };

    function replaceFeatureNameWithDescription(inputString: string, mapper: { [key: string]: string }): string {
      for (const featureName in mapper) {
        if (featureName == inputString) {
          return mapper[featureName];
        }
      }
      return "";
    }

    function categorizeFeatures(features: FeatureMap): { [category: string]: FeatureMap } {
      const tempCategorizedFeatures: { [category: string]: FeatureMap } = {};

      for (const category in CATEGORIES) {
        tempCategorizedFeatures[category] = {};
        for (const featureKey of CATEGORIES[category]) {
          let featureVerbose = replaceFeatureNameWithDescription(featureKey, featureDescriptionMapper)
          if (features[featureKey] !== undefined) {
            tempCategorizedFeatures[category][featureVerbose] = features[featureKey];
          }
        }
      }
      return tempCategorizedFeatures;
    }

    const fetchData = async () => {
      try {
        loadedResults.value = false;
        let dataSet = `${dataSelect.value}_obfuscated_0`;
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

        response.data.matrix.forEach((data: number[], index: number) => {
          // Replace NaN with 0
          const cleanData = data.map(value => isNaN(value) ? 0 : value);
          if (currentSeriesNames.length > 0) {
            chartOptionsOriginal.value.series[index] = createSeries(index, cleanData, dataSelect.value, currentSeriesNames[index]);
          } else {
            chartOptionsOriginal.value.series[index] = createSeries(index, cleanData, dataSelect.value);
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
        let dataSet = `${dataSelect.value}_obfuscated_0`;
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
        categorizedFeatures.value = categorizeFeatures(response.data);
        loadedResults.value = true;
      } catch (error) {
        error.value = `Error: ${error.message}`;
        console.error(error);
      } finally {
        loading.value = false;
      }
    }

    const submitForm = async () => {
      if (document.activeElement.id === "delta_reset")
      {
        location.reload();
      }
    }

    // Define a new function that calls fetchData
    const handleDataSelectChange = () => {
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
      submitForm
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 55px; /* Change this value to increase or decrease the margin */
}
</style>
