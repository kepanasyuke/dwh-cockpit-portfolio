{{ config(materialized='table', unique_key='route') }}

-- log-log МНК: наклон регрессии ln(demand) ~ ln(price) равен эластичности
with points as (
    select route, ln(price) as x, ln(demand) as y
    from {{ ref('stg_quotes') }}
),
means as (
    select route, avg(x) as mx, avg(y) as my
    from points
    group by route
),
moments as (
    select
        p.route,
        sum((p.x - m.mx) * (p.y - m.my)) as sxy,
        sum((p.x - m.mx) * (p.x - m.mx)) as sxx,
        sum((p.y - m.my) * (p.y - m.my)) as syy
    from points p
    join means m using (route)
    group by p.route
),
fitted as (
    select
        route,
        sxy / nullif(sxx, 0) as elasticity,
        sxy * sxy / nullif(sxx * syy, 0) as r2
    from moments
)
select
    route,
    round(elasticity, 3) as elasticity,
    round(r2, 3) as r2,
    case when elasticity < -1 then 'raise' else 'hold' end as price_action
from fitted
