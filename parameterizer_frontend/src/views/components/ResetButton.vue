<template>
  <form ref="ref_reload" @submit.prevent="submitForm">
    <div class="justify-content-right" style="padding: 10px; position: absolute; z-index: 100; right: 0; top: 60px;">
      <button type="submit" class="btn align-center" style="background-color: #f0f0f0; padding: 10px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="1.5em" height="1.5em" viewBox="-2 0 24 24" style="margin-top: -2px; margin-right: 4px;">
          <path fill="currentColor" d="M2 12a9 9 0 0 0 9 9c2.39 0 4.68-.94 6.4-2.6l-1.5-1.5A6.706 6.706 0 0 1 11 19c-6.24 0-9.36-7.54-4.95-11.95C10.46 2.64 18 5.77 18 12h-3l4 4h.1l3.9-4h-3a9 9 0 0 0-18 0"/>
        </svg>
      </button>
    </div>
  </form>
</template>

<script>
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'ResetButton',
  methods: {
    submitForm() {
      // You can perform some additional form submission logic here if needed
      console.log('Form submitted');

      // Reload the page when the button is clicked
      location.reload();
    }
  }
});
</script>
