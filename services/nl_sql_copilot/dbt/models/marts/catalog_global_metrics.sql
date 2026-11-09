{{ config(materialized='table', unique_key='metric_key') }}

-- каталог метрик: сырые определения из источника, нормализованные для планировщика копайлота
select
    metric_key,
    label,
    table_name,
    expression,
    unit
from {{ source('raw', 'metrics_catalog') }}
where expression is not null
  and metric_key is not null
