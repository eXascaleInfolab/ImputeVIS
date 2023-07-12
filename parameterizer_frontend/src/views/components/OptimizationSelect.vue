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
        <label for="nCalls" class="form-label">Number of Calls: {{nCalls}}</label>
        <input id="nCalls" v-model.number="nCalls" type="range" min="1" max="100" step="1" class="form-control">
      </div>
      <div class="mb-3">
        <label for="nRandomStarts" class="form-label">Number of Random Starts: {{ nRandomStarts }}</label>
        <input id="nRandomStarts" v-model.number="nRandomStarts" type="range" min="1" max="100" step="1" class="form-control">
      </div>
      <div class="mb-3">
        <label for="acqFunc" class="form-label">Acquisition Function:</label>
        <input id="acqFunc" v-model="acqFunc" class="form-control" type="text">
      </div>
    </div>

    <!-- PSO parameters -->
    <div v-if="selectedOptimization === 'particleSwarmOptimization'">
      <div class="mb-3">
        <label for="c1" class="form-label">Cognitive Parameter: {{c1}}</label>
        <input id="c1" v-model.number="c1" type="range" min="0.1" max="1" step="0.1" class="form-control">
      </div>
      <div class="mb-3">
        <label for="c2" class="form-label">Social Parameter: {{c2}}</label>
        <input id="c2" v-model.number="c2" type="range" min="0.1" max="1" step="0.1" class="form-control">
      </div>
      <div class="mb-3">
        <label for="w" class="form-label">Inertia Weight: {{w}}</label>
        <input id="w" v-model.number="w" type="range" min="0.1" max="1" step="0.1" class="form-control">
      </div>
      <div class="mb-3">
        <label for="nParticles" class="form-label">Number of Particles: {{nParticles}}</label>
        <input id="nParticles" v-model.number="nParticles" type="range" min="1" max="100" step="1" class="form-control">
      </div>
      <div class="mb-3">
        <label for="iterations" class="form-label">Number of Iterations: {{iterations}}</label>
        <input id="iterations" v-model.number="iterations" type="range" min="1" max="100" step="1" class="form-control">
      </div>
    </div>

    <!-- Successive Halving parameters -->
    <div v-if="selectedOptimization === 'successiveHalving'">
      <div class="mb-3">
        <label for="numConfigs" class="form-label">Number of Configurations: {{numConfigs}}</label>
        <input id="numConfigs" v-model.number="numConfigs" type="range" min="1" max="100" step="1" class="form-control">
      </div>
      <div class="mb-3">
        <label for="numIterations" class="form-label">Number of Iterations: {{numIterations}}</label>
        <input id="numIterations" v-model.number="numIterations" type="range" min="1" max="100" step="1" class="form-control">
      </div>
      <div class="mb-3">
        <label for="reductionFactor" class="form-label">Reduction Factor: {{reductionFactor}}</label>
        <input id="reductionFactor" v-model.number="reductionFactor" type="range" min="2" max="20" step="1" class="form-control">
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
    const selectedMetrics = ref(['rmse']);

    // Bayesian Optimization parameters
    const nCalls = ref(10);
    const nRandomStarts = ref(1);
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
    }, { immediate: true });

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
