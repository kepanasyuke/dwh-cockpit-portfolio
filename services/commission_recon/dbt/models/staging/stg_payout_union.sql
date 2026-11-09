-- федеративный запрос: два каталога Trino (payout и billing) в одном CTE
select
    partner,
    day,
    accrued,
    'payout' as source
from {{ source('payout_catalog', 'fact_payouts') }}

union all

select
    partner,
    day,
    0 as accrued,
    'billing' as source
from {{ source('billing_catalog', 'fact_billing') }}
where billed > 0
