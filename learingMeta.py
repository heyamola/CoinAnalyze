from learningHelper import *
from copy import deepcopy
import numpy as np
import pandas as pd
import indicators
import timeit
import labelCreator

RAW = True
CHANGE = True
PRICES = CLOSE[0]

'''
    Normalize 
        if 0 not normalize
        elif -1 then (val - min(val)) / (max(val) - min(val))
        else: val / normalize
'''
META = {
    "raw_columns": [
        # {
        #     "column": OPEN,     # (col_no, col_name)
        #     "name": OPEN[1]
        #     "raw": True,
        #     "change": True,
        #     "normalize_raw": -1,
        #     "normalize_change": -1,
        # }
    ],
    "indicators": [
        #
        # {
        #     "func": "sma",
        #     "raw": True,
        #     "change": True,
        #     "prices": [OPEN[0]],
        #     "kwargs": {"period": 20},
        #     "normalize_raw": -1,
        #     "normalize_change": -1,
        # }
    ],
    "label":
        {
            "func": "createLabelConstantIncrease",
            "column": CLOSE[0],
            "kwargs": {"step": 30, "class_points": [0.004]}
        }
}


def prepareMeta():
    meta = deepcopy(META)
    features = [OPEN, HIGH, LOW, CLOSE, VOLUME, NUMBER_OF_TRADE]
    for feature in features:
        d = {"column": feature, "name": feature[1],
             "raw": RAW, "change": CHANGE, "normalize_raw": -1}
        meta["raw_columns"].append(d)

    periods = [10, 20, 40, 80, 160]
    funcnames = ["sma", "wma", "ema", ]
    for func_name in funcnames:
        for period in periods:
            name = "%s_%s" % (func_name, period,)
            d = {"func": func_name, "raw": RAW, "change": CHANGE, "name": name,
                 "prices": [PRICES], "kwargs": {"period": period},
                 "normalize_raw": -1, "normalize_change": -1}
            meta["indicators"].append(d)

    periods = [7, 14, 28, 58, 106]
    for period in periods:
        name = "rsi_%s" % (period,)
        d = {"func": "rsi", "raw": RAW, "change": CHANGE, "name": name,
             "prices": [PRICES], "kwargs": {"period": period},
             "normalize_raw": -1, "normalize_change": -1}
        meta["indicators"].append(d)

    args = [(20, 2.), (40, 2.), (80, 2.)]
    for period, num_std_dev in args[0:1]:
        name = "bb_%s_%s" % (period, num_std_dev)
        d = {"func": "bb", "raw": RAW, "change": CHANGE, "name": ["%s_upper" % name, "%s_lower" % name, "%s_B" % name],
             "prices": [PRICES], "kwargs": {"period": period, "num_std_dev": num_std_dev},
             "normalize_raw": -1, "normalize_change": -1}
        meta["indicators"].append(d)

    args = [(14, 3), (14, 5), (28, 3), (28, 5), (56, 3), (56, 5)]
    for k_period, d_period in args:
        name = "stochastic_%s_%s" % (k_period, d_period)
        d = {"func": "stochastic", "name": ["%s_K" % name, "%s_D" % name],
             "raw": RAW, "change": CHANGE,
             "prices": [OPEN[0], HIGH[0], LOW[0], CLOSE[0]], "kwargs": {"d_period": d_period, "k_period": k_period},
             "normalize_raw": 0, "normalize_change": 0}
        meta["indicators"].append(d)

    return meta


def getNormalizeInfoFromMeta(meta):
    retVal = []
    combinedList = []
    combinedList += meta["raw_columns"]
    combinedList += meta["indicators"]

    for item in combinedList:
        if item["raw"]:
            retVal.append(item["normalize_raw"])
        if item["change"]:
            retVal.append(item["normalize_change"])
    return retVal


def _indicatorAppend(dataset, df, trim_indexes, indi_info):
    '''
        appends new columns to dataframe according to given indicator info
        {
            "func": "sma",
            "name": "sma_20",
            "raw": True,
            "change": True,
            "prices": [OPEN[0]],
            "kwargs": {"period": 20},
            "normalize_raw": -1,
            "normalize_change": -1,
        }
    '''
    name = indi_info["name"]
    func_name = indi_info["func"]
    indicator_data = dataset[:, indi_info["prices"]]
    kwargs = indi_info["kwargs"]

    func = getattr(indicators, func_name)
    v, begin, end = func(indicator_data, **kwargs)
    if indi_info["raw"]:
        trim_indexes.append((begin, end))
        if type(name) == list:
            for i, n in enumerate(name):
                df[n] = v[:, i].reshape(v.shape[0])
        else:
            df[name] = v
    if indi_info["change"]:
        if type(name) == list:
            for i, n in enumerate(name):
                v_perc, begin_perc, end_perc = calculatePercentageChange(v[:, i].reshape(v.shape[0]))
                trim_indexes.append((begin + begin_perc, end + end_perc))
                df["%s_perc" % n] = v_perc
        else:
            v_perc, begin_perc, end_perc = calculatePercentageChange(v)
            trim_indexes.append((begin + begin_perc, end + end_perc))
            df["%s_perc" % name] = v_perc


def _rawAppend(dataset, df, trim_indexes, raw_info):
    '''
        appends new columns to dataframe according to given raw_column info
        {
            "column": OPEN,
            "name": OPEN[1]
            "raw": True,
            "change": True,
            "normalize_raw": -1,
            "normalize_change": -1,
        }
    '''
    col, col_name = raw_info["column"]
    col_vector = dataset[:, col]
    if raw_info["raw"]:
        df[col_name] = col_vector
    if raw_info["change"]:
        perc_name = "%s_perc" % col_name
        v, begin, end = calculatePercentageChange(col_vector)
        trim_indexes.append((begin, end))
        df[perc_name] = v


def _createLabel(dataset, df, trim_indexes, label_info):
    '''
        {
            "func": "createLabelConstantIncrease",
            "column": CLOSE[0],
            "kwargs": {"step": 30, "class_points": [-0.005, 0.005]}
        }
    '''
    func_name = label_info["func"]
    col = label_info["column"]
    kwargs = label_info["kwargs"]

    func = getattr(labelCreator, func_name)
    labels, begin, end = func(dataset[:, col], **kwargs)
    df["LABEL"] = labels
    trim_indexes.append((begin, end))

def createDataFrames(raw_datasets, meta):
    dataFrames = []
    headerList = []

    print "createDataFrames --- len(raw_datasets): ", len(raw_datasets)
    start = timeit.default_timer()
    for idx, dataset in enumerate(raw_datasets):
        print "Dataset: %s/%s" % (idx + 1, len(raw_datasets))
        df = pd.DataFrame()
        trim_indexes = []

        for d in meta["raw_columns"]:
            _rawAppend(dataset, df, trim_indexes, d)
        print "Raw Append done"

        tmp_start = timeit.default_timer()
        for d in meta["indicators"]:
            _indicatorAppend(dataset, df, trim_indexes, d)
        tmp_end = timeit.default_timer()
        print "indicators done. elapsed: ", tmp_end - tmp_start

        print "Creating label..."
        _createLabel(dataset, df, trim_indexes, meta["label"])
        print "label creation done"

        begin_max = max(map(lambda x: x[0], trim_indexes))
        end_max = max(map(lambda x: x[1], trim_indexes))

        values = df.values[begin_max: -end_max, :]
        dataFrames.append(values)

        if not headerList:
            headerList = list(df)

    end = timeit.default_timer()
    print "total processing time: ", end - start

    return dataFrames, headerList
