import numpy as np
"""
    [
                [
                    1499040000000,      # Open time
                    "0.01634790",       # Open
                    "0.80000000",       # High
                    "0.01575800",       # Low
                    "0.01577100",       # Close
                    "148976.11427815",  # Volume
                    1499644799999,      # Close time
                    "2434.19055334",    # Quote asset volume
                    308,                # Number of trades
                    "1756.87402397",    # Taker buy base asset volume
                    "28.46694368",      # Taker buy quote asset volume
                    "17928899.62484339" # Can be ignored
                ]
            ]
    """
OPEN_TIME           = (0, "OPEN_TIME")
OPEN                = (1, "OPEN")
HIGH                = (2, "HIGH")
LOW                 = (3, "LOW")
CLOSE               = (4, "CLOSE")
VOLUME              = (5, "VOLUME")
CLOSE_TIME          = (6, "CLOSE_TIME")
QUOTE_VOLUME        = (7, "QUOTE_VOLUME")
NUMBER_OF_TRADE     = (8, "NUMBER_OF_TRADE")
BUY_BASE_VOLUME     = (9, "BUY_BASE_VOLUME")
BUY_QUOTE_VOLUME    = (10, "BUY_QUOTE_VOLUME")


ROW = 0
COLUMN = 1

def calculatePercentageChange(data, step=1):
    '''
    According to given step, it calculates percentage change
    :param data: as a vector
    :param step: according to (n + step) change is calculated
    :return: it returns percentages change as a vector, begin offset, end offset
    '''

    ret = np.copy(data)
    data1 = ret[:-step]
    data2 = ret[step:]

    with np.errstate(divide='ignore', invalid='ignore'):
        ret[: -step] = (data2 - data1) / data1

    # mask nan values to 1
    t = np.where(np.isnan(ret))
    ret[t] = 1.

    # mask inf value to 0
    t = np.where(np.isinf(ret))
    ret[t] = 0.

    ret[ret < -500] = 500.
    ret[ret > 500] = 500.

    # if ret[ret < -2500].any():
    #     raise Exception("Change calculation error! Min value exceeded")
    # if ret[ret > 2500].any():
    #     raise Exception("Change calculation error! Max value exceeded")

    return ret, step, step


def append_to_matrix(m, v, axis=COLUMN):
    '''
    if m(matrix) is none, then assing v(vector) to m
    o.w according to given axis, append v to m
    :param m: base matrix
    :param v: given vector
    :param axis: row base or column base append
    '''

    if type(m) == type(None):
        return np.copy(v)

    if axis == ROW:
        if len(v.shape) == 1:
            tmp_v = v.reshape(1, v.shape[0])
        else:
            tmp_v = v
        return np.r_[m, tmp_v]
    else:
        return np.c_[m, v]

def calculate_column_min_max(dataset, index):
    _min, _max = dataset[:, index].min(), dataset[:, index].max()
    if _min == _max:
        raise Exception("Column min max values are equal!")
    return _min, _max

def normalize_column(dataset, index):
    _min, _max = calculate_column_min_max(dataset, index)
    dataset[:, index] = (dataset[:, index] - _min) / (_max - _min)

def normalize_dataset(dataset):
    for i in range(dataset.shape[1]):
        normalize_column(dataset, i)
