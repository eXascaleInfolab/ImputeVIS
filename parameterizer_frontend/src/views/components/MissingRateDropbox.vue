<template>
  <div class="mb-3" data-toggle="tooltip" data-placement="top"
       title="Also impacts run-time, amount depends on algorithm.">
    <label for="missingRate" class="form-label">MCAR Rate: {{ sliderValue }}%</label>

    <!-- Dropdown for MCAR Rate -->
    <select v-model="sliderValue" id="missingRate" class="form-control" @change="adjustSliderValue">
      <option value="1">1%</option>
      <option value="5">5%</option>
      <option value="10">10%</option>
      <option value="20">20%</option>
      <option value="40">40%</option>
      <option value="50">50%</option>
    </select>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'MissingRate',
  props: {
    modelValue: {
      type: String,
      default: '10',
    },
  },
  setup(props, { emit }) {
    const sliderValue = ref(props.modelValue);

    const adjustSliderValue = () => {
      emit('update:modelValue', sliderValue.value);
    };

    return {
      sliderValue,
      adjustSliderValue,
    };
  },
});
</script>
