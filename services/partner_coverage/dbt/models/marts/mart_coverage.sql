{{ config(materialized='table', unique_key='city') }}

-- mart_coverage: отели по городам, спрос и ключевой поставщик
with per_city as (
    select city, count(distinct hub_key) as hotels
    from {{ ref('hub_hotel') }}
    group by city
),
per_supplier as (
    select
        h.city,
        l.supplier,
        count(*) as cnt,
        row_number() over (partition by h.city order by count(*) desc) as rn
    from {{ ref('hub_hotel') }} h
    join {{ source('raw', 'hotel_supplier_links') }} l using (hub_key)
    group by h.city, l.supplier
),
demand as (
    select city, demand from {{ source('raw', 'market_demand') }}
)
select
    d.city,
    coalesce(pc.hotels, 0) as hotels,
    d.demand,
    least(100.0, round(100.0 * coalesce(pc.hotels, 0) / greatest(3, round(d.demand / 600.0)), 1)) as coverage,
    coalesce(ps.supplier, '—') as top_supplier
from demand d
left join per_city pc on pc.city = d.city
left join per_supplier ps on ps.city = d.city and ps.rn = 1
