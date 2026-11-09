{{ config(materialized='incremental', unique_key='model || hour') }}

with runs as (
    select
        model,
        layer,
        hour,
        lag_hours,
        rows,
        status
    from {{ source('airflow', 'pipeline_runs') }}
),
checks as (
    select
        model,
        rule,
        status,
        failed_rows,
        lag_hours
    from {{ source('airflow', 'dq_checks') }}
),
per_model as (
    select
        model,
        layer,
        max(lag_hours) as lag_hours,
        max(rows) as rows,
        sum(case when status = 'fail' then 1 else 0 end) as failed_runs
    from runs
    group by model, layer
)
select
    m.model,
    m.layer,
    round(m.lag_hours, 2) as lag_hours,
    m.rows,
    m.failed_runs,
    count(c.rule) as checks_total,
    sum(case when c.status = 'fail' then 1 else 0 end) as checks_failed,
    case
        when m.lag_hours > 5.5 or sum(case when c.status = 'fail' then 1 else 0 end) > 0 then 'fail'
        when m.lag_hours > 3.0 then 'warn'
        else 'ok'
    end as status
from per_model m
left join checks c on c.model = m.model
group by m.model, m.layer, m.lag_hours, m.rows, m.failed_runs
