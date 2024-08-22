<template>
  <div>
    <div class="mb-3">
      <label for="optimizationSelect" class="form-label" style="font-weight: bold;">Optimization</label> <br/>
      <div class="custom-select" >
        <select id="optimizationSelect" v-model="selectedOptimization" class="form-control me-3" >
          <option value="bayesianOptimization">Bayesian Optimization</option>
          <option value="particleSwarmOptimization">Particle Swarm Optimization</option>
          <option value="successiveHalving">Successive Halving</option>
        </select>
      </div>
    </div>

    <h3 v-if="naterq_error" style="color : red; margin-left : 20%" >The current algorithm does not match with the current optimization, no feature available...</h3>


    <!-- Bayesian Optimization parameters -->
    <div v-if="selectedOptimization === 'bayesianOptimization' && !natehidden">
      <div class="mb-3">
        <label for="nCalls" class="form-label">Number of Calls: {{ nCalls }}</label>
        <input id="nCalls" v-model.number="nCalls" type="range" min="1" max="10" step="1" class="form-control">
      </div>
      <div class="mb-3">
        <label for="nRandomStarts" class="form-label">Random Starts: {{ nRandomStarts }}</label>
        <input id="nRandomStarts" v-model.number="nRandomStarts" type="range" min="1" max="2" step="1"
               class="form-control">
      </div>
      <div class="mb-3">
        <label for="acqFunc" class="form-label">Acquisition Function:</label> <br/>
        <div class="custom-select">
          <select id="acqFunc" v-model="acqFunc" class="form-control me-5">
            <option value="gp_hedge">gp_hedge</option>
            <option value="EI">EI</option>
            <option value="LCB">LCB</option>
            <option value="PI">PI</option>
           <!-- <option value="EIps">EIps</option>
            <option value="PIps">PIps</option>-->
          </select>
        </div>
      </div>
    </div>

    <!-- PSO parameters -->
    <div v-if="selectedOptimization === 'particleSwarmOptimization' && !natehidden">
      <div class="mb-3">
        <label for="c1" class="form-label">Cognitive Parameter: {{ c1 }}</label>
        <input id="c1" v-model.number="c1" type="range" min="0.1" max="1" step="0.1" class="form-control">
      </div>
      <div class="mb-3">
        <label for="c2" class="form-label">Social Parameter: {{ c2 }}</label>
        <input id="c2" v-model.number="c2" type="range" min="0.1" max="1" step="0.1" class="form-control">
      </div>
      <div class="mb-3">
        <label for="w" class="form-label">Inertia Weight: {{ w }}</label>
        <input id="w" v-model.number="w" type="range" min="0.1" max="1" step="0.1" class="form-control">
      </div>
      <div class="mb-3" data-toggle="tooltip" data-placement="top" title="Also impacts run-time proportionally.">
        <label for="nParticles" class="form-label">Particles: {{ nParticles }}</label>
        <input id="nParticles" v-model.number="nParticles" type="range" min="1" max="100" step="1" class="form-control">
      </div>
      <div class="mb-3" data-toggle="tooltip" data-placement="top" title="Also impacts run-time proportionally.">
        <label for="iterations" class="form-label">Iterations: {{ iterations }}</label>
        <input id="iterations" v-model.number="iterations" type="range" min="1" max="100" step="1" class="form-control">
      </div>
    </div>

    <!-- Successive Halving parameters -->
    <div v-if="selectedOptimization === 'successiveHalving' && !natehidden">
      <div class="mb-3">
        <label for="numConfigs" class="form-label">Configurations: {{ numConfigs }}</label>
        <input id="numConfigs" v-model.number="numConfigs" type="range" min="1" max="100" step="1" class="form-control">
      </div>
      <div class="mb-3" data-toggle="tooltip" data-placement="top" title="Also impacts run-time proportionally.">
        <label for="numIterations" class="form-label">Iterations: {{ numIterations }}</label>
        <input id="numIterations" v-model.number="numIterations" type="range" min="1" max="100" step="1"
               class="form-control">
      </div>
      <div class="mb-3">
        <label for="reductionFactor" class="form-label">Reduction Factor: {{ reductionFactor }}</label>
        <input id="reductionFactor" v-model.number="reductionFactor" type="range" min="2" max="20" step="1"
               class="form-control">
      </div>
    </div>

    <!-- Metrics parameters -->
    <div class="mb-3"  v-if="!natehidden">
      <label for="metricsSelect" class="form-label">Metrics:</label>
      <select id="metricsSelect" v-model="selectedMetrics" class="form-control pb-4" multiple>
        <option value="rmse">RMSE</option>
        <option value="mae">MAE</option>
        <option value="mse">MSE</option>
        <option value="mi">NMI</option>
        <option value="corr">CORR</option>
      </select>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, defineComponent, computed, watch, PropType} from 'vue';

export default defineComponent({
  name: 'OptimizationSelect',
  props: {
    natehidden: {
      type: Boolean,
      required: true
      },
    },
    setup(props, {emit}) {
    const selectedOptimization = ref('bayesianOptimization');
    const selectedMetrics = ref(['rmse']);

    // Bayesian Optimization parameters
    const nCalls = ref(2);
    const nRandomStarts = ref(2);
    const acqFunc = ref('gp_hedge');

    // PSO parameters
    const c1 = ref(0.5);
    const c2 = ref(0.5);
    const w = ref(0.8);
    const nParticles = ref(10);
    const iterations = ref(3);

    // Successive Halving parameters
    const numConfigs = ref(5);
    const numIterations = ref(3);
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
    }, {immediate: true});

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
