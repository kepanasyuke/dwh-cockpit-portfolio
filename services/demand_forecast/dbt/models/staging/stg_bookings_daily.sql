select
    day_index,
    day,
    route,
    weekday,
    bookings,
    capacity
from {{ source('raw', 'bookings_daily') }}
where bookings >= 0
