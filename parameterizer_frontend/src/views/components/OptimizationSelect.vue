<template>
  <div>
    <div class="mb-3">
      <label for="optimizationSelect" class="form-label">Optimization:</label>
      <select id="optimizationSelect" v-model="selectedOptimization" class="form-control">
        <option value="bayesianOptimization">Bayesian Optimization</option>
        <option value="particleSwarmOptimization">Particle Swarm Optimization</option>
        <option value="successiveHalving">Successive Halving</option>
      </select>
    </div>

    <!-- Bayesian Optimization parameters -->
    <div v-if="selectedOptimization === 'bayesianOptimization'">
      <div class="mb-3">
        <label for="nCalls" class="form-label">Number of Calls:</label>
        <input id="nCalls" v-model="nCalls" class="form-control" type="number">
      </div>
      <div class="mb-3">
<!--        <label for="nRandomStarts" class="form-label">Number of Random Starts:</label>-->
<!--        <input id="nRandomStarts" v-model="nRandomStarts" class="form-control" type="number">-->
<!--        <option v-for="number in Array.from({ length: 100 }, (_, i) => i + 1)" :key="number">{{ number }}</option>-->
<!--        <select id="nRandomStarts" v-model="nRandomStarts" class="form-control">-->
<!--            <option v-for="number in Array.from({ length: 100 }, (_, i) => i + 1)" :key="number">{{ number }}</option>-->
<!--        </select>-->
        <label for="nRandomStarts" class="form-label">Number of Random Starts: {{ nRandomStarts }}</label>
          <input id="nRandomStarts" v-model.number="nRandomStarts" type="range" min="0" max="50" step="1" class="form-control">
      </div>
      <div class="mb-3">
        <label for="acqFunc" class="form-label">Acquisition Function:</label>
        <input id="acqFunc" v-model="acqFunc" class="form-control" type="text">
      </div>
    </div>

    <!-- PSO parameters -->
    <div v-if="selectedOptimization === 'particleSwarmOptimization'">
      <div class="mb-3">
        <label for="c1" class="form-label">Cognitive Parameter:</label>
        <input id="c1" v-model="c1" class="form-control" type="number" step="0.1">
      </div>
      <div class="mb-3">
        <label for="c2" class="form-label">Social Parameter:</label>
        <input id="c2" v-model="c2" class="form-control" type="number" step="0.1">
      </div>
      <div class="mb-3">
        <label for="w" class="form-label">Inertia Weight:</label>
        <input id="w" v-model="w" class="form-control" type="number" step="0.1">
      </div>
      <div class="mb-3">
        <label for="nParticles" class="form-label">Number of Particles:</label>
        <input id="nParticles" v-model="nParticles" class="form-control" type="number">
      </div>
      <div class="mb-3">
        <label for="iterations" class="form-label">Number of Iterations:</label>
        <input id="iterations" v-model="iterations" class="form-control" type="number">
      </div>
    </div>

    <!-- Successive Halving parameters -->
    <div v-if="selectedOptimization === 'successiveHalving'">
      <div class="mb-3">
        <label for="numConfigs" class="form-label">Number of Configurations:</label>
        <input id="numConfigs" v-model="numConfigs" class="form-control" type="number">
      </div>
      <div class="mb-3">
        <label for="numIterations" class="form-label">Number of Iterations:</label>
        <input id="numIterations" v-model="numIterations" class="form-control" type="number">
      </div>
      <div class="mb-3">
        <label for="reductionFactor" class="form-label">Reduction Factor:</label>
        <input id="reductionFactor" v-model="reductionFactor" class="form-control" type="number">
      </div>
    </div>

    <!-- Metrics parameters -->
    <div class="mb-3">
      <label for="metricsSelect" class="form-label">Metrics:</label>
      <select id="metricsSelect" v-model="selectedMetrics" class="form-control" multiple>
        <option value="rmse">Root Mean Square Error (RMSE)</option>
        <option value="mse">Mean Square Error (MSE)</option>
        <option value="mi">Mutual Information (MI)</option>
        <option value="corr">Correlation (CORR)</option>
      </select>
    </div>
  </div>
</template>

<script lang="ts">
import { ref, defineComponent, computed, watch } from 'vue';

export default defineComponent({
  name: 'OptimizationSelect',
  setup(props, { emit }) {
    const selectedOptimization = ref('bayesianOptimization');
    const selectedMetrics = ref([]);

    // Bayesian Optimization parameters
    const nCalls = ref(50);
    const nRandomStarts = ref(0);
    const acqFunc = ref('gp_hedge');

    // PSO parameters
    const c1 = ref(0.5);
    const c2 = ref(0.3);
    const w = ref(0.9);
    const nParticles = ref(20);
    const iterations = ref(10);

    // Successive Halving parameters
    const numConfigs = ref(10);
    const numIterations = ref(5);
    const reductionFactor = ref(2);

    // Combine all parameters into one object
    const optimizationParams = computed(() => {
      return {
        optimization: selectedOptimization.value,
        metrics: selectedMetrics.value,
        n_calls: nCalls.value,
        n_random_starts: nRandomStarts.value,
        acq_func: acqFunc.value,
        c1: c1.value,
        c2: c2.value,
        w: w.value,
        n_particles: nParticles.value,
        iterations: iterations.value,
        num_configs: numConfigs.value,
        num_iterations: numIterations.value,
        reduction_factor: reductionFactor.value
      };
    });

    // Emit the custom event whenever the parameters change
    watch(optimizationParams, (newValue) => {
      emit('parametersChanged', newValue);
    });

    return {
      selectedOptimization,
      selectedMetrics,
      nCalls,
      nRandomStarts,
      acqFunc,
      c1,
      c2,
      w,
      nParticles,
      iterations,
      numConfigs,
      numIterations,
      reductionFactor
    };
  }
});
</script>
