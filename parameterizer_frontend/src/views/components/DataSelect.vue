<template>
  <div class="mb-n5" data-toggle="tooltip" data-placement="top"
       title="For faster results, consider selecting the 1/8 size dataset">
    <label for="dataSelect" class="form-label">Dataset:</label>
    <br/>
    <span class="glyphicon glyphicon-info-sign info-icon" data-toggle="tooltip" data-placement="right"
          title="For faster results, consider selecting the 1/8 size dataset"></span>

    <div class="mb-3" data-toggle="tooltip" data-placement="top" >
      <div class="custom-select">

        <select id="dataSelect" v-model="selectedData" class="form-control me-5 pe-5">
          <option value="drift">Drift</option>
          <option value="bafu">BAFU</option>
          <option value="chlorine">Chlorine</option>
          <option value="climate">Climate</option>
          <option value="meteo">Meteo</option>
          <option value="upload" @click="uploadFile" >Upload...</option>
        </select>
      </div>

       <div v-if="selectedData === 'upload'">
          <input type="file" ref="fileInput" @change="uploadFile" style="margin-top:6px; width:100px;  ">
       </div>

    </div>
  </div>
</template>

<script lang="ts">
import {ref, watch, defineComponent} from 'vue';


const bafu_series_names = [
  'Thur-Andelfingen',
  'Emme-Emmenmatt',
  'Sitter-Appenzell',
  'Murg-Wängi',
  'Emme-Wiler',
  'Thur-Halden',
  'Thur-Jonschwil',
  'Murg-Frauenfeld',
  'Emme-Eggowoö',
  'Rietholzbach-Mosnang',
  'Sitter-St. Gallen',
  'Ilfis-Langnau'
]

// Based on https://viterbi-web.usc.edu/~liu32/data.html
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
'DR_1', '|DR|_1', 'EMAi0.001_1', 'EMAi0.01_1', 'EMAi0.1_1', 'EMAd0.001_1', 'EMAd0.01_1', 'EMAd0.1_1',
  'DR_2', '|DR|_2']

// Based on https://archive.ics.uci.edu/dataset/270/gas+sensor+array+drift+dataset+at+different+concentrations
const drift_series_names_full = [
  // '0-6_EMAi0.1_0',
  //   '1-10_|DR|_1',
  //   '2-28_EMAi0.01_3',
  //   '3-18_|DR|_2',
  //   '4-58_|DR|_7',
  //   '5-21_EMAi0.001_2',
  //   '6-52_EMAi0.01_6',
  //   '7-124_EMAi0.01_15',
  //   '8-110_EMAi0.1_13',
  //   '9-36_EMAi0.01_4',
  'DR_1', '|DR|_1', 'EMAi0.001_1', 'EMAi0.01_1', 'EMAi0.1_1', 'EMAd0.001_1', 'EMAd0.01_1', 'EMAd0.1_1',
  'DR_2', '|DR|_2', 'EMAi0.001_2', 'EMAi0.01_2', 'EMAi0.1_2', 'EMAd0.001_2', 'EMAd0.01_2', 'EMAd0.1_2',
  'DR_3', '|DR|_3', 'EMAi0.001_3', 'EMAi0.01_3', 'EMAi0.1_3', 'EMAd0.001_3', 'EMAd0.01_3', 'EMAd0.1_3',
  'DR_4', '|DR|_4', 'EMAi0.001_4', 'EMAi0.01_4', 'EMAi0.1_4', 'EMAd0.001_4', 'EMAd0.01_4', 'EMAd0.1_4',
  'DR_5', '|DR|_5', 'EMAi0.001_5', 'EMAi0.01_5', 'EMAi0.1_5', 'EMAd0.001_5', 'EMAd0.01_5', 'EMAd0.1_5',
  'DR_6', '|DR|_6', 'EMAi0.001_6', 'EMAi0.01_6', 'EMAi0.1_6', 'EMAd0.001_6', 'EMAd0.01_6', 'EMAd0.1_6',
  'DR_7', '|DR|_7', 'EMAi0.001_7', 'EMAi0.01_7', 'EMAi0.1_7', 'EMAd0.001_7', 'EMAd0.01_7', 'EMAd0.1_7',
  'DR_8', '|DR|_8', 'EMAi0.001_8', 'EMAi0.01_8', 'EMAi0.1_8', 'EMAd0.001_8', 'EMAd0.01_8', 'EMAd0.1_8',
  'DR_9', '|DR|_9', 'EMAi0.001_9', 'EMAi0.01_9', 'EMAi0.1_9', 'EMAd0.001_9', 'EMAd0.01_9', 'EMAd0.1_9',
  'DR_10', '|DR|_10', 'EMAi0.001_10', 'EMAi0.01_10', 'EMAi0.1_10', 'EMAd0.001_10', 'EMAd0.01_10', 'EMAd0.1_10',
  'DR_11', '|DR|_11', 'EMAi0.001_11', 'EMAi0.01_11', 'EMAi0.1_11', 'EMAd0.001_11', 'EMAd0.01_11', 'EMAd0.1_11',
  'DR_12', '|DR|_12', 'EMAi0.001_12', 'EMAi0.01_12', 'EMAi0.1_12', 'EMAd0.001_12', 'EMAd0.01_12', 'EMAd0.1_12',
  'DR_13', '|DR|_13', 'EMAi0.001_13', 'EMAi0.01_13', 'EMAi0.1_13', 'EMAd0.001_13', 'EMAd0.01_13', 'EMAd0.1_13',
  'DR_14', '|DR|_14', 'EMAi0.001_14', 'EMAi0.01_14', 'EMAi0.1_14', 'EMAd0.001_14', 'EMAd0.01_14', 'EMAd0.1_14',
  'DR_15', '|DR|_15', 'EMAi0.001_15', 'EMAi0.01_15', 'EMAi0.1_15', 'EMAd0.001_15', 'EMAd0.01_15', 'EMAd0.1_15',
  'DR_16', '|DR|_16', 'EMAi0.001_16', 'EMAi0.01_16', 'EMAi0.1_16', 'EMAd0.001_16', 'EMAd0.01_16', 'EMAd0.1_16',
];
const meteo_series_names = [
  'tde000s0',
  'tre000s0',
  'trssurs0',
  'ure000s0',
  'tde000s1',
  'tre000s1',
  'trssurs1',
  'ure000s1',
  'tde000s2',
  'tre000s2',
  'trssurs2',
  'ure000s2',
];

const chlorine_series_names = [
  'Series A',
  'Series B',
  'Series C',
  'Series D',
  'Series E',
  'Series F',
  'Series G',
  'Series H',
  'Series I',
  'Series J',
  'Series K',
  'Series L',
];

const others = [
  'Series A',
  'Series B',
  'Series C',
  'Series D',
  'Series E',
  'Series F',
  'Series G',
  'Series H',
  'Series I',
  'Series J',
  'Series K',
  'Series L',
];


export default defineComponent({
  name: 'DataSelect',
  props: {
    modelValue: {
      type: String,
      default: 'climate_eighth'
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
  methods: {
    uploadFile() {
      const file = this.$refs.fileInput.files[0];
      if (file) {
        // Here you can write code to upload the file
        console.log('File uploaded:', file.name);
      } else {
        console.log('Please select a file');
      }
    }
  },

  setup(props, {emit}) {
    const selectedData = ref(props.modelValue);

    watch(() => props.modelValue, (newVal) => {
      selectedData.value = newVal;
    });

    const emitSeriesNamesBasedOnSelection = () => {
      const datasetMapping: { [key: string]: string[] } = {
        "bafu": bafu_series_names,
        "climate": climate_series_names,
        "drift": drift_series_names,
        "meteo": meteo_series_names,
        "chlorine": chlorine_series_names,
        // ... add other conditions for more datasets as needed
      };

      const selectedValue = selectedData.value.toString().toLowerCase();

      let seriesNames: string[] = others; // Default assignment to 'others' array

      for (const [key, value] of Object.entries(datasetMapping)) {
        if (selectedValue.startsWith(key)) {
          seriesNames = value;
          break;
        }
      }

      emit('update:seriesNames', seriesNames);
    };

    // Watch for selectedData changes and emit series names
    watch(selectedData, emitSeriesNamesBasedOnSelection);
    emitSeriesNamesBasedOnSelection();
  }
});
</script>
