-- Recency/Frequency/Monetary per customer, computed in-warehouse — same
-- definition as Project 1's notebook (projects/01-retail-customer-
-- analytics): Recency in days since last order relative to a snapshot
-- date one day after the most recent order in the loaded data; Frequency
-- is distinct orders; Monetary is total spend. Deliberately doesn't repeat
-- Project 1's KMeans segmentation here — that's a modeling step that
-- belongs in a notebook with sklearn, not a SQL transform; this mart's job
-- is to hand a clean, warehouse-native feature table to whatever
-- downstream tool (a notebook, a BI dashboard) needs it.

with bounds as (
    select max(OrderDate) + interval 1 day as snapshot_date
    from {{ ref('fct_orders') }}
)

select
    o.CustomerID,
    date_diff('day', max(o.OrderDate), (select snapshot_date from bounds)) as Recency,
    count(distinct o.InvoiceNo) as Frequency,
    round(sum(o.TotalPrice), 2) as Monetary
from {{ ref('fct_orders') }} o
group by o.CustomerID
