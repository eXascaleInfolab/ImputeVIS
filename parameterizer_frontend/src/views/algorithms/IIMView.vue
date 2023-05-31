<template>
  <div class="container">
    <h1 class="mb-4">I am IIM page.</h1>
    <form @submit.prevent="submitForm">
      <div class="mb-3">
        <label for="name" class="form-label">Name:</label>
        <input id="name" v-model="name" type="text" class="form-control" required>
      </div>

      <div class="mb-3">
        <label for="alg_code" class="form-label">Algorithm Code:</label>
        <input id="alg_code" v-model="alg_code" type="text" class="form-control" required>
      </div>

      <!--
      <div class="mb-3">
        <label for="filename_input" class="form-label">Input Filename:</label>
        <input id="filename_input" v-model="filename_input" type="text" class="form-control" required>
      </div>

      <div class="mb-3">
        <label for="filename_output" class="form-label">Output Filename:</label>
        <input id="filename_output" v-model="filename_output" type="text" class="form-control" required>
      </div>

      <div class="mb-3">
        <label for="runtime" class="form-label">Runtime:</label>
        <input id="runtime" v-model="runtime" type="number" class="form-control" required>
      </div>
      -->

      <button type="submit" class="btn btn-primary">Submit</button>
    </form>

    <h2> RMSE: {{rmse}}</h2>
  </div>
</template>

<script lang="ts">
import { ref } from 'vue';
import axios from 'axios';

export default {
  setup() {
    const name = ref('');
    const alg_code = ref('');
    const filename_input = ref('');
    const filename_output = ref('');
    const runtime = ref(0);
    const rmse = ref(null);

    const submitForm = async () => {
      try {
        const response = await axios.post('http://localhost:8000/api/submit-name/',
          {
            name: name.value,
            alg_code: alg_code.value,
            filename_input: filename_input.value,
            filename_output: filename_output.value,
            runtime: runtime.value
          },
          {
            headers: {
              'Content-Type': 'application/json',
            }
          }
        );
        rmse.value = response.data.rmse;
        console.log(response.data);
      } catch (error) {
        console.error(error);
      }
    }


    return {
      name,
      alg_code,
      filename_input,
      filename_output,
      runtime,
      submitForm,
      rmse
    }
  }
}
</script>