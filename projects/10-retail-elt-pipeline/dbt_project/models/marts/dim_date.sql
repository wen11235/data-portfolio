-- Date spine covering the loaded order data's range. Generated directly
-- with DuckDB's generate_series rather than pulling in the dbt_utils
-- package for a single date_spine call — one fewer external dependency
-- for a pipeline that's already deliberately avoided depending on a live
-- external API (see pipeline/generate_daily_drops.py).

with bounds as (
    select min(OrderDate) as min_date, max(OrderDate) as max_date
    from {{ ref('stg_orders') }}
),

spine as (
    select unnest(generate_series(
        (select min_date from bounds),
        (select max_date from bounds),
        interval 1 day
    ))::date as OrderDate
)

select
    OrderDate,
    extract(year from OrderDate) as Year,
    extract(month from OrderDate) as Month,
    extract(day from OrderDate) as Day,
    extract(dow from OrderDate) as DayOfWeek,
    dayname(OrderDate) as DayName,
    (extract(dow from OrderDate) in (0, 6)) as IsWeekend
from spine
