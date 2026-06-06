{{ config(materialized='table') }}

with source as (
    select *
    from read_parquet('s3://silver/health/child-mortality/child-mortality.parquet')
    where code is not null
),

with_bounds as (
    select
        entity,
        code,
        year,
        mortality_rate,
        min(year) over (partition by entity) as first_year,
        max(year) over (partition by entity) as last_year
    from source
),

first_and_last as (
    select
        entity,
        code,
        max(first_year)                                                      as first_year,
        max(last_year)                                                       as last_year,
        round(max(case when year = first_year then mortality_rate end), 2)   as first_rate,
        round(max(case when year = last_year  then mortality_rate end), 2)   as last_rate
    from with_bounds
    group by entity, code
)

select
    entity,
    code,
    first_year,
    last_year,
    first_rate,
    last_rate,
    round(first_rate - last_rate, 2) as improvement
from first_and_last
where first_rate is not null
  and last_rate is not null
order by improvement desc
limit 10
