from zipline.api import order, symbol, record
from matplotlib import pyplot as plt
import pandas as pd
from joblib import load
import numpy as np


class BuyAndHold:
    
    stocks = ['AAPL', 'MSFT', 'TSLA']
    lag = 33
    forecast = 8
    
    def initialize(self, context):
        context.has_ordered = False
        context.stocks = self.stocks
        context.asset = symbol('AAPL')
        context.regressor = load('./strategies/models/rf_regressor.joblib')

    def handle_data(self, context, data):
        for stock in context.stocks:
            timeseries = data.history(
                symbol(stock),
                'price',
                bar_count=self.lag,
                frequency='1d')
            np_timeseries = np.array(timeseries.values).reshape(1, -1)
            preds = context.regressor.predict(np_timeseries)
            max_price = np.max(preds)
            historical_mean = np.mean(np_timeseries)
            
            if max_price > historical_mean:
                order(symbol(stock), 1000)
            
            if max_price < historical_mean:
                order(symbol(stock), -1000)
        
        record(AAPL=data.current(context.asset, 'price'))

    def _test_args(self):
        return {
            'start': pd.Timestamp('2017', tz='utc'),
            'end': pd.Timestamp('2018', tz='utc'),
            'capital_base': 1e7
        }
    
    def analyze(self, context, perf):
        fig = plt.figure()
        ax1 = fig.add_subplot(211)
        perf.portfolio_value.plot(ax=ax1)
        ax1.set_ylabel('portfolio value in $')
    
        ax2 = fig.add_subplot(212)
        perf['AAPL'].plot(ax=ax2)

        ax2.set_ylabel('price in $')
        plt.legend(loc=0)
        plt.show()
