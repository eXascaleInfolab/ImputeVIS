<template>
  <div class="about">
    <br>
    <div class="row">
      <div class="col-md-12">
        <div class="page-header">
          <h1>
            <small>About the tool</small>
          </h1>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        <p><b>Technology</b><br>
          ImputeVIS is a client-server application.
          The client-side is implemented using <a href="https://vuejs.org/">Vue</a> with TypeScript,
          supplemented with <a href="https://www.highcharts.com/">HighCharts</a> (a JavaScript library for charts) and
          HTML/CSS.
          <br/>
          The server-side uses <a href="https://www.djangoproject.com/">Django</a>, with additional Python scripts for processing requests.
        </p>
        <p><b>Contact</b><br>
          <a href="https://exascale.info/members/mourad-khayati/">Dr. Mourad Khayati</a>
        </p>
        <p><b>Contributors</b><br></p>
        <ul>
          <li><a href="https://www.linkedin.com/in/brian-schweigler/">Brian Schweigler</a></li>
          <li><a href="https://exascale.info/members/zakhar-tymchenko/">Zakhar Tymchenko</a></li>
        </ul>
        <p></p>
        <p><b>Teams</b><br></p>
        <div class="col-md-4">
          <div>
            <a href="https://exascale.info/"><img style="width: 60%;height: auto;" src="public/Xi_logo.svg"></a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.about {
  margin-left: 35px; /* Change this value to increase or decrease the margin */
}
</style>