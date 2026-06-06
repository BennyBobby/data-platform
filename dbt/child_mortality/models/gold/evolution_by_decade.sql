{{ config(materialized='table') }}

with source as (
    select *
    from read_parquet('s3://silver/health/child-mortality/child-mortality.parquet')
),

by_decade as (
    select
        (year / 10) * 10          as decade,
        round(avg(mortality_rate), 2) as avg_mortality_rate
    from source
    where code is not null
    group by decade
)

select *
from by_decade
order by decade
