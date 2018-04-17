from learningHelper import *
import numpy as np
import pandas as pd

def checkCommonExceptions(ind_name, prices, period):
    num_prices = len(prices)
    if period < 0:
        raise Exception("{} period < 0".format(ind_name))
    if num_prices < period:
        raise Exception("{} num_prices < period".format(ind_name))

def sma(prices, period=20):
    '''
    Simple Moving Average (SMA)
    SMA = (P1 + P2 + ... + Pn) / K

    :param prices: price vector
    :param period: sma period
    :return: it returns simple moving average, begin offset, end offset
    '''
    checkCommonExceptions("sma", prices, period)

    ret = np.cumsum(prices, dtype=float)
    ret[period:] = ret[period:] - ret[:-period]
    ret[:period - 1] = 0
    return ret / period, period - 1, 0

def wma(prices, period=20):
    '''
    Weighted Moving Average (WMA)

    WMA = (P1 + 2 P2 + 3 P3 + ... + n Pn) / K
    where K = (1+2+...+n) = n(n+1)/2 and Pn is the most recent price after the
    1st WMA we can use another formula
    WMAn = WMAn-1 + w.(Pn - SMA(prices, n-1))
    where w = 2 / (n + 1)

    :param prices:
    :param period:
    :return:
    '''
    checkCommonExceptions("wma", prices, period)

    k = (period * (period + 1)) / 2.0
    weights = np.arange(1, period + 1, dtype=float) / k

    wmas = np.zeros(prices.shape[0])

    for i in xrange(period, len(prices) + 1):
        wmas[i - 1] = np.dot(prices[i - period: i].reshape(*weights.shape), weights)

    return wmas, period - 1, 0

def ema(prices, period=20):
    '''
    Exponencial Moving Average (EMA)

    EMAn = w.Pn + (1 - w).EMAn-1
    EMAn = w.Pn + w.(1 - w).Pn-1 + w.(1 - w)^2.Pn-2 + ... +
    w.(1 - w)^(n-1).P1 + w.(1 - w)^n.EMA0
    where w = 2 / (n + 1) and EMA0 = mean(oldest period)

    :param prices:
    :param period:
    :return:
    '''
    checkCommonExceptions("ema", prices, period)

    emas = np.zeros(prices.shape[0])
    emas[:period - 1] = 0
    emas[period - 1] = np.mean(prices[:period])

    w = 2. / float(period + 1)

    for i in xrange(period, len(prices)):
        emas[i] = w * prices[i] + (1 - w) * emas[i - 1]

    return emas, period - 1, 0

def rsi(prices, period=14):
    '''
    Relative Strength Index (RSI)

    RSI = 100 - 100  / (1 + RS)
    RS  = Average Gain / Average Loss

    The very first calculations for average gain and average loss are simple 14-period averages.
        First Average Gain = Sum of Gains over the past 14 periods / 14.
        First Average Loss = Sum of Losses over the past 14 periods / 14

    The second, and subsequent, calculations are based on the prior averages and the current gain loss:
        Average Gain = [(previous Average Gain) x 13 + current Gain] / 14.
        Average Loss = [(previous Average Loss) x 13 + current Loss] / 14.
    :param prices: price vector
    :param period: rsi period
    :return: it returns rsi vector, begin offset, end offset
    '''
    checkCommonExceptions("rsi", prices, period)
    rsis = np.zeros(prices.shape[0])
    changes = np.diff(prices.T[0])  # Conver column vector to row vector
                                    # then take first row as a vector

    # First Calculation
    seed = changes[:period]
    avg_gain = seed[seed > 0].sum() / period
    avg_loss = -seed[seed < 0].sum() / period

    if avg_loss == 0:
        rsis[period] = 1.
    else:
        rs = avg_gain / avg_loss
        rsis[period] = 1. - (1. / (1. + rs))

    # Rest
    for i in xrange(period + 1, len(prices)):
        delta = changes[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            gain = delta
            loss = 0.
        else:
            gain = 0.
            loss = -delta
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

        if avg_loss == 0:
            rsis[i] = 1.
        else:
            rs = avg_gain / avg_loss
            rsis[i] = 1. - (1. / (1. + rs))

    return rsis, period, 0

def bb(prices, period=20, num_std_dev=2.0):
    '''
    Bollinger Bands (BB)

    Middle Band = 20-day simple moving average (SMA)
    Upper Band = 20-day SMA + (20-day standard deviation of price x 2)
    Lower Band = 20-day SMA - (20-day standard deviation of price x 2)
    %B = (Price - Lower Band)/(Upper Band - Lower Band)

    :param prices: price vector
    :param period: bb period
    :return: it returns upper band, lower band and %B as a matrix, begin offset, end offset
    '''
    _prices = prices.T[0]
    checkCommonExceptions("bb", _prices, period)
    pdData = pd.DataFrame(data=_prices)
    m = np.zeros((_prices.shape[0], 3))  # upper, lower, B

    means = pdData.rolling(period).mean().fillna(0).values.T
    stds = pdData.rolling(period).std(ddof=0).fillna(0).values.T

    m[:, 0] = (means + (stds * num_std_dev))  # upper
    m[:, 1] = (means - (stds * num_std_dev))  # lower

    with np.errstate(divide='ignore', invalid='ignore'):
        divisor = (m[:, 0] - m[:, 1])

        if divisor[divisor < 0].any():
            raise Exception("BB divisor cannot be less than 0!")

        m[:, 2] = (_prices - m[:, 1]) / divisor
        x = m[:, 2]

        # setting inft values
        x[divisor == 0] = 1.

        # setting nan values to 0
        np.nan_to_num(x, copy=False)

        # min max normalization
        x[x < -2] = -2.
        x[x > 2] = 2.

    return m, period, 0

def stochastic(ohlc, k_period=14, d_period=3):
    '''
    Stochastic Oscillator ()
    %K = (Current Close - Lowest Low)/(Highest High - Lowest Low) * 100
    %D = 3-day SMA of %K

    Lowest Low = lowest low for the look-back period
    Highest High = highest high for the look-back period
    :param ohlc: numpy matrix, columns: open, high, low , close
    :param d_period:
    :param k_period:
    :return: it returns %K and %D values as a matrix,
    '''
    df = pd.DataFrame(data=ohlc, columns=["open", "high", "low", "close"])

    df['L'] = df['low'].rolling(window=k_period).min()
    df['H'] = df['high'].rolling(window=k_period).max()

    # Create the "%K" column in the DataFrame
    df['%K'] = (df['close'] - df['L']) / (df['H'] - df['L'])
    df.fillna(0, inplace=True)

    if df['%K'][df['%K'] < 0].any() or df['%K'][df['%K'] > 1].any():
        raise Exception("stochastic out of bound!")

    # Create the "%D" column in the DataFrame
    df['%D'] = df['%K'].rolling(window=d_period).mean()
    return df.values[:, -2:], d_period + k_period, 0

import timeit
if __name__ == '__main__':
    m = np.random.randint(1, 10, (20, 4)) * 1.0
    m[:, 1] = m[:, 0] - np.random.randint(0, 2)     # high
    m[:, 2] = m[:, 0] - np.random.randint(0, 2)     # low
    m[:, 3] = m[:, 0] - np.random.randint(0, 10)                               # close


    print m
    start = timeit.default_timer()
    res = stochastic(m)
    print res
    print res[0].shape
    # ret = stochastic(m)
    end = timeit.default_timer()

    print "time: ", end - start

