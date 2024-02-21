<template>
  <div class="mb-3" data-toggle="tooltip" data-placement="top" style="margin-bottom: 12px; margin-top:12px;"
       title="Also impacts run-time, amount depends on algorithm.">
    <label for="missingRate" class="form-label">Contamination Rate:</label>

    <!-- Dropdown for MCAR Rate -->
    <select v-model="missingValue" id="missingRate" class="form-control" @change="adjustMissingValues">
      <option value="0">0%</option>
      <option value="1">1%</option>
      <option value="5">5%</option>
      <option value="10">10%</option>
      <option value="20">20%</option>
      <option value="40">40%</option>
      <option value="60">60%</option>
      <option value="80">80%</option>
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
      default: '0',
    },
  },
  setup(props, { emit }) {
    const missingValue = ref(props.modelValue);

    const adjustMissingValues = () => {
      emit('update:modelValue', missingValue.value);
    };

    return {
      missingValue,
      adjustMissingValues,
    };
  },
});
</script>
