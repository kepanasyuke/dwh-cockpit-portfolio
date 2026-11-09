select
    booking_id,
    city as city_name,
    hotel,
    channel,
    lead_time_days,
    nights,
    amount,
    deposit,
    is_refundable,
    past_cancels,
    cancelled
from {{ source('raw', 'booking_events') }}
where booking_id is not null
  and lead_time_days between 0 and 400
