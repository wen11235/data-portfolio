-- Cleaned, one-row-per-line-item view: drops cancellations (InvoiceNo
-- starting 'C'), rows with no CustomerID (can't attribute to a customer),
-- and non-positive Quantity/UnitPrice (data entry errors). Same rules as
-- Project 1's notebook (projects/01-retail-customer-analytics), just
-- expressed in SQL instead of pandas, and applied here at the warehouse
-- layer instead of in a notebook — the standard ELT pattern: load raw
-- as-is, transform where the rest of the pipeline can reuse and test it.

with source as (
    select * from {{ source('raw', 'orders_raw') }}
)

select
    InvoiceNo,
    StockCode,
    Description,
    Quantity,
    InvoiceDate,
    cast(InvoiceDate as date) as OrderDate,
    UnitPrice,
    cast(CustomerID as bigint) as CustomerID,
    Country,
    round(Quantity * UnitPrice, 2) as TotalPrice,
    _batch_date
from source
where
    left(InvoiceNo, 1) != 'C'
    and CustomerID is not null
    and Quantity > 0
    and UnitPrice > 0
