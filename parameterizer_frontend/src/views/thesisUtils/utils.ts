export const createSeries = (index: number, data: number[], seriesName: string = 'Series') => ({
  name: `${seriesName} ${index + 1}`,
  data,
  pointStart: Date.UTC(2010, 1, 1),
  pointInterval: 1000 * 60 * 30, // Granularity of 30 minutes
  // visible: true,
  tooltip: {
    valueDecimals: 2
  }
});

export const generateChartOptions = (title, seriesName) => ({
      credits: {
        enabled: false
      },
      title: {
        text: title
      },
      legend: {
        title: {
          text: '<span style="font-size: 11px; color: #666; font-weight: normal;">(Click on series to hide)</span>',
          style: {
            fontStyle: 'italic'
          }
        },
        verticalAlign: "top"
      },
      xAxis: {
        type: 'datetime'
      },
      chart: {
        type: 'line',
        zoomType: 'x',
        panning: true,
        panKey: 'shift'
      },
      rangeSelector: {
        x: 0,
        // floating: true,
        style: {
          color: 'black',
          fontWeight: 'bold',
          position: 'relative',
          "font-family": "Arial"
        },
        enabled: true,
        inputEnabled: false,
        // inputDateFormat: '%y',
        // inputEditDateFormat: '%y',
        buttons: [{
          type: 'hour',
          count: 1,
          text: 'H'
        },
          {
            type: 'day',
            count: 1,
            text: 'D'
          },

          {
            type: 'month',
            count: 1,
            text: 'M'
          },
          {
            type: 'year',
            count: 1,
            text: 'Y'
          },

          {
            type: 'all',
            text: 'All',
            align: 'right',
            x: 1000,
            y: 100,
          }],
      },
      series: [{
        name: seriesName,
        data: Uint32Array.from({length: 10000}, () => Math.floor(Math.random() * 0)),
        pointStart: Date.UTC(2010, 1, 1),
        pointInterval: 1000 * 60 * 30, // Granularity of 30 minutes
        tooltip: {
          valueDecimals: 2
        }
      }],
      // plotOptions: {
      //   series: {
      //     pointStart: Date.UTC(2010, 0, 1),
      //     pointInterval: 100000 * 1000 // one day
      //   }
      // },
    });

export const generateChartOptionsLarge = (title, seriesName) => ({
  credits: {
    enabled: false
  },
  title: {
    text: title
  },
  legend: {
    title: {
      text: '<span style="font-size: 11px; color: #666; font-weight: normal;">(Click on series to hide)</span>',
      style: {
        fontStyle: 'italic'
      }
    },
    verticalAlign: "top"
  },
  xAxis: {
    type: 'datetime'
  },
  chart: {
    height: 900,
    type: 'line',
    zoomType: 'x',
    panning: true,
    panKey: 'shift'
  },
  rangeSelector: {
    x: 0,
    // floating: true,
    style: {
      color: 'black',
      fontWeight: 'bold',
      position: 'relative',
      "font-family": "Arial"
    },
    enabled: true,
    inputEnabled: false,
    // inputDateFormat: '%y',
    // inputEditDateFormat: '%y',
    buttons: [
      {
        type: 'day',
        count: 1,
        text: 'D'
      },

      {
        type: 'month',
        count: 1,
        text: 'M'
      },
      {
        type: 'year',
        count: 1,
        text: 'Y'
      },

      {
        type: 'all',
        text: 'All',
        align: 'right',
        x: 1000,
        y: 100,
      }],
  },
  series: [{
    name: seriesName,
    data: Uint32Array.from({length: 10000}, () => Math.floor(Math.random() * 0)),
    pointStart: Date.UTC(2010, 1, 1),
    pointInterval: 1000 * 60 * 30, // Granularity of 30 minutes
    tooltip: {
      valueDecimals: 2
    }
  }],
});