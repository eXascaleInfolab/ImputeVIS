<template>

  I am IIM page.
  <div>
    <form @submit.prevent="submitForm">
      <label for="name">Name:</label>
      <input id="name" v-model="name" type="text" required>
      <button type="submit">Submit</button>
    </form>
  </div>
</template>

<script lang="ts">
import {ref} from 'vue';
import axios from 'axios';

export default {
  setup() {
    const name = ref('');

    const submitForm = async () => {
      try {
        const response = await axios.post('http://localhost:8000/api/submit-name/',
            {name: name.value},
            {
              headers: {
                'Content-Type': 'application/json',
              }
            });
        console.log(response.data);
      } catch (error) {
        console.error(error);
      }
    }

    return {
      name,
      submitForm
    }
  }
}
</script>