{{ config(materialized='table') }}

with joined as (
    select
        b.*,
        c.channel,
        c.kind as channel_kind,
        city.city,
        city.country,
        d.day,
        d.week,
        d.is_weekend
    from {{ ref('stg_bookings') }} b
    left join {{ source('raw', 'dim_channel') }} c using (channel_id)
    left join {{ source('raw', 'dim_city') }} city using (city_id)
    left join {{ source('raw', 'dim_date') }} d using (date_id)
)

select
    *,
    case when status = 'confirmed' then amount else 0 end as realised_gmv
from joined
