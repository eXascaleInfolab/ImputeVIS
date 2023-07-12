<template>
  <div class="mb-3">
    <label for="missingRate" class="form-label">Missing Rate:</label>
    <select id="missingRate" v-model="missingRate" class="form-control">
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
import {defineComponent} from 'vue';

export default defineComponent({
  name: 'MissingRate',
  props: {
    modelValue: {
      type: String,
      default: '10'
    }
  },
  computed: {
    missingRate: {
      get: function () {
        return this.modelValue;
      },
      set: function (newValue) {
        this.$emit('update:modelValue', newValue);
      }
    }
  }
});
</script>
