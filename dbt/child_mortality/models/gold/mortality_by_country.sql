{{ config(materialized='table') }}

with source as (
    select *
    from read_parquet('s3://silver/health/child-mortality/child-mortality.parquet')
)

select
    entity,
    code,
    round(avg(mortality_rate), 2) as avg_mortality_rate,
    min(year)                     as first_year,
    max(year)                     as last_year
from source
group by entity, code
order by avg_mortality_rate desc
