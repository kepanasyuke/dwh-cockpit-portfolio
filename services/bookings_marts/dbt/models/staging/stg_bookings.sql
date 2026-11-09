{{ config(materialized='view') }}

select
    booking_id,
    date_id,
    city_id,
    channel_id,
    nights,
    rooms,
    amount,
    guests,
    status,
    amount / nullif(nights * rooms, 0) as nightly_rate
from {{ source('raw', 'fact_bookings') }}
where booking_id is not null
