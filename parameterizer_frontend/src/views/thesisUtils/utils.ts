import { color } from "highcharts";

// Constants for clarity
const BASE_YEAR = 2010;
const BASE_MONTH = 1;
const BASE_DAY = 1;
const POINT_START = Date.UTC(2010, 1, 1);
const THIRTY_MINUTES = 1000 * 60 * 42;
const VISIBILITY_THRESHOLD = 10;

export const createSeries = (index: number, data: number[], datasetSelected: string = "BAFU_eighth", seriesName: string = 'Series', lineT = 'line', l_size = 2, s_color = "") => {

    const datasetCode = datasetSelected.split('_')[0].toLowerCase();


    let visible = 3;

    if (lineT == "display")
    {
       visible = 100;
       lineT = "line";
    }


    return {
        name: `${seriesName} ${seriesName === 'Series' ? index + 1 : ''}`.trim(),
        data,
        animation: false,
        marker: {
            enabled: false
        },
        pointStart: Date.UTC(BASE_YEAR, BASE_MONTH, BASE_DAY),
        pointInterval: THIRTY_MINUTES,
        visible: index < visible,  // This ensures only the first two series are visible
        tooltip: {
            valueDecimals: 2,
            fontSize:'20px'
        },
        plotOptions: {
            series: {
                showInNavigator: shouldShow(index, datasetCode),
            }
        },
        dashStyle: lineT,
        color : s_color,
        lineWidth: l_size
    };
};


const createSingleSeries = (data: number[], referenceData: number[]): (number | null)[] => {
    return data.map((value, index) => {
        const prevIsNull = referenceData[index - 1] === null;
        const currentIsNull = referenceData[index] === null;
        const nextIsNull = referenceData[index + 1] === null;

        if (prevIsNull || currentIsNull || nextIsNull) {
            return value;
        }

        return null;
    });
};


export const createSegmentedSeries = (index: number, data: number[], obfuscatedData: number[], groundtruthData: number[], chartOptions, datasetSelected: string = "BAFU_eighth", seriesName: string = 'Series') => {
    const datasetCode = datasetSelected.split('_')[0].toLowerCase();
    const imputedData = createSingleSeries(data, obfuscatedData);
    const mainSeriesId = `${seriesName}_${index}_main`;
    const imputedSeriesId = `${seriesName}_${index}_imputed`;
    const mainSeriesColor = chartOptions.colors[index % (chartOptions.colors.length)];
    const imputationSeriesColor = chartOptions.colors_imp[index % (chartOptions.colors_imp.length)];

    //const isVisible = shouldShow(index, datasetCode);
    const isShownInNavigator = shouldShow(index, datasetCode);
    const seriesNameGenerated = seriesName === 'Series' ? `${seriesName} ${index + 1}` : seriesName;

    const commonProperties = {
        marker: {
            enabled: false
        },
        pointStart: POINT_START,
        pointInterval: THIRTY_MINUTES,
        animation: false,
        findNearestPointBy: 'xy',
        opacity: 0.9,
        //visible: isVisible,
        tooltip: {
            valueDecimals: 2
        },
        navigator: {
            adaptToUpdatedData: false
        },
        plotOptions: {
            series: {
                showInNavigator: isShownInNavigator
            }
        },
        scrollbar: {
            liveRedraw: false
        }
    };

    const mainSeries = {
        id: `${index}_main`,
        name: processSeriesName(seriesName, index),
        data: groundtruthData,
        color: mainSeriesColor,
        lineWidth: 1.5,
        // zones: zones,
        ...commonProperties
    };

    const imputedSeries = {
        id: `${mainSeriesId}_imputed`,
        name: `(Imp.) ${seriesNameGenerated}`,
        data: imputedData,
        connectNulls: false,  // is false by default, added for ease of toggling
        color: imputationSeriesColor,
        lineWidth: 2.5,
        // dashStyle: 'Dot',
        ...commonProperties,
        marker: {
            enabled: true,
            symbol: determineSymbol(seriesName),
            radius: 3.5,
        },
    }
    return [imputedSeries];
};

export const generateChartOptions = (title, seriesName) => ({
    credits: {
        enabled: false
    },
    boost: {
        seriesThreshold: 1,
        useGPUTranslations: false,
        usePreAllocated: false
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
            text: '<span style="font-size: 20px; color: #666; font-weight: normal;"></span>',
            style: {
                fontStyle: 'italic'
            }
        },
        itemStyle: {
            fontSize: '20px',
            opacity: 1
        },
        itemHiddenStyle: {
            opacity: 0.5 // Set the opacity for hidden legends
        },
        verticalAlign: "top"
    },
    xAxis: {
        type: 'datetime'
    },
    colors: ["#7cb5ec", "#2b908f", "#a6c96a", "#876d5d", "#8f10ba", "#f7a35c", "#434348", "#f15c80", "#910000", "#8085e9", "#365e0c", "#90ed7d"],
    colors_imp: ["#5a89ba", "#20736b", "#839f57", "#6a4e49", "#730e9a", "#bf7d48","#343437", "#b84b68", "#720000", "#6167b0", "#293f08", "#71b15f"],
    chart: {
        height: 900,
        type: 'line',
        zoomType: 'x',
        panning: true,
        panKey: 'shift'
    },
    rangeSelector: {
        selected: 10,
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
    scrollbar: {
        liveRedraw: false
    },
    series: [{
        name: seriesName,
        data: Uint32Array.from({length: 10000}, () => Math.floor(Math.random() * 0)),
        animation: false,
        findNearestPointBy: 'xy',
        pointStart: Date.UTC(2010, 1, 1),
        pointInterval: 1000 * 60 * 42, // Granularity of 42 minutes
        tooltip: {
            valueDecimals: 2,
        },
    }]
});


export const generateChartOptionsLarge = (title, seriesName) => ({
    credits: {
        enabled: false
    },
    boost: {
        seriesThreshold: 1,
        useGPUTranslations: true,
        usePreAllocated: true
    },
    title: {
        text: title
    },
    navigator: {
        enabled: true,
        adaptToUpdateData: false,
        stickToMax: true
    },
    legend: {
        showCheckbox: true,
        title: {
            text: '<span style="font-size: 16px; color: #666; font-weight: normal;"></span>',
            style: {
                fontStyle: 'italic'
            }
        },
        itemStyle: {
            fontSize: '20px',
            opacity: 1
        },
        itemHiddenStyle: {
            fontStyle: 'italic',
            opacity: 0.5 // Set the opacity for hidden legends
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
    colors: ["#7cb5ec", "#2b908f", "#a6c96a", "#876d5d", "#8f10ba", "#f7a35c", "#434348", "#f15c80", "#910000", "#8085e9", "#365e0c", "#90ed7d"],
    colors_imp: ["#5a89ba", "#20736b", "#839f57", "#6a4e49", "#730e9a", "#bf7d48","#343437", "#b84b68", "#720000", "#6167b0", "#293f08", "#71b15f"],
    rangeSelector: {
        selected: 4,
        x: 0,
        style: {
            color: 'black',
            fontWeight: 'bold',
            position: 'relative',
            "font-family": "Arial"
        },
        enabled: true,
        inputEnabled: false,
        buttons: [
            { type: 'hour', count: 12, text: '12H' },
            { type: 'day', count: 3, text: '3D' },
            { type: 'day', count: 5, text: '5D' },
            { type: 'week', count: 1, text: 'W' },
            { type: 'month', count: 1, text: 'M' },
            { type: 'all', text: 'All', align: 'right', x: 900, y: 100}],
    },
    scrollbar: {
        liveRedraw: false
    },
    plotOptions: {
        series: {
            showInNavigator: true
        }
    },
    series: [{
        name: seriesName,
        data: Uint32Array.from({length: 10000}, () => Math.floor(Math.random() * 1)),
        animation: false,
        pointStart: Date.UTC(2010, 1, 1),
        findNearestPointBy: 'xy',
        pointInterval: 1000 * 60 * 42, // Granularity of 42 minutes
        tooltip: {
            valueDecimals: 2
        }
    }]
});

export const generateChartOptionsHeight = (title, seriesName) => ({
    credits: {
        enabled: false
    },
    boost: {
        seriesThreshold: 1,
        useGPUTranslations: true,
        usePreAllocated: true
    },
    title: {
        text: title
    },
    navigator: {
        enabled: true,
        adaptToUpdateData: false,
        stickToMax: true
    },
    legend: {
        showCheckbox: true,
        title: {
            text: '<span style="font-size: 16px; color: #666; font-weight: normal;"></span>',
            style: {
                fontStyle: 'italic'
            }
        },
        itemStyle: {
            fontSize: '20px',
            opacity: 1
        },
        itemHiddenStyle: {
            fontStyle: 'italic',
            opacity: 0.5 // Set the opacity for hidden legends
        },
        verticalAlign: "top"
    },
    xAxis: {
        type: 'datetime'
    },
    chart: {
        height: 620,
        type: 'line',
        zoomType: 'x',
        panning: true,
        panKey: 'shift'
    },
    colors: ["#7cb5ec", "#2b908f", "#a6c96a", "#876d5d", "#8f10ba", "#f7a35c", "#434348", "#f15c80", "#910000", "#8085e9", "#365e0c", "#90ed7d"],
    colors_imp: ["#5a89ba", "#20736b", "#839f57", "#6a4e49", "#730e9a", "#bf7d48","#343437", "#b84b68", "#720000", "#6167b0", "#293f08", "#71b15f"],
    rangeSelector: {
        selected: 10,
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
    scrollbar: {
        liveRedraw: false
    },
    plotOptions: {
        series: {
            showInNavigator: true,
            // zoneAxis: 'x',
        }
    },
    series: [{
        name: seriesName,
        data: Uint32Array.from({length: 10000}, () => Math.floor(Math.random() * 0)),
        animation: false,
        pointStart: Date.UTC(2010, 1, 1),
        findNearestPointBy: 'xy',
        pointInterval: 1000 * 60 * 42, // Granularity of 42 minutes
        tooltip: {
            valueDecimals: 2
        },

    }]
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

function shouldShow(idx: number, datasetName: string): boolean {
    if (datasetName === 'bafu') return idx === 0 || idx === 5;
    else if (datasetName === 'climate') return idx === 1 || idx === 8;
    else if (datasetName === 'chlorine') return idx === 2 || idx === 8;
    else if (datasetName === 'batch10') return idx === 3 || idx === 7; // drift
    else if (datasetName === 'meteo') return idx === 1 || idx === 3;
    else
        return idx === 1 || idx === 3;
}

function processSeriesName(seriesName: string, index: number): string {
    if (seriesName.startsWith('Series')) {
        return seriesName + ' ' + (index + 1);
    }

    // Check if seriesName is just a number
    if (!isNaN(Number(seriesName))) {
        return 'Series :' + seriesName.trim();
    }


    if (!seriesName.includes(':')) {
        return seriesName.trim();
    }


    // Remove everything before the first ":"
    const afterColon = seriesName.split(':').slice(1).join(':');

    // Check if seriesName is just a number
    if (!isNaN(Number(afterColon))) {
        return 'Series: ' + afterColon.trim();
    }

    // Trim whitespace from beginning and end
    return afterColon.trim();
}

const determineSymbol = (seriesName: string): string => {
    if (seriesName.includes('CDRec')) return 'circle';
    if (seriesName.includes('IIM')) return 'square';
    if (seriesName.includes('M-RNN')) return 'diamond';
    if (seriesName.includes('ST-MVL')) return 'triangle';
    return 'diamond';  // default value if none of the above
};
