{{
    config(
        materialized='view'
    )
}}

SELECT *
FROM {{ source('staging', 'fhv_tripdata') }}
WHERE dispatching_base_num IS NOT NULL