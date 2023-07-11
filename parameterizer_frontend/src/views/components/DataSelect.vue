<template>

  <div class="mb-3">
    <label for="dataSelect" class="form-label">Data:</label>
    <select id="dataSelect" v-model="selectedData" class="form-control">
      <!--            <option value="BAFU">BAFU</option>-->
      <option value="BAFU_small">BAFU 1/2 Size</option>
      <option value="BAFU_tiny">BAFU 1/4 Size</option>
      <!--            <option value="cl2fullLarge">Chlorine</option>-->
      <option value="cl2fullLarge_half">Chlorine 1/2 Size</option>
      <option value="cl2fullLarge_quarter">Chlorine 1/4 Size</option>
      <!--            <option value="climate">Climate</option>-->
      <option value="climate_half">Climate 1/2 Size</option>
      <option value="climate_quarter">Climate 1/4 Size</option>
      <!--            <option value="meteo_total">Meteo</option>-->
      <option value="meteo_total_half">Meteo 1/2 Size</option>
      <option value="meteo_total_quarter">Meteo 1/4 Size</option>
    </select>
  </div>
</template>

<script lang="ts">
import {defineComponent} from 'vue';

export default defineComponent({
  name: 'DataSelect',
  props: {
    modelValue: {
      type: String,
      default: 'BAFU_tiny'
    }
  },
  computed: {
    selectedData: {
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
