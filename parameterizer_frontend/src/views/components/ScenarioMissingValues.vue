<template>
  <div class="mb-3" data-toggle="tooltip" data-placement="top"  style="margin-bottom: 12px; margin-top:12px;"
       title="Also impacts run-time, amount depends on algorithm.">
    <label for="scenarios" class="form-label" style="font-weight: bold;" >Pattern</label>

    <!-- Dropdown for MCAR Rate -->
    <div class="custom-select">
        <select v-model="scenarioMissingValues" id="scenarioMissingValues" class="form-control" @change="adjustScenarios">
          <option value="mcar">MCAR</option>
          <option value="missing_pourcentage">Missing Percentage</option>
          <option value="disjoint">Disjoint</option>
          <option value="overlap">Overlap</option>
          <option value="blackout">Blackout</option>
        </select>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'scenarioMissingValues',
  props: {
    modelValue: {
      type: String,
      default: 'mcar',
    },
  },
  setup(props, { emit }) {
    const scenarioMissingValues = ref(props.modelValue);

    const adjustScenarios = () => {
      emit('update:modelValue', scenarioMissingValues.value);
    };

    return {
      scenarioMissingValues,
      adjustScenarios,
    };
  },
});
</script>
