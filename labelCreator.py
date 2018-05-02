import numpy as np
import learningHelper as LH

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
    print "createLabelConstantIncrease"
    changes, begin, end = LH.calculatePercentageChange(prices, step)
    print changes
    labels = np.zeros_like(changes)
    for i in range(len(changes)):
        label = 0
        for point in class_points:
            if changes[i] > point:
                label += 1
            else:
                break
        labels[i] = label

    print "changes: "
    print changes[:100]
    print "labels: "
    print labels[:100]
    print np.unique(labels, return_counts=True)


