select
    quote_id,
    route,
    price,
    demand,
    season_index,
    week
from {{ source('raw', 'quotes') }}
where price > 0
  and demand > 0
