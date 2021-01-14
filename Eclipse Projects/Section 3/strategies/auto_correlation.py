from zipline.api import order, symbol, record
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from scipy.stats.stats import pearsonr   


class AutoCorrelation:
    
    stocks = ['APL', 'MSFT', 'TSLA']
    lag = 1
    steps = 3
    
    def initialize(self, context):
        context.has_ordered = False
        context.stocks = self.stocks
        context.asset = symbol(self.stocks[-1])

    def handle_data(self, context, data):
        # loop stocks in portfolio
        for stock in context.stocks:
            # fetch history up to steps
            s1 = data.history(
                symbol(stock),
                'price',
                bar_count=self.steps,
                frequency='1d')
            
            # fetch history up to steps + lag and drop extra values
            s2 = data.history(
                symbol(stock),
                'price',
                bar_count=self.steps+self.lag,
                frequency='1d').iloc[:-1 * self.lag]

            # convert to numpy arrays
            np_s1 = np.array(s1.values)
            np_s2 = np.array(s2.values)

            # calculate auto-correlation
            corr, hypothesis = pearsonr(np_s1, np_s2)

            # fetch our basket status
            cpp = context.portfolio.positions
            
            # map basket to symbol:shares pairs
            cpp_symbols = map(lambda x: x.symbol, cpp)
            
            # what is today price
            curr_price = data.current(symbol(stock), 'price')
            
            # what was yesterday closing price
            last_price = data.history(
                symbol(stock),
                'price',
                bar_count=2,
                frequency='1d').iloc[0:1].values

            # go short or long positions
            if corr < -0.75 and hypothesis < 0.85:
                # is stock falling? exit position
                if curr_price < last_price:
                    order(symbol(stock), -1 * cpp[symbol(stock)].amount)
                # is stock rising? enter position
                elif curr_price > last_price:
                    order(symbol(stock), 1000)

        record(ASSETME=data.current(context.asset, 'price'))
        record(CORR=corr)

    def _test_args(self):
        return {
            'start': pd.Timestamp('2017', tz='utc'),
            'end': pd.Timestamp('2018', tz='utc'),
            'capital_base': 1e7
        }
    
    def analyze(self, context, perf):
        # init figure
        fig = plt.figure()
        
        # plot stock price
        ax1 = fig.add_subplot(211)
        perf['ASSETME'].plot(ax=ax1)
        ax1.set_ylabel('price in $')
    
        # plot correlation
        ax2 = fig.add_subplot(212)
        perf['CORR'].plot(ax=ax2)
        ax2.set_ylabel('correlation')
        
        # plot confidence levels
        ax2.axhline(0.75, linestyle='dashed', color='k')
        ax2.axhline(0, linestyle='dashed', color='b')
        ax2.axhline(-0.75, linestyle='dashed', color='k')
        
        # add spacing between plots
        plt.subplots_adjust(hspace=1)

        # display plot
        plt.show()
