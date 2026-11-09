{{ config(materialized='table', unique_key='booking_id') }}

with features as (
    select
        *,
        -4.3
        + 0.011 * lead_time_days
        + 0.045 * nights
        + 0.0000045 * amount
        + 0.32 * (channel = 'web')::int
        - 0.28 * (channel = 'partner')::int
        + 0.62 * is_refundable
        + 0.55 * past_cancels as logit
    from {{ ref('stg_bookings_events') }}
)

select
    booking_id,
    city_name,
    hotel,
    channel,
    lead_time_days,
    amount,
    cancelled,
    round((1 / (1 + exp(-logit)))::numeric, 4) as risk,
    round(((1 / (1 + exp(-logit))) * amount)::numeric, 2) as expected_loss
from features
