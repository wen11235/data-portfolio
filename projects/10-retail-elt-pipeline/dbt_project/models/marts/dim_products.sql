-- One row per product. Description occasionally varies slightly for the
-- same StockCode across orders (free-text field on the source system) —
-- resolved the same way as dim_customers' Country: most frequent value
-- wins, picked explicitly rather than left to an arbitrary aggregate.

with description_counts as (
    select
        StockCode,
        Description,
        count(*) as n,
        row_number() over (partition by StockCode order by count(*) desc, Description) as rn
    from {{ ref('stg_orders') }}
    group by StockCode, Description
)

select
    s.StockCode,
    dc.Description,
    round(avg(s.UnitPrice), 2) as AvgUnitPrice,
    sum(s.Quantity) as TotalUnitsSold
from {{ ref('stg_orders') }} s
join description_counts dc on s.StockCode = dc.StockCode and dc.rn = 1
group by s.StockCode, dc.Description
