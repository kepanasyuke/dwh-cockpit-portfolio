{{ config(materialized='table') }}

-- сезонная модель: уровень направления × коэффициент дня недели
with train as (
    select * from {{ ref('stg_bookings_daily') }} where day_index < 28
),
seasonality as (
    select route, weekday, avg(bookings) as weekday_level
    from train
    group by route, weekday
),
levels as (
    select route, avg(bookings) as route_level
    from train
    group by route
),
factors as (
    select s.route,
           s.weekday,
           s.weekday_level / nullif(l.route_level, 0) as factor
    from seasonality s
    join levels l using (route)
),
backtest as (
    select * from {{ ref('stg_bookings_daily') }} where day_index >= 28
)
select
    b.day,
    b.route,
    round(l.route_level * f.factor) as plan,
    b.bookings as fact,
    round(100.0 * round(l.route_level * f.factor) / nullif(b.capacity, 0), 2) as load
from backtest b
join levels l using (route)
join factors f on f.route = b.route and f.weekday = b.weekday
