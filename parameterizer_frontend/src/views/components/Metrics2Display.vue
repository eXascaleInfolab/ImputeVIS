<template>
  <div class="row">
    <div class="col-xs">
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
  },
});
</script>