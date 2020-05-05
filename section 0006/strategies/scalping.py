from zipline.api import order, symbol, record
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np 
from joblib import load


class ScalpBollingerBand:
    
    stocks = ['BTCUSD', 'ETHUSD']
    ma1 = 10
    ma2 = 120
    steps = 1280
    stop_loss = 0.005
    stdv = 0.5


    def initialize(self, context):
        context.stocks = self.stocks
        context.asset = symbol(self.stocks[-1])
        
        context.burndown = 0
        context.number_shorts = 0
        context.number_longs = 0
        
        context.position = {}
        for stock in self.stocks:
            context.position[stock] = None
        
        # VaR
        context.historical_returns = []
        
        #SVR
        context.regressor = load('./strategies/models/sv_regressor.joblib')


    def handle_data(self, context, data):
        # wait till enough historical data arrives for calculations
        context.burndown += 1
        
        # log while backtesting
        if context.burndown % 1000 == 0:
            print(context.burndown)

        # calculate VaR only when there is enough data
        if len(context.historical_returns) > 15:
    
            # Non-Parametric Historical Value at Risk
            
            # history
            historical_returns = np.array(context.historical_returns)
            
            # forecast
            forecast_returns = context.regressor.predict(
                                    historical_returns[-15:].reshape(1, -1)
                                )

            # VaR
            lowest_percentile = np.percentile(
                                    np.concatenate(
                                        (
                                            historical_returns,
                                            forecast_returns[0]
                                        ), axis=0
                                    ), 0.05)
            expected_shortfall = np.mean(
                                    np.where(
                                        historical_returns <= lowest_percentile
                                        )
                                    )
            
            # stop loss value
            value_at_risk = expected_shortfall / 60 / 24

            # exit all positions
            if ( context.portfolio.returns <= value_at_risk ):
                # loop stocks in portfolio
                for i, stock in enumerate(context.stocks):
                    # are we in a trade?
                    if context.position[stock] == 'trade':
                        # short position
                        order(symbol(stock), 0)
                        context.position[stock] = None
                        context.number_shorts += 1
                        print('Stop Loss: {} @ VaR {} for {}'.format(
                            context.portfolio.returns,
                            value_at_risk,
                            stock
                            )
                        )


        # trade only when there is enough data
        if context.burndown > self.steps:

            # loop stocks in portfolio
            for i, stock in enumerate(context.stocks):
                # history
                hist = data.history(
                    symbol(stock),
                    'price',
                    bar_count=self.steps,
                    frequency='1m')
                
                # bollinger bands
                blw = hist.mean() - self.stdv * hist.std()
                bhi = hist.mean() + self.stdv * hist.std()
                
                # moving average short
                short_term = data.history(
                    symbol(stock),
                    'price',
                    bar_count=self.ma1,
                    frequency='1m').mean()
    
                # moving average long
                long_term = data.history(
                    symbol(stock),
                    'price',
                    bar_count=self.ma2,
                    frequency='1m').mean()
    
                # fetch our basket status
                cpp = context.portfolio.positions
                
                # map basket to symbol:shares pairs
                cpp_symbols = map(lambda x: x.symbol, cpp)
                
                # check indicator signal
                if short_term >= long_term and context.position[stock] != 'trade':
                    context.position[stock] = 'long'
                elif short_term <= long_term and context.position[stock] == 'trade':
                    context.position[stock] = 'short'


                # what is current price
                current_price = data.current(symbol(stock), 'price')
                
                
                # check bollinger bands
                if short_term >= bhi and context.position[stock] == 'long':
                    # how many shares I can afford?
                    num_shares = context.portfolio.cash // current_price
                    
                    # long position
                    order(symbol(stock), num_shares)  # order_value
                    context.position[stock] = 'trade'
                    context.number_longs += 1
                    print('Enter Trade: ', stock)
                
                elif (current_price <= blw and context.position[stock] == 'trade') \
                    or (short_term <= blw and context.position[stock] == 'short'):
                    # short position
                    order(symbol(stock), 0)
                    context.position[stock] = None
                    context.number_shorts += 1
                    print('Exit Trade: ', stock)

                
                # what is the price paid on beginning of trade
                last_price = cpp[symbol(stock)].last_sale_price
                
                # stop loss value
                val = last_price - last_price * self.stop_loss

                # are we in a trade?
                if context.position[stock] == 'trade':
                    # stop loss violated
                    if current_price < val:
                        # short position
                        order(symbol(stock), 0)
                        context.position[stock] = None
                        context.number_shorts += 1
                        print('Stop Loss: ', stock)
                
                # is last stock?
                if i == len(self.stocks) - 1:
                    
                    # record price, ma1, ma2, Bollinger bands
                    record(REC_PRICE=current_price)
                    record(REC_MA1=short_term)
                    record(REC_MA2=long_term)
                    record(REC_BB1=blw)
                    record(REC_BB2=bhi)
        
            context.historical_returns.append(context.portfolio.returns)
        
        # record positions count
        record(REC_NUM_SHORTS=context.number_shorts)
        record(REC_NUM_LONGS=context.number_longs)

    def _test_args(self):
        return {
#             'start': pd.Timestamp('2017', tz='utc'),
#             'end': pd.Timestamp('2018', tz='utc'),
#             'capital_base': 1e7,
#             'data_frequency': 'minute'
        }

    def analyze(self, context, perf):
        # init figure
        fig = plt.figure()
        
        # plot recorded data
        ax1 = fig.add_subplot(211)
        perf.plot(y=[
            'REC_PRICE',
            'REC_MA1',
            'REC_MA2'
            ], ax=ax1)
        ax1.set_ylabel('price in $')

        # plot recorded data
        ax2 = fig.add_subplot(212)
        perf.plot(y=[
            'REC_PRICE',
            'REC_BB1',
            'REC_BB2'
            ], ax=ax2)
        ax2.set_ylabel('Bollinger Bands')

        # add spacing between plots
        plt.subplots_adjust(hspace=1)
        
        # display plot
        plt.show()
