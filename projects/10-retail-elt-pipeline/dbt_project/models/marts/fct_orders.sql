-- Fact table, grain = one row per (InvoiceNo, StockCode) line item.
-- Foreign keys to dim_customers/dim_products/dim_date, tested for
-- referential integrity in schema.yml.

select
    s.InvoiceNo,
    s.StockCode,
    s.CustomerID,
    s.OrderDate,
    s.Quantity,
    s.UnitPrice,
    s.TotalPrice,
    s._batch_date
from {{ ref('stg_orders') }} s
