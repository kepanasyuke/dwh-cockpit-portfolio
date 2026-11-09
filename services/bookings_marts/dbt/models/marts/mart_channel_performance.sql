{{ config(materialized='table', unique_key='channel') }}

select
    channel,
    channel_kind,
    count(*) as attempts,
    sum(case when status = 'confirmed' then 1 else 0 end) as bookings,
    round(sum(realised_gmv), 2) as gmv,
    round(avg(case when status = 'confirmed' then amount end), 2) as adr,
    round(100.0 * sum(case when status = 'confirmed' then 1 else 0 end) / count(*), 2) as conversion
from {{ ref('int_booking_revenue') }}
group by channel, channel_kind
