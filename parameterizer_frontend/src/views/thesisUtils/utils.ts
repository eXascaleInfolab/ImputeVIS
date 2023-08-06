export const createSeries = (index: number, data: number[], seriesName: string = 'Series') => ({
    name: seriesName === 'Series' ? `${seriesName} ${index + 1}` : seriesName,
    data,
    lineWidth: 1.25,
    marker: {
        enabled: false
    },
    pointStart: Date.UTC(2010, 1, 1),
    pointInterval: 1000 * 60 * 30, // Granularity of 30 minutes
    // This will return false if index is even, and true if it's odd
    // If larger than 10, it will return true every 10th index
    visible: index < 10 ? index % 2 !==1 : index % 10 === 0,
    tooltip: {
        valueDecimals: 2
    },
    plotOptions: {
        series: {
            showInNavigator: index < 10 ? index % 2 !== 0 : index % 10 === 0,
        }
    }
});

const createSegments = (data: number[], referenceData: number[]) => {
    const segments = [];
    const DASHED_WIDTH = 2.5;
    const lineWidth = referenceData[0] === null ? DASHED_WIDTH : 1.25;

    for (let i = 0; i < data.length; i++) {
        if (referenceData[i] === null) {
            let j = i;
            const segmentData = new Array(data.length).fill(null);

            if (i > 0 && referenceData[i - 1] !== null) segmentData[i - 1] = data[i - 1];

            while (j < data.length && referenceData[j] === null) {
                segmentData[j] = data[j];
                j++;
            }

            if (j < data.length && referenceData[j] !== null) segmentData[j] = data[j];

            segments.push({
                data: segmentData,
                lineWidth: lineWidth,
            });

            i = j - 1;  // Jump to the end of the segment
        }
    }

    return segments;
};




// Utility function to segment your data based on the presence of null in the referenceData array
// const createSegments = (data: number[], referenceData: number[]) => {
//     const segments = [];
//     let currentWidth = referenceData[0] === null ? 2.5 : 1.25;
//     let currentDashStyle = referenceData[0] === null ? 'ShortDash' : 'Solid';
//
//     for (let i = 0; i < data.length; i++) {
//         // Start of a new segment
//         if ((referenceData[i] === null && currentWidth === 1.25) || (referenceData[i] !== null && currentWidth === 2.5)) {
//             const segmentData = Array(data.length).fill(null);
//             let j = i;
//
//             while (j < data.length && ((currentWidth === 2.5 && referenceData[j] === null) || (currentWidth === 1.25 && referenceData[j] !== null))) {
//                 segmentData[j] = data[j];
//                 j++;
//             }
//             i = j - 1;  // Update the loop counter to skip over the current segment
//
//             segments.push({
//                 data: segmentData,
//                 color: 'black',
//                 lineWidth: currentWidth,
//                 dashStyle: 'ShortDash'
//             });
//
//             // Set the next width
//             currentWidth = currentWidth === 1.25 ? 2.5 : 1.25;
//             currentDashStyle = currentDashStyle === 'Solid' ? 'ShortDash' : 'Solid';
//         }
//     }
//
//     return segments;
// };


export const createSegmentedSeries = (index: number, data: number[], referenceData: number[], chartOptions, seriesName: string = 'Series') => {
    const segments = createSegments(data, referenceData);
    const mainSeriesId = `${seriesName}_${index}_main`;
    const mainSeriesColor = chartOptions.colors[index % (chartOptions.colors.length)];
    const darkenedColor = darkenColor(mainSeriesColor, 0.55);

    const isVisible = index < 10 ? index % 2 !== 1 : index % 10 === 0;
    const isShownInNavigator = index < 10 ? index % 2 !== 0 : index % 10 === 0;
    const seriesNameGenerated = seriesName === 'Series' ? `${seriesName} ${index + 1}` : seriesName;

    const commonProperties = {
        marker: {
            enabled: false
        },
        pointStart: Date.UTC(2010, 1, 1),
        pointInterval: 1000 * 60 * 30,
        visible: isVisible,
        tooltip: {
            valueDecimals: 2
        },
        plotOptions: {
            series: {
                showInNavigator: isShownInNavigator
            }
        }
    };

    const mainSeries = {
        id: mainSeriesId,
        name: seriesNameGenerated,
        data: data,
        color: mainSeriesColor,
        lineWidth: 1.25,
        ...commonProperties
    };

    const linkedSeries = segments.map(segment => ({
        linkedTo: mainSeriesId,
        color: darkenedColor,
        name: seriesNameGenerated,
        data: segment.data,
        lineWidth: segment.lineWidth,
        ...commonProperties
    }));

    return [mainSeries, ...linkedSeries];
};

export const generateChartOptions = (title, seriesName) => ({
    credits: {
        enabled: false
    },
    title: {
        text: title
    },
    navigator: {
        enabled: true
    },
    legend: {
        showCheckbox: true,
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
        height: 700,
        type: 'line',
        zoomType: 'x',
        panning: true,
        panKey: 'shift'
    },
    rangeSelector: {
        selected: 1,
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
                type: 'hour',
                count: 12,
                text: '12H'
            },
            {
                type: 'day',
                count: 3,
                text: '3D'
            },

            {
                type: 'day',
                count: 5,
                text: '5D'
            },
            {
                type: 'week',
                count: 1,
                text: 'W'
            },
            {
                type: 'month',
                count: 1,
                text: 'M'
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
    navigator: {
        enabled: true
    },
    legend: {
        showCheckbox: true,
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
        height: 810,
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
        selected: 1,
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
                type: 'hour',
                count: 12,
                text: '12H'
            },
            {
                type: 'day',
                count: 3,
                text: '3D'
            },

            {
                type: 'day',
                count: 5,
                text: '5D'
            },
            {
                type: 'week',
                count: 1,
                text: 'W'
            },
            {
                type: 'month',
                count: 1,
                text: 'M'
            },

            {
                type: 'all',
                text: 'All',
                align: 'right',
                x: 900,
                y: 100,
            }],
    },
    plotOptions: {
        series: {
            showInNavigator: true
        }
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


function hexToRgb(hex: string): [number, number, number] {
    // Remove the hash at the start if it's there
    hex = hex.replace(/^#/, '');

    // Parse r, g, b values
    let bigint = parseInt(hex, 16);
    let r = (bigint >> 16) & 255;
    let g = (bigint >> 8) & 255;
    let b = bigint & 255;

    return [r, g, b];
}

function rgbToHex(r: number, g: number, b: number): string {
    return '#' + (1 << 24 | r << 16 | g << 8 | b).toString(16).slice(1).toUpperCase();
}

function lightenColor(color: string, percent: number): string {
    const [r, g, b] = hexToRgb(color);
    const t = percent < 0 ? 0 : 255;
    const p = percent < 0 ? percent * -1 : percent;
    return rgbToHex(Math.round((t - r) * p) + r, Math.round((t - g) * p) + g, Math.round((t - b) * p) + b);
}

function darkenColor(color: string, percent: number): string {
    return lightenColor(color, -1 * percent);
}