<template>
  <div class="mb-3" data-toggle="tooltip" data-placement="top"
       title="Also impacts run-time, amount depends on algorithm.">
    <label for="missingRate" class="form-label">MCAR Rate: {{ sliderValue }}</label>
    <input type="range"
           id="missingRate"
           v-model="sliderValue"
           class="form-control"
           min="1"
           max="40"
           step="1"
           list="tickmarks"
           @input="adjustSliderValue">
    <datalist id="tickmarks">
      <option value="1" label="1%">1%</option>
      <option value="5" label="5%">5%</option>
      <option value="10" label="10%">10%</option>
      <option value="20" label="20%">20%</option>
      <option value="40" label="40%">40%</option>
    </datalist>
  </div>
</template>

<script lang="ts">
import {defineComponent, ref} from 'vue';

export default defineComponent({
  name: 'MissingRate',
  props: {
    modelValue: {
      type: String,
      default: '10'
    }
  },
  setup(props, {emit}) {
    const sliderValue = ref(props.modelValue);

    const adjustSliderValue = () => {
      const allowedValues = [1, 5, 10, 20, 40];
      let closest = allowedValues.reduce((prev, curr) => {
        return (Math.abs(Number(curr) - Number(sliderValue.value)) < Math.abs(Number(prev) - Number(sliderValue.value)) ? curr : prev);
      });
      sliderValue.value = String(closest);
      emit('update:modelValue', sliderValue.value);
    };

    return {
      sliderValue,
      adjustSliderValue
    };
  }
});
</script>
