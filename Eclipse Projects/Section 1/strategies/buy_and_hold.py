from zipline.api import order, symbol, record
from matplotlib import pyplot as plt
import pandas as pd


class BuyAndHold:
    
    stocks = ['AAPL', 'MSFT', 'TSLA']
    
    def initialize(self, context):
        context.has_ordered = False
        context.stocks = self.stocks
        context.asset = symbol('AAPL')
     
    def handle_data(self, context, data):
        if not context.has_ordered:
            for stock in context.stocks:
                order(symbol(stock), 100)
            context.has_ordered = True
        
        record(AAPL=data.current(context.asset, 'price'))

    def _test_args(self):
        return {
            'start': pd.Timestamp('2008', tz='utc'),
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
