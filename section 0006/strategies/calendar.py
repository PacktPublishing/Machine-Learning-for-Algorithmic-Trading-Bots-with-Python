from zipline.utils.calendars import TradingCalendar
from datetime import time
from pandas.tseries.offsets import CustomBusinessDay
from pytz import timezone
from zipline.utils.memoize import lazyval


class CryptoCalendar(TradingCalendar):
    """
    Exchange calendar for 24/7 trading.

    Open Time: 12am, UTC
    Close Time: 11:59pm, UTC

    """
    @property
    def name(self):
        return "cryptocalendar"

    @property
    def tz(self):
        return timezone("UTC")

    @property
    def open_time(self):
        return time(0, 0)

    @property
    def close_time(self):
        return time(23, 59)

    @property
    def open_times(self):
        return [(None, time(0, 0))]

    @property
    def close_times(self):
        return [(None, time(23, 59))]

    @lazyval
    def day(self):
        return CustomBusinessDay(
            weekmask='Mon Tue Wed Thu Fri Sat Sun',
        )