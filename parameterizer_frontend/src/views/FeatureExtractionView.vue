<template>
  <h4 class="mb-4 text-center" style="margin-top:40px;margin-bottom:40px;">Dataset Feature Extractor</h4>
  <div class="d-flex mb-auto">
    <div class="col-lg-10">
      <div v-if="loading" class="d-flex justify-content-center mt-3" style="margin-left : 320px;">
        <div class="alert alert-info d-flex align-items-center">
          <div class="spinner-border text-primary me-3" role="status"></div>
          Loading, please wait...
        </div>
      </div>

      <div v-else-if="error" class="mt-3 alert alert-danger">
        {{ error }}
      </div>


      <div v-else class="mt-2 ms-5" v-if="featureResults.length > 0">
        <h4>Geometry</h4>
        <table class="table" style="margin-bottom: 50px;">
          <thead>
          <tr>
            <th style="width: 50%;">Feature Name</th>
            <th v-for="(result, index) in featureResults" :key="index" style="width: 10%;">{{ `${my_data[index]}` }}</th>
          </tr>
          </thead>

          <tbody>
          <tr>
            <td>
              <div v-for="(value, key) in categorizedFeatures['Geometry']" :key="key">
                <tr style="height: 10px;">{{ key }}</tr>
              </div>
            </td>
            <td v-for="(category, categoryIndex) in featureResults" :key="categoryIndex">
                <tr style="height: 10px;" v-for="(value, key) in category['Geometry']" :key="key">{{ (value.toFixed(4)).padEnd(7, '0') }}</tr>
            </td>
          </tr>
          </tbody>
        </table>


        <h4>Correlation</h4>
        <table class="table" style="margin-bottom: 50px;">
          <thead>
          <tr>
            <th style="width: 50%;">Feature Name</th>
            <th v-for="(result, index) in featureResults" :key="index" style="width: 10%;">{{ `${my_data[index]}` }}</th>
          </tr>
          </thead>

          <tbody>
          <tr>
            <td>
              <div v-for="(value, key) in categorizedFeatures['Correlation']" :key="key">
                <tr style="height: 10px;">{{ key }}</tr>
              </div>
            </td>
            <td v-for="(category, categoryIndex) in featureResults" :key="categoryIndex">
              <tr style="height: 10px;" v-for="(value, key) in category['Correlation']" :key="key">{{ (value.toFixed(4)).padEnd(7, '0') }}</tr>
            </td>
          </tr>
          </tbody>
        </table>





        <h4>Transformation</h4>
        <table class="table" style="margin-bottom: 50px;">
          <thead>
          <tr>
            <th style="width: 50%;">Feature Name</th>
            <th v-for="(result, index) in featureResults" :key="index" style="width: 10%;">{{ `${my_data[index]}` }}</th>
          </tr>
          </thead>

          <tbody>
          <tr>
            <td>
              <div v-for="(value, key) in categorizedFeatures['Transformation']" :key="key">
                <tr style="height: 10px;">{{ key }}</tr>
              </div>
            </td>
            <td v-for="(category, categoryIndex) in featureResults" :key="categoryIndex">
              <tr style="height: 10px;" v-for="(value, key) in category['Transformation']" :key="key">{{ (value.toFixed(4)).padEnd(7, '0') }}</tr>
            </td>
          </tr>
          </tbody>
        </table>


        <h4>Trend</h4>
        <table class="table" style="margin-bottom: 50px;">
          <thead>
          <tr>
            <th style="width: 50%;">Feature Name</th>
            <th v-for="(result, index) in featureResults" :key="index" style="width: 10%;">{{ `${my_data[index]}` }}</th>
          </tr>
          </thead>

          <tbody>
          <tr>
            <td>
              <div v-for="(value, key) in categorizedFeatures['Trend']" :key="key">
                <tr style="height: 10px;">{{ key }}</tr>
              </div>
            </td>
            <td v-for="(category, categoryIndex) in featureResults" :key="categoryIndex">
              <tr style="height: 10px;" v-for="(value, key) in category['Trend']" :key="key">{{ (value.toFixed(4)).padEnd(7, '0') }}</tr>
            </td>
          </tr>
          </tbody>
        </table>

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


    <div class="col-lg-2" style="margin-top: 10px;">
      <div class="sidebar me-5">
        <data-select v-model="dataSelect" @update:seriesNames="updateSeriesNames" class="mb-5"/>
        <button type="submit" class="btn btn-primary mt-5" @click="fetchDataFeatures">Extract</button>
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
import {createSeries, generateChartOptions, generateChartOptionsLarge} from "@/views/thesisUtils/utils";


export default {
  components: {
    DataSelect,
    MetricsDisplay,
    MissingRate,
    NormalizationToggle
  }, setup() {
    const route = useRoute()
    const dataSelect = ref(route.params.datasetName || 'chlorine');
    const normalizationMode = ref('Normal')
    let currentSeriesNames = []; // Names of series currently displayed
    const features = ref<Record<string, number>>({});
    const loading = ref(false)
    const error = ref("");
    const loadedResults = ref(false);
    const categorizedFeatures = ref({});
    const featureResults = ref([]); // New data property to store results
    const my_data = ref([]);
    const my_data_set =ref("");


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
      "SC_FluctAnal_2_rsrangefit_50_1_logi_prop_r1": "Rescaled range fluctuation analysis (low-scale scaling)",
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
      if (dataSelect.value !== "upload") {
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
        } catch (error) {
          console.error(error);
        }
      }
    }

    function categoryExists(category: string): boolean {
      return categorizedFeatures.value[category] && Object.keys(categorizedFeatures.value[category]).length > 0;
    }

    const fetchDataFeatures = async () => {
      if (dataSelect.value !== "upload") {
        loading.value = true;
        error.value = "";
        loadedResults.value = false;

        //switch (dataSelect.value) {
        //  case "BAFU_onetwentyeigth":
        //    my_data.value.push(`bafu`);
        //    break;
        //  case "cl2fullLarge_eighth":
        //    my_data.value.push(`chlorine`);
        //    break;
        //  case "climate_eighth":
        //    my_data.value.push(`climate`);
        //    break;
        //  case "batch10_eighth":
        //    my_data.value.push(`drift`);
        //    break;
        //  case "meteo_total_eighth":
        //    my_data.value.push(`meteo`);
        //    break;
        // }

        my_data.value.push(dataSelect.value);

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
          featureResults.value.push(categorizedFeatures.value);


          loadedResults.value = true;
        } catch (error) {
          error.value = `Error: ${error.message}`;
          console.error(error);
        } finally {
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
      categorizedFeatures,
      categoryExists,
      submitForm,
      featureResults,
      my_data,
      my_data_set
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 55px; /* Change this value to increase or decrease the margin */
}
</style>
