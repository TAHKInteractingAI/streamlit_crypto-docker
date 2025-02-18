import pandas as pd
import numpy as np
import ta


def crossover(short_term, long_term):
    """Extract buy/sell position from crossover of 2 lines.

    Args:
        short_term: get buy position if this line crosses above long_term
        long_term: get sell position if this line crossed below short_term
    Returns:
        buy/sell position in 1 serie as 1/-1, 0 otherwise
    """
    position = pd.Series(np.where(short_term > long_term, 1, 0), index=short_term.index)
    position = position.diff()

    return position


def compare_threshold(indicator, buy_threshold=0, sell_threshold=0):
    """Extract buy/sell position from threshold comparision.

    Args:
        indicator: indicator value
        buy_threshold: threshold of buy position, default is 0
        sell_threshold: threshold of sell position, default is 0
    Returns:
        buy as 1, sell as -1 and 0 otherwise
    """
    position = pd.Series(index=indicator.index)
    buy_position = indicator[(indicator > buy_threshold) & (indicator.shift(1) <= buy_threshold)]
    sell_position = indicator[(indicator < sell_threshold) & (indicator.shift(1) >= sell_threshold)]
    position.loc[buy_position.index] = 1
    position.loc[sell_position.index] = -1

    return position


def find_position(df, paras, strat):
    if strat == 'EMA':
        short_window = int(paras['short_window'])
        long_window = int(paras['long_window'])

        ema_short = ta.trend.EMAIndicator(close=df['Close'],
                                          window=short_window)
        ema_long = ta.trend.EMAIndicator(close=df['Close'],
                                         window=long_window)

        position = crossover(short_term=ema_short.ema_indicator(),
                             long_term=ema_long.ema_indicator())

    elif strat == 'MACD':
        window_slow = int(paras['window_slow'])
        window_fast = int(paras['window_fast'])
        window_sign = int(paras['window_sign'])

        macd = ta.trend.MACD(close=df['Close'],
                             window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
        macd_diff = macd.macd_diff()
        position = compare_threshold(indicator=macd_diff)

    return position




