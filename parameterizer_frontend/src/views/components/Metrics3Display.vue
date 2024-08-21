<template>
  <div class="row">
    <div class="col-xs">
      <table class="table table-bordered">
        <thead class="thead-dark">
        <tr>
          <th scope="col" style="width: 40%">Metrics</th>
          <th scope="col" style="width: 30%">Optimal Results</th>
          <th scope="col" style="width: 30%">Default Results</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(value, key, index) in metrics" :key="key" v-if="value !== null && value !== ''">
          <td>{{ key.toUpperCase() }}</td>
          <td>{{ value }}</td>
          <td>{{ default_values[index] }}</td> <!-- This will display the value from default_values based on the index -->
        </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>


<script lang="ts">
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  name: 'MetricsDisplay',
  props: {
    metrics: {
      type: Object as PropType<{ [key: string]: number | null }>,
      required: true,
    },
     default_values: {
      type: Array as PropType<number[]>,
      required: true,
    },
  },
});
</script>