{{ config(materialized='table', unique_key='partner') }}

with payouts as (
    select partner, sum(accrued) as accrued
    from {{ source('payout_catalog', 'fact_payouts') }}
    group by partner
),
billing as (
    select partner, sum(billed) as billed
    from {{ source('billing_catalog', 'fact_billing') }}
    group by partner
),
merged as (
    select p.partner, p.accrued, coalesce(b.billed, 0) as billed
    from payouts p
    left join billing b using (partner)
    union all
    select b.partner, 0 as accrued, b.billed
    from billing b
    where b.partner not in (select partner from payouts)
)
select
    partner,
    round(sum(accrued), 2) as accrued,
    round(sum(billed), 2) as billed,
    round(sum(accrued) - sum(billed), 2) as diff,
    case
        when abs(sum(accrued) - sum(billed)) < 1 then 'matched'
        when abs(sum(accrued) - sum(billed)) < 900 then 'minor'
        else 'open'
    end as status
from merged
group by partner
