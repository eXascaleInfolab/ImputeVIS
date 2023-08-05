<template>
  <div class="row">
    <div class="col-xs" v-for="(value, key) in metrics" :key="key">
      <h6 v-if="value !== null && value !== ''"> {{ key.toUpperCase() }}: {{ value }}</h6>
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