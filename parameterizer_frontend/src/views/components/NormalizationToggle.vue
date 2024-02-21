<template>
  <div class="btn-group btn-group-sm mb-n5" role="group" style="margin-bottom: 12px; margin-top:12px;">
    <button type="button"
            class="btn btn-sm"
            :class="{'btn-secondary': displayMode === 'Normal', 'btn-outline-secondary': displayMode !== 'Normal'}"
            @click="setDisplayMode('Normal')">Raw</button>
    <button type="button"
            class="btn btn-sm"
            :class="{'btn-secondary': displayMode === 'Normalized', 'btn-outline-secondary': displayMode !== 'Normalized'}"
            @click="setDisplayMode('Normalized')">Z-Score</button>
  </div>
</template>

<script lang="ts">
import {defineComponent, ref, watch} from 'vue';

export default defineComponent({
  name: 'NormalizationToggle',

  props: {
    modelValue: {
      type: String,
      default: 'Normal'
    }
  },

  setup(props, {emit}) {
    const displayMode = ref(props.modelValue);

    // Watch for external prop changes and adjust the internal state accordingly
    watch(() => props.modelValue, (newVal) => {
      displayMode.value = newVal;
    });

    const setDisplayMode = (mode) => {
      displayMode.value = mode;
      emit('update:modelValue', mode); // Emits the new mode to the parent
    };

    return {
      displayMode,
      setDisplayMode
    };
  }
});

</script>
