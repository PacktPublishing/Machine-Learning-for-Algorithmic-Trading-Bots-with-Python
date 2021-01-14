import pandas as pd

from zipline.data.bundles import register
from zipline.data.bundles.csvdir import csvdir_equities

start_session = pd.Timestamp('2017-01-01 00:00:00', tz='utc')
end_session = pd.Timestamp('2017-12-31 23:59:00', tz='utc')

register(
    'crypto-bundle',
    csvdir_equities(
        ['minute'],
        '/path/to/your/csvs',
    ),
    calendar_name='NYSE', # US equities
    start_session=start_session,
    end_session=end_session
)