<template>
  <div class="container">
    <h1 class="mb-4">I am IIM page.</h1>
    <form @submit.prevent="submitForm">
      <div class="mb-3">
        <label for="name" class="form-label">Name:</label>
        <input id="name" v-model="name" type="text" class="form-control" required>
      </div>

      <div class="mb-3">
        <label for="alg_code" class="form-label">Algorithm Code:</label>
        <input id="alg_code" v-model="alg_code" type="text" class="form-control" required>
      </div>

      <button type="submit" class="btn btn-primary">Submit</button>
    </form>

    <h2> RMSE: {{ rmse }}</h2>

    <highcharts :options="chartOptions"></highcharts>
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
    const name = ref('');
    const alg_code = ref('');
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
              name: name.value,
              alg_code: alg_code.value,
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
        );
        rmse.value = response.data.rmse;
        console.log(response.data);
      } catch (error) {
        console.error(error);
      }
    }

    return {
      name,
      alg_code,
      submitForm,
      rmse,
      chartOptions
    }
  }
}
</script>
