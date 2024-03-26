<template xmlns="http://www.w3.org/1999/html">
  <main class="home">
    <h3 class="mb-4 text-center">ImputeVIS</h3>
    <p class="text-center">
      ImputeVis is an online tool that allows visualization, parameterization, and optimization of time series
      imputation algorithms.
      <br/>
      This tool was created at the <a href="http://exascale.info/" target="_blank">eXascale Infolab</a>, a research group
      at the <a href="http://www.unifr.ch/" target="_blank">University of Fribourg</a>, Switzerland.
    </p>
    <p class="ml-5 text-center">
      This is a master thesis project by Brian Schweigler, supervised by Dr. Mourad Khayati, Prof. Philippe
      Cudré-Mauroux, and Zakhar Tymchenko.
      <!--      Done at the University of Fribourg, Switzerland at the eXascale Institue.-->
      <!--      ImputeVIS is a built on a Vue front-end and a Django back-end.-->
    </p>
    <h4 class="text-center"><strong>Features</strong></h4>
    <br/>

    <div class="row justify-content-center">

      <!-- First Column for Compare -->
      <div class="col-md-3">
        <p><b>Datasets:</b></p>
        <ul>
          <li>
            <RouterLink to="/display">Display</RouterLink>
          </li>
          <li>
            <RouterLink to="/feature_extraction">Feature Extraction</RouterLink>
          </li>
          <li>
            <RouterLink to="/contamination">Contamination</RouterLink>
          </li>
        </ul>
      </div>

      <!-- Second Column for Algorithms -->
      <div class="col-md-3">
        <p><b>Optimization:</b></p>
        <ul>
          <li>
            <RouterLink to="/user_optimizer">User-Defined</RouterLink>
          </li>
          <li>
            <RouterLink to="/auto_optimizer">Auto-ML</RouterLink>
          </li>
        </ul>
      </div>

      <!-- Third Column for Algorithm Optimization -->
      <div class="col-md-3">
        <p><b>Imputation:</b></p>
        <ul>
          <li>
            <RouterLink to="/imputation">Imputation Management</RouterLink>
          </li>
          <li>
            <RouterLink to="/explainer">Explainer (SHAP)</RouterLink>
          </li>

        </ul>
      </div>

    </div>


    <p>
      Its primary features empower users to:
      <ul>
        <li>Conduct a comprehensive comparison between CDRec, IIM, M-RNN, and ST-MVL based on imputation metrics such as
          RMSE, MAE, MI, and correlation.<br>
          Within this context, users are endowed with the capability to:
          <ul>
            <li>
              Opt between various configurations:
              those recommended by the thesis author, default parameters delineated in the
              original algorithm papers, or parameters optimized through techniques like Bayesian Optimization, Particle
              Swarm Optimization, or Successive Halving.
            </li>
            <li>
              Obtain metrics including RMSE, MAE, MI, and CORR of the chosen configuration.

            </li>
            <li>
              Visualize the resulting imputations for each algorithm, dependant on the data set.

            </li>
          </ul>

        </li>
        <li>
          Fine-tune individual algorithm parameters for imputation tasks on predefined datasets, during which they can
          access the aforementioned metrics and visualization.
        </li>
        <li>
          Employ distinct optimization strategies, such as Bayesian Optimization, Particle Swarm Optimization, or
          Successive Halving, to pinpoint optimal parameters for a dataset and derive the associated metrics and visual
          insights.
        </li>
        <li>
          Scrutinize the characteristics of individual data sets using the Catch-22 methodology.

        </li>
      </ul>
    </p>

  </main>

</template>

<script lang="ts">
import {defineComponent} from "vue";
import {RouterLink} from "vue-router";

export default defineComponent({
  components: {RouterLink}
})
</script>
<style scoped>
.home {
  margin-left: 35px; /* Change this value to increase or decrease the margin */
}
</style>

