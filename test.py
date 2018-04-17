import numpy as np
from learningHelper import *
import indicators
from learingMeta import *



if __name__ == '__main__':
    m = np.random.randint(1, 10, (10, 3)) * 1.0
    print m

    func = getattr(indicators, "bb")
    print func(m[:, [1]], period=2)
