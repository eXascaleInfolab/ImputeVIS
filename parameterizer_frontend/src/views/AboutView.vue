<template>
  <div class="about">
    <br>
    <p class="ml-5">
      This is a master thesis project by Brian Schweigler, supervised by Mourad Khayati and Zakhar Tymchenko.
      Done at the University of Fribourg, Switzerland in the eXascale Institue.

      ImputeVIS is a built on a Vue front-end and a Django back-end.
    </p>
    Its primary features empower users to:
    <ul>
      <li>Conduct a comprehensive comparison between CDRec, IIM, M-RNN, and ST-MVL based on imputation metrics such as
        RMSE, MAE, MI, and correlation.<br>
        Within this context, users are endowed with the capability to:
        <ul>
          <li>
            Opt between various configurations: <br>
            those recommended by the thesis author, default parameters delineated in             the
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
  </div>
</template>

<style scoped>
.about {
  margin-left: 35px; /* Change this value to increase or decrease the margin */
}
</style>