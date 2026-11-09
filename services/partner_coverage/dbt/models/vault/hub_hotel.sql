{{ config(materialized='table', unique_key='hub_key') }}

with source as (
    select * from {{ source('raw', 'supplier_feeds') }}
),
deduplicated as (
    select
        md5(hotel_name || '|' || city) as hub_key,
        min(hotel_name) as hotel_name,
        min(city) as city
    from source
    group by 1
)
select * from deduplicated
