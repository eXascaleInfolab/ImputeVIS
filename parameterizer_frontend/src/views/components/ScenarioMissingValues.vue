<template>
  <div class="mb-3" data-toggle="tooltip" data-placement="top"  style="margin-bottom: 12px; margin-top:12px;"
       title="Also impacts run-time, amount depends on algorithm.">
    <label for="scenarios" class="form-label">Scenario:</label>

    <!-- Dropdown for MCAR Rate -->
    <div class="custom-select">
        <select v-model="scenarioMissingValues" id="scenarioMissingValues" class="form-control" @change="adjustScenarios">
          <option value="obfuscated">MCAR</option>
          <option value="missingpourcentage">Missing Pourcentage</option>
          <option value="blackout">Blackout</option>
          <option value="overlap">Overlap</option>
          <option value="disjoint">Disjoint</option>
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
      default: 'MCAR',
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
