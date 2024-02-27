<template>
  <div class="col-md-12 offset-md-12">
    <div class="row">
      <div class="col-2" style="width: 40%;">
        <table class="table table-bordered">
          <thead class="thead-dark">
          <tr>
            <th scope="col" style="width: 50%">Metric</th>
            <th scope="col" style="width: 50%">Value</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="(value, key) in metrics" :key="key" v-if="value !== null && value !== ''">
            <td>{{ key.toUpperCase() }}</td>
            <td>{{ value }}</td>
          </tr>
          </tbody>
        </table>
      </div>
      <div class="col-10" style="width: 60%; text-align: center;">
        <canvas ref="kiviatChart"></canvas>
      </div>
    </div>
  </div>

</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';
import Chart from 'chart.js/auto';

export default defineComponent({
  name: 'MetricsDisplay',
  props: {
    metrics: {
      type: Object as PropType<{ [key: string]: number | null }>,
      required: true,
    },
  },
  mounted() {
    this.createKiviatChart();
  },
  methods: {
    createKiviatChart() {
      const ctx = this.$refs.kiviatChart.getContext('2d');

    // Function to normalize a value based on specific metric details
          function normalizeMetricValue(value, min, max) {
            // Ensure the value is within the specified range
            const clampedValue = Math.min(Math.max(value, min), max);

            // Normalize the clamped value between 0 and 1
            return (clampedValue - min) / (max - min);
          }

    // Extract values from the metrics object
          const metricValues = Object.values(this.metrics);

    // Define normalization details for each metric
          const normalizationDetails = [
            { min: 0, max: 150 },
            { min: 0, max: 75 },
            { min: 0, max: 1.5 },
            { min: 0, max: 1 },
          ];

    // Normalize each value based on the corresponding metric details
          const normalizedValues = metricValues.map((value, index) => {
            const { min, max } = normalizationDetails[index];
            return (value !== undefined ? normalizeMetricValue(value, min, max) : 0);
          });

      new Chart(ctx, {
        type: 'radar',
        data: {
          labels: ['RMSE', 'MAE', 'MI', 'CORR'],
          datasets: [
            {
              label: 'Metrics',
              data: normalizedValues,
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              borderColor: 'rgba(75, 192, 192, 1)',
              pointBackgroundColor: 'rgba(75, 192, 192, 1)',
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: 'rgba(75, 192, 192, 1)',
            },
          ],
        },
      });
    },
  },
});
</script>
