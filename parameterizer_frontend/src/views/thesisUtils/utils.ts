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
    colors: [
        '#058DC7',  // Blue
        '#50B432',  // Green
        '#ED561B',  // Orange-Red
        '#DDDF00',  // Yellow
        '#24CBE5',  // Light Blue
        '#64E572',  // Light Green
        '#FF9655',  // Light Orange
        '#FFD700',  // Gold
        '#6AF9C4',  // Aqua
        '#FF69B4',  // Pink
        '#A020F0',  // Purple
        '#8B4513',  // Saddle Brown
        '#2E8B57',  // Sea Green
        '#D2691E',  // Chocolate
        '#B22222',  // Firebrick
        '#20B2AA',  // Light Sea Green
        '#8A2BE2',  // BlueViolet
        '#5F9EA0',  // CadetBlue
        '#FFF263',  // Pale Yellow
        '#7B68EE'   // MediumSlateBlue
    ],
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
    colors: [
        '#058DC7',  // Blue
        '#50B432',  // Green
        '#ED561B',  // Orange-Red
        '#DDDF00',  // Yellow
        '#24CBE5',  // Light Blue
        '#64E572',  // Light Green
        '#FF9655',  // Light Orange
        '#FFD700',  // Gold
        '#6AF9C4',  // Aqua
        '#FF69B4',  // Pink
        '#A020F0',  // Purple
        '#8B4513',  // Saddle Brown
        '#2E8B57',  // Sea Green
        '#D2691E',  // Chocolate
        '#B22222',  // Firebrick
        '#20B2AA',  // Light Sea Green
        '#8A2BE2',  // BlueViolet
        '#5F9EA0',  // CadetBlue
        '#FFF263',  // Pale Yellow
        '#7B68EE'   // MediumSlateBlue
    ],
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