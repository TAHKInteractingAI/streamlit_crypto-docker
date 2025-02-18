import numpy as np
from backtesting import Backtest, Strategy
from geneal.genetic_algorithms import ContinuousGenAlgSolver
from hyperopt import hp

from lib import lib_strategy



class GeneralStrategy(Strategy):
    def init(self):
        pass

    def next(self):
        if self.data.position == 1:
            self.buy()
        elif self.data.position == -1:
            self.position.close()


def compute_sharpe(returns, window=252):
    try:
        return np.sqrt(window) * (returns.mean() / returns.std())
    except:
        return np.nan


def backtest(df, cash, commission):
    bt = Backtest(df,
                  GeneralStrategy,
                  cash=cash,
                  commission=commission,
                  trade_on_close=True,
                  exclusive_orders=True)

    stats = bt.run()
    stats = stats.to_frame()
    # re-compute stats
    stats.loc['Duration'] = len(df)
    returns = stats.loc['_equity_curve'][0]['Equity'].pct_change()
    stats.loc['Sharpe Ratio'] = compute_sharpe(returns=returns)
    stats = stats.round(2)

    return bt, stats


def ga_config(df, cash, commission, max_gen, strat):
    if strat == 'EMA':
        n_genes = 2
        variables_limits = [(35, 65), (150, 250)]
        best_paras = {'short_window': 0,
                      'long_window': 0}
    elif strat == 'MACD':
        n_genes = 3
        variables_limits = [(10, 40), (5, 30), (5, 15)]
        best_paras = {'window_slow': 0,
                      'window_fast': 0,
                      'window_sign': 0}

    def score(paras):
        if strat == 'EMA':
            fspace = {'short_window': paras[0],
                      'long_window': paras[1]}

        elif strat == 'MACD':
            fspace = {'window_slow': paras[0],
                      'window_fast': paras[1],
                      'window_sign': paras[2]}

        position = lib_strategy.find_position(df, fspace, strat)
        df['position'] = position

        bt, stats = backtest(df, cash, commission)

        # optimize Sharpe ratio
        return -stats.loc['Sharpe Ratio'][0]
        # optimize gross return
        # return -stats.loc['Return [%]'][0]

    solver = ContinuousGenAlgSolver(
        n_genes=n_genes,
        fitness_function=score,
        pop_size=10,
        max_gen=max_gen,
        mutation_rate=0.1,
        selection_rate=0.6,
        selection_strategy='roulette_wheel',
        problem_type=float, # Defines the possible values as float numbers
        variables_limits=variables_limits # Defines the limits of all variables between -10 and 10.
                                          # Alternatively one can pass an array of tuples defining the limits
                                          # for each variable: [(-10, 10), (0, 5), (0, 5), (-20, 20)]
    )
    solver.solve()

    tune_res = list(solver.best_individual_)
    tune_res = [round(x) for x in tune_res]
    ii = 0
    for key in best_paras:
        best_paras[key] = tune_res[ii]
        ii += 1

    return best_paras


def bo_config(df, cash, commission, strat):
    if strat == 'EMA':
        fspace = {'short_window': hp.quniform('short_window', 35, 65, 1),
                  'long_window': hp.quniform('long_window', 150, 250, 1)}

    elif strat == 'MACD':
        fspace = {'window_slow': hp.quniform('window_slow', 10, 40, 1),
                  'window_fast': hp.quniform('window_fast', 5, 30, 1),
                  'window_sign': hp.quniform('window_sign', 5, 15, 1)}

    def score(paras):
        position = lib_strategy.find_position(df, paras, strat)
        df['position'] = position

        bt, stats = backtest(df, cash, commission)

        # optimize Sharpe ratio
        return -stats.loc['Sharpe Ratio'][0]
        # optimize gross return
        # return -stats.loc['Return [%]'][0]

    return score, fspace




