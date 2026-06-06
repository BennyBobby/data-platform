{{ config(materialized='table') }}

with source as (
    select * from {{ source('staging', 'child_mortality') }}
    where code is not null
),

by_decade as (
    select
        (year / 10) * 10                       as decade,
        round(avg(mortality_rate)::numeric, 2) as avg_mortality_rate
    from source
    group by decade
)

select *
from by_decade
order by decade
