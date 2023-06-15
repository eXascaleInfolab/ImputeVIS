<template>
  <h1 class="mb-4 text-center">IIM Detail</h1>
  <div class="d-flex">
    <div class="col-lg-8">
      <h2> RMSE: {{ rmse }}</h2>
      <highcharts :options="chartOptions"></highcharts>
    </div>
    <div class="col-lg-4">
      <form @submit.prevent="submitForm" class="position-fixed sidebar">
        <div class="mb-3">
          <label for="alg_code" class="form-label">Algorithm Code:</label>
          <input id="alg_code" v-model="alg_code" type="text" class="form-control" required>
        </div>
        <div class="mb-3">
          <label for="numberSelect" class="form-label">Number Select:</label>
          <select id="numberSelect" v-model="numberSelect" class="form-control">
            <option v-for="number in Array.from({ length: 100 }, (_, i) => i + 1)" :key="number">{{ number }}</option>
          </select>
        </div>
        <div class="mb-3">
          <label for="typeSelect" class="form-label">Type Select:</label>
          <select id="typeSelect" v-model="typeSelect" class="form-control">
            <option value="Normal">Normal</option>
            <option value="Adaptive">Adaptive</option>
          </select>
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import {ref} from 'vue';
import axios from 'axios';
import {Chart} from 'highcharts-vue'
import Highcharts from 'highcharts'
import HC_exporting from 'highcharts/modules/exporting'
import HC_exportData from 'highcharts/modules/export-data'

// Initialize exporting modules
HC_exporting(Highcharts)
HC_exportData(Highcharts)

export default {
  components: {
    highcharts: Chart
  },
  setup() {

    const alg_code = ref('');
    const numberSelect = ref(1); // Default selected learning neighborsx§ is 1
    const typeSelect = ref('Normal'); // Default selected type is "Normal"
    const rmse = ref(null);

    const chartOptions = ref({
      title: {
        text: 'Time-series Data'
      },
      xAxis: {
        type: 'datetime'
      },
      series: [{
        data: [
          [Date.UTC(2023, 0, 1), 1],
          [Date.UTC(2023, 0, 2), 2],
          [Date.UTC(2023, 0, 3), 3],
          [Date.UTC(2023, 0, 4), 4],
          [Date.UTC(2023, 0, 5), 5],
          //... more data points
        ],
        name: 'Example Data',
        showInLegend: false
      }]
    });

    const submitForm = async () => {
      try {
        const response = await axios.post('http://localhost:8000/api/submit-name/',
            {
              alg_code: alg_code.value,
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
        );
        rmse.value = response.data.rmse;
        console.log(numberSelect.value); // You can use these in your form submission
        console.log(typeSelect.value); // You can use these in your form submission
        console.log(response.data);
      } catch (error) {
        console.error(error);
      }
    }

    return {
      alg_code,
      submitForm,
      rmse,
      chartOptions,
      numberSelect,
      typeSelect
    }
  }
}
</script>

<style scoped>
.sidebar {
  margin-left: 35px;  /* Change this value to increase or decrease the margin */
}
</style>

