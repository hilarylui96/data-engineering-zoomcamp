SELECT distinct
    year,
    month,
    pickup_borough,
    dropoff_borough,
    percentile_cont(TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime,SECOND),0.9) 
        OVER(partition by year, month, PULocationID, DOLocationID) as trip_duration_p90
FROM {{ ref('dim_fhv_trips') }}