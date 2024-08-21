<template>
  <div class="mb-n5" data-toggle="tooltip" data-placement="top"
       title="For faster results, consider selecting the 1/8 size dataset">
    <label for="seriesSelect" class="form-label">Series:</label>
    <br/>
    <span class="glyphicon glyphicon-info-sign info-icon" data-toggle="tooltip" data-placement="right"
          title="For faster results, consider selecting the 1/8 size dataset"></span>

    <div class="mb-3" data-toggle="tooltip" data-placement="top">
      <div class="custom-select">
        <select v-model="selectedSeries" id="seriesSelect" class="form-control me-5 pe-5">
          <option v-for="series in seriesNames" :key="series" :value="series">{{ series }}</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    seriesNames: {
      type: Array,
      required: true
    },
    value: {
      type: String,
      required: true
    }
  },
  computed: {
    selectedSeries: {
      get() {
        return this.value;
      },
      set(val) {
        this.$emit('input', val);
      }
    }
  }
}
</script>
