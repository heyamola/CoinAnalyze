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


def calculateReturns(data, index, step=1):

    data1 = data[ :-step    , index]
    data2 = data[step:      , index]

    ret = (data2 - data1) / data1

    return ret

