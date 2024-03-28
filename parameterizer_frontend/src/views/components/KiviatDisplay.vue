<template>
  <canvas ref="kiviatChart"></canvas>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';
import Chart from 'chart.js/auto';

export default defineComponent({
  name: 'KiviatDisplay',
  props: {
    metrics: {
      type: Object as PropType<{ [key: string]: { [metric: string]: number | null } }>,
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
      function normalizeMetricValue(value: number, min: number, max: number): number {
        // Ensure the value is within the specified range
        const clampedValue = Math.min(Math.max(value, min), max);

        // Normalize the clamped value between 0 and 1
        return (clampedValue - min) / (max - min);
      }

      // Extract values from the metrics object
      const algorithms = Object.keys(this.metrics);
      const metricValues = algorithms.map((algorithm) => {
        const algorithmMetrics = this.metrics[algorithm];
        return Object.values(algorithmMetrics);
      });

      // Define normalization details for each metric
      const normalizationDetails = [
        { min: 0, max: 200 },
        { min: 0, max: 100 },
        { min: 0, max: 1.5 },
        { min: 0, max: 1 },
      ];

      // Normalize each value based on the corresponding metric details
      const normalizedValues = metricValues.map((algorithmMetrics) => {
        return algorithmMetrics.map((value, index) => {
          const { min, max } = normalizationDetails[index];
          return value !== null ? normalizeMetricValue(value, min, max) : 0;
        });
      });

      new Chart(ctx, {
        type: 'radar',
        data: {
          labels: ['RMSE', 'MAE', 'MI', 'CORR'],
          datasets: [
            {
              label: 'CDRec',
              data: normalizedValues[0],
              backgroundColor: 'rgba(255, 0, 0, 0.2)',
              borderColor: 'rgba(255, 0, 0, 1)',
              pointBackgroundColor: 'rgba(255, 0, 0, 1)',
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: 'rgba(255, 0, 0, 1)',
            },
            {
              label: 'IIM',
              data: normalizedValues[1],
              backgroundColor: 'rgba(0, 255, 0, 0.2)',
              borderColor: 'rgba(0, 255, 0, 1)',
              pointBackgroundColor: 'rgba(0, 255, 0, 1)',
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: 'rgba(0, 255, 0, 1)',
            },
            {
              label: 'MRNN',
              data: normalizedValues[2],
              backgroundColor: 'rgba(0, 0, 255, 0.2)',
              borderColor: 'rgba(0, 0, 255, 1)',
              pointBackgroundColor: 'rgba(0, 0, 255, 1)',
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: 'rgba(0, 0, 255, 1)',
            },
            {
              label: 'STMVL',
              data: normalizedValues[3],
              backgroundColor: 'rgba(255, 255, 0, 0.2)',
              borderColor: 'rgba(255, 255, 0, 1)',
              pointBackgroundColor: 'rgba(255, 255, 0, 1)',
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: 'rgba(255, 255, 0, 1)',
            },
          ],
        },
      });
    },
  },
});
</script>
