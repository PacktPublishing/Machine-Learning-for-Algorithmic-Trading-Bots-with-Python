from toolz import merge 
from zipline import run_algorithm
from zipline.utils.calendars import register_calendar, get_calendar
from strategies.buy_and_hold import BuyAndHold
from os import environ


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
 
 
def run_strategy(strategy_name):
    mod = None
    
    if strategy_name == "buy_and_hold": 
        mod = BuyAndHold()
 
    register_calendar("YAHOO", get_calendar("NYSE"), force=True)
 
    return run_algorithm(
        initialize=getattr(mod, 'initialize', None),
        handle_data=getattr(mod, 'handle_data', None),
        before_trading_start=getattr(mod, 'before_trading_start', None),
        analyze=getattr(mod, 'analyze', None),
        bundle='quandl',
        environ=environ,
        # Provide a default capital base, but allow the test to override.
        **merge({'capital_base': 1e7}, mod._test_args())
    )


 
 