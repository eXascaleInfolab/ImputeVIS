<template>
  <div>
    I am IIM page.
    <form @submit.prevent="submitForm">
      <label for="name">Name:</label>
      <input id="name" v-model="name" type="text" required> <br>

      <label for="alg_code">Algorithm Code:</label>
      <input id="alg_code" v-model="alg_code" type="text" required> <br>

<!--      <label for="filename_input">Input Filename:</label>-->
<!--      <input id="filename_input" v-model="filename_input" type="text" required> <br>-->

<!--      <label for="filename_output">Output Filename:</label>-->
<!--      <input id="filename_output" v-model="filename_output" type="text" required> <br>-->

<!--      <label for="runtime">Runtime:</label>-->
<!--      <input id="runtime" v-model="runtime" type="number" required> <br>-->

      <button type="submit">Submit</button>
    </form>
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
      submitForm
    }
  }
}
</script>