{{ config(materialized='table') }}

with source as (
    select * from {{ source('staging', 'child_mortality') }}
    where code is not null
)

select
    year,
    round(avg(mortality_rate)::numeric, 2) as global_avg_mortality
from source
group by year
order by year
