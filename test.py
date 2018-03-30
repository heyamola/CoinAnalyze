import numpy as np
import random

if __name__ == '__main__':
    data = []
    for i in range(10):
        data.append(random.randint(1, 10) * 1.0)


    a = np.array([[1,2,3], [4,11,6], [7,8,9]])
    print a
    print a[:, 1].mean()

    exit(1)
    data = np.array(data)
    print data

    step = 1
    data1 = data[:-step]
    data2 = data[step:]

    print "data1: ", data1
    print "data2: ", data2

    ret = np.zeros(data.shape)
    ret[:-step] = (data2 - data1) / data1
    print "return: "
    print ret

    def rolling_window(a, window, step_size):
        shape = a.shape[:-1] + (a.shape[-1] - window + 1 - step_size, window)
        strides = a.strides + (a.strides[-1] * step_size,)
        return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

    print "\n"
    window_size = 5
    label_step = 1

    rolledData = rolling_window(ret, window_size, 1)
    labels = ret[window_size + label_step - 1:]

    print "rolledData: "
    print rolledData[:-label_step]

    print "labels:"
    print labels[:-1]