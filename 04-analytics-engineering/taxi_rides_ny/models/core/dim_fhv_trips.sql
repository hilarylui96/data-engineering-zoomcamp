SELECT
    fhv.dispatching_base_num,
    fhv.pickup_datetime,
    fhv.dropoff_datetime,
    EXTRACT(year from pickup_datetime) as year,
    EXTRACT(month from pickup_datetime) as month,
    fhv.PULocationID,
    pickup_zone.borough as pickup_borough, 
    fhv.DOLocationID,
    dropoff_zone.borough as dropoff_borough, 
    fhv.Affiliated_base_number
FROM {{ ref('stg_fhv_tripdata') }} fhv
inner join {{ ref('dim_zones') }} as pickup_zone
on fhv.PULocationID = pickup_zone.locationid
inner join {{ ref('dim_zones') }} as dropoff_zone
on fhv.DOLocationID = dropoff_zone.locationid