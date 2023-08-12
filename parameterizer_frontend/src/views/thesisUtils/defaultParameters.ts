// algorithmsDefaults.ts

// IIM
export interface IIMDefaults {
    learningNeighbors: number;
}

export const IIM_DEFAULTS: IIMDefaults = {
    learningNeighbors: 10,
};

// CDREC
export interface CDRecDefaults {
    reductionValue: string;
    epsilon: number;
    iterations: number;
}

export const CDREC_DEFAULTS: CDRecDefaults = {
    reductionValue: "0",
    epsilon: 1E-6,
    iterations: 100,
};

// M-RNN
export interface MRNNDefaults {
    hiddenDim: number;
    learningRate: number;
    keepProb: number;
    iterations: number;
}

export const MRNN_DEFAULTS: MRNNDefaults = {
    hiddenDim: 10,
    learningRate: 0.01,
    keepProb: 1.0,
    iterations: 1000,
};

// ST-MVL
export interface STMVLDefaults {
    windowSize: number;
    gamma: number;
    alpha: number;
}

export const STMVL_DEFAULTS: STMVLDefaults = {
    windowSize: 2.0,
    gamma: 0.85,
    alpha: 7,
};
