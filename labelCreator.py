import numpy as np
import learningHelper as LH
import pandas as pd


def createLabelConstantIncrease(prices, step=30, class_points=[-0.1, 0.1]):
    '''
    It creates labels as given number of class.
    Ex:
        price[i] < -0.1         -> class 1
        -0.1 < price[i] < 0.1   -> class 2
        price[i] > 0.1          -> class 3

    :param prices: create labels based on prices, it is a numpy column vector
    :param num_class: number of class
    :param diff: class range
    :return: it returns labels, begin trim, end trim
    '''
    changes, begin, end = LH.calculatePercentageChange(prices, step)

    # printing label info
    # tmp = np.zeros_like(prices)
    # tmp[:-step] = prices[step:]
    #
    # # df = pd.DataFrame()
    # df["prices"] = prices
    # df["prices_step"] = tmp
    # df["changes"] = changes
    #
    # df.to_csv("check.csv")

    labels = np.zeros_like(changes)
    for i in range(len(changes)):
        label = 0
        for point in class_points:
            if changes[i] > point:
                label += 1
            else:
                break
        labels[i] = label

    u, c = np.unique(labels, return_counts=True)
    print "createLabelConstantIncrease - unique labels: ", dict(zip(u, c))

    return labels, begin, end


def labelSplitter(labels):
    '''
    labels are enumerated as 0, 1...
    this function binarizes labels by creating new columns
    :param labels: labels as a numpy vector
    :return: matrix as a binary label
    '''
    u = np.unique(labels)
    m = np.zeros((len(labels), len(u)))
    for i in range(len(labels)):
        m[i, int(labels[i])] = 1
    return m
