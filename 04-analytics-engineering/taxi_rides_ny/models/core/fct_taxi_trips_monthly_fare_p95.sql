with
    filtered as (
        select
            service_type,
            fare_amount,
            extract(year from pickup_datetime) as pu_year,
            extract(month from pickup_datetime) as pu_month
        from {{ ref("fact_trips") }}
        where
            fare_amount > 0
            and trip_distance > 0
            and payment_type_description in ('Cash', 'Credit card')
    )

select distinct 
    service_type,
    pu_year,
    pu_month,
    ROUND(percentile_cont(fare_amount, 0.90) over (
        partition by service_type, pu_year, pu_month
    ),2) as p90,
    ROUND(percentile_cont(fare_amount, 0.95) over (
        partition by service_type, pu_year, pu_month
    ),2) as p95,
    ROUND(percentile_cont(fare_amount, 0.97) over (
        partition by service_type, pu_year, pu_month
    ),2) as p97,

from filtered
ORDER BY 1,2,3
