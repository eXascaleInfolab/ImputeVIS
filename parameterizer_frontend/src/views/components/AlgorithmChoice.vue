<template>
  <div class="mb-3" data-toggle="tooltip" data-placement="top"  style="margin-bottom: 12px; margin-top:12px;"
       title="Also impacts run-time, amount depends on algorithm.">
    <label for="algos" class="form-label">Algorithm:</label>

    <!-- Dropdown for MCAR Rate -->
    <div class="custom-select">
        <select v-model="algorithmChoice" id="scenarioMissingValues" class="form-control" @change="adjustAlgorithm">
        <option value="cdrec">CDRec</option>
        <option value="iim">IIM</option>
        <option value="mrnn">M-RNN</option>
        <option value="stmvl">ST-MVL</option>
      </select>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'algorithmChoice',
  props: {
    modelValue: {
      type: String,
      default: 'CDRec',
    },
  },
  setup(props, { emit }) {
    const algorithmChoice = ref(props.modelValue);

    const adjustAlgorithm = () => {
      emit('update:modelValue', algorithmChoice.value);
    };

    return {
      algorithmChoice,
      adjustAlgorithm,
    };
  },
});
</script>
