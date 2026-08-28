-- One row per customer. Country is the customer's most frequent country
-- (a handful of customers have orders tagged to more than one country in
-- the raw data — a real messiness worth resolving explicitly here rather
-- than silently picking whichever row happens to sort first).

with country_counts as (
    select
        CustomerID,
        Country,
        count(*) as n,
        row_number() over (partition by CustomerID order by count(*) desc, Country) as rn
    from {{ ref('stg_orders') }}
    group by CustomerID, Country
)

select
    s.CustomerID,
    cc.Country,
    min(s.OrderDate) as FirstOrderDate,
    max(s.OrderDate) as LastOrderDate,
    count(distinct s.InvoiceNo) as TotalOrders
from {{ ref('stg_orders') }} s
join country_counts cc on s.CustomerID = cc.CustomerID and cc.rn = 1
group by s.CustomerID, cc.Country
