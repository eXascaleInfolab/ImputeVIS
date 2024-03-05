<template>
    <div>
      <canvas ref="kiviatChart"></canvas>
    </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';
import Chart from 'chart.js/auto';

export default defineComponent({
  name: 'MetricsKiviatDisplay',
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
