<template>

  <div class="mb-3">
    <label for="dataSelect" class="form-label">Data:</label>
    <select id="dataSelect" v-model="selectedData" class="form-control">
      <!--            <option value="BAFU">BAFU</option>-->
      <option value="BAFU_half">BAFU 1/2 Size</option>
      <option value="BAFU_quarter">BAFU 1/4 Size</option>
      <!--      <option value="BAFU_sixth">BAFU 1/6 Size</option>-->
      <option value="BAFU_eighth">BAFU 1/8 Size</option>
      <!--            <option value="cl2fullLarge">Chlorine</option>-->
      <option value="cl2fullLarge_half">Chlorine 1/2 Size</option>
      <option value="cl2fullLarge_quarter">Chlorine 1/4 Size</option>
      <!--      <option value="cl2fullLarge_sixth">Chlorine 1/6 Size</option>-->
      <option value="cl2fullLarge_eighth">Chlorine 1/8 Size</option>
      <!--            <option value="climate">Climate</option>-->
      <option value="climate_half">Climate 1/2 Size</option>
      <option value="climate_quarter">Climate 1/4 Size</option>
      <!--      <option value="climate_sixth">Climate 1/6 Size</option>-->
      <option value="climate_eighth">Climate 1/8 Size</option>
      <!--      <option value="drift">Drift</option>-->
      <option value="batch10_half">Drift 1/2 Size</option>
      <option value="batch10_quarter">Drift 1/4 Size</option>
      <!--      <option value="batch10_sixth">Drift 1/6 Size</option>-->
      <option value="batch10_eighth">Drift 1/8 Size</option>
      <!--            <option value="meteo_total">Meteo</option>-->
      <option value="meteo_total_half">Meteo 1/2 Size</option>
      <option value="meteo_total_quarter">Meteo 1/4 Size</option>
      <!--      <option value="meteo_total_sixth">Meteo 1/6 Size</option>-->
      <option value="meteo_total_eighth">Meteo 1/8 Size</option>
    </select>
  </div>
</template>

<script lang="ts">
import {ref, watch, computed, defineComponent} from 'vue';


const bafu_series_names = [
    'Appenzell',
    'Halden',
    'Jonschwil',
    'Liestal',
    'Moutier',
    'Rheinhalle',
    'Wiler'
]

const climate_series_names = [
  'CLD',
  'CO',
  'DTR',
  'FRS',
  'H2',
  'PRE',
  'TMN',
  'TMP',
  'VAP',
  'WET'
]

const drift_series_names = [
  '0-6_EMAi0.1_0',
    '1-10_|DR|_1',
    '2-28_EMAi0.01_3',
    '3-18_|DR|_2',
    '4-58_|DR|_7',
    '5-21_EMAi0.001_2',
    '6-52_EMAi0.01_6',
    '7-124_EMAi0.01_15',
    '8-110_EMAi0.1_13',
    '9-36_EMAi0.01_4',
];
const meteo_series_names = [
  'tde000s0',
  'tre000s0',
  'trssurs0',
  'ure000s0',
];

export default defineComponent({
  name: 'DataSelect',
  props: {
    modelValue: {
      type: String,
      default: 'BAFU_eighth'
    }
  },
  computed: {
    selectedData: {
      get: function () {
        return this.modelValue;
      },
      set: function (newValue) {
        this.$emit('update:modelValue', newValue);
      }
    }
  },

  setup(props, {emit}) {
    const selectedData = ref(props.modelValue);

    watch(() => props.modelValue, (newVal) => {
      selectedData.value = newVal;
    });

    const updateSelectedData = (newVal) => {
      selectedData.value = newVal;
      emit('update:modelValue', newVal);
      emitSeriesNamesBasedOnSelection();
    };

    const emitSeriesNamesBasedOnSelection = () => {
      let seriesNames: string[] = [];
      switch (true) {
        case selectedData.value.toString().toLowerCase().startsWith("bafu"):
          console.log("entered BAFU")
          seriesNames = bafu_series_names;
          break;
        case selectedData.value.toString().startsWith("climate"):
          seriesNames = climate_series_names;
          break;
        case selectedData.value.toString().startsWith("batch10"):
          seriesNames = drift_series_names;
          break;
        case selectedData.value.toString().startsWith("meteo_total"):
          console.log("entered meteo_total")
          seriesNames = meteo_series_names;
          break;

        default:
          seriesNames = [];
          break;
          // ... add other conditions for more datasets as needed
      }
      emit('update:seriesNames', seriesNames);
    };

    // Watch for selectedData changes and emit series names
    watch(selectedData, emitSeriesNamesBasedOnSelection);
    emitSeriesNamesBasedOnSelection();
  }
});
</script>
