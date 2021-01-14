from toolz import merge 
from zipline import run_algorithm
from zipline.utils.calendars import register_calendar, get_calendar
from strategies.buy_and_hold import BuyAndHold
from strategies.auto_correlation import AutoCorrelation
from os import environ
from strategies.scalping import ScalpBollingerBand
import pandas as pd
import os
import pytz
from collections import OrderedDict
from strategies.calendar import CryptoCalendar


# Columns that we expect to be able to reliably deterministic
# Doesn't include fields that have UUIDS.
_cols_to_check = [
    'algo_volatility',
    'algorithm_period_return',
    'alpha',
    'benchmark_period_return',
    'benchmark_volatility',
    'beta',
    'capital_used',
    'ending_cash',
    'ending_exposure',
    'ending_value',
    'excess_return',
    'gross_leverage',
    'long_exposure',
    'long_value',
    'longs_count',
    'max_drawdown',
    'max_leverage',
    'net_leverage',
    'period_close',
    'period_label',
    'period_open',
    'pnl',
    'portfolio_value',
    'positions',
    'returns',
    'short_exposure',
    'short_value',
    'shorts_count',
    'sortino',
    'starting_cash',
    'starting_exposure',
    'starting_value',
    'trading_days',
    'treasury_period_return',
]


def prepareCSV(csv_pth):
    files = os.listdir(csv_pth)
    start = end = None
    
    dd = OrderedDict()
    for f in files:
        fp = os.path.join(csv_pth, f)
        n1 = os.path.splitext(fp)[0]
        key = n1.split('/')[1]
        df = pd.read_csv(fp)
        df.index = pd.DatetimeIndex(df.date)
        df = df.sort_index()
        dd[key] = df.drop(columns=['date'])
        start = df.index.values[0]
        end = df.index.values[10*24*60]
    
    panel = pd.Panel(dd)

    panel.major_axis = panel.major_axis.tz_localize(pytz.utc)

    return panel, pd.to_datetime(start).tz_localize(pytz.utc), pd.to_datetime(end).tz_localize(pytz.utc)


def run_strategy(strategy_name):
    mod = None
    
    if strategy_name == "buy_and_hold": 
        mod = BuyAndHold()
    elif strategy_name == "auto_correlation":
        mod = AutoCorrelation()
    elif strategy_name == "scalping":
        mod = ScalpBollingerBand()

#     register_calendar("YAHOO", get_calendar("NYSE"), force=True)
    data_panel, start, end = prepareCSV('csv')
    print(data_panel, type(start))
 
    return run_algorithm(
        data=data_panel,
        trading_calendar=CryptoCalendar(),
        initialize=getattr(mod, 'initialize', None),
        handle_data=getattr(mod, 'handle_data', None),
        before_trading_start=getattr(mod, 'before_trading_start', None),
        analyze=getattr(mod, 'analyze', None),
#         bundle='quandl',
        environ=environ,
        data_frequency='minute',
        # Provide a default capital base, but allow the test to override.
        **merge({
            'capital_base': 1000,
            'start': start,
            'end': end
            }, mod._test_args())
    )
