import numpy as np
from learningHelper import *
import indicators
from learingMeta import *


def rolling_window(data, window):
    '''
    This function creates rolling windows for 2d array
    :return:
    '''
    row_no, col_no = data.shape  # matrix shape
    print "data.shape: ", data.shape

    new_row_no, new_col_no = (row_no - window + 1, col_no * window)
    retVal = np.zeros((new_row_no, new_col_no))

    for i in range(window):
        base = i * col_no
        retVal[0, base: base + col_no] = data[i, :]

    for i in range(1, new_row_no):
        retVal[i, : -col_no] = retVal[i - 1, col_no:]
        retVal[i, -col_no:] = data[window + i - 1, :]

    # print "retVal\n", retVal
    return retVal


def rolling_window2(a, window, step_size):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1 - step_size, window)
    strides = a.strides + (a.strides[-1] * step_size,)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def window_stack(a, stepsize=1, width=3):
    return np.hstack(a[i:1 + i - width or None:stepsize] for i in range(0, width))


if __name__ == '__main__':
    m = np.random.randint(1, 1000, (5, 2)) * 1.0
    print m
    start = timeit.default_timer()
    # res = rolling_window(m, 120)
    res = rolling_window(m, 3)
    end = timeit.default_timer()

    print "elapsed: ", end - start
    print res
    print m[3:,]
    # func = getattr(indicators, "bb")
    # print func(m[:, [1]], period=2)
