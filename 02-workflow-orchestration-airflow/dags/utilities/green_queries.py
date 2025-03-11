create_tripdata_table = """
  CREATE TABLE IF NOT EXISTS `{table}`(
    unique_row_id BYTES,
    filename STRING,
    VendorID INT64,
    lpep_pickup_datetime TIMESTAMP,
    lpep_dropoff_datetime TIMESTAMP,
    store_and_fwd_flag STRING,
    RatecodeID INT64,
    PULocationID INT64,
    DOLocationID INT64,
    passenger_count INT64,
    trip_distance FLOAT64,
    fare_amount FLOAT64,
    extra FLOAT64,
    mta_tax FLOAT64,
    tip_amount FLOAT64,
    tolls_amount FLOAT64,
    ehail_fee FLOAT64,
    improvement_surcharge FLOAT64,
    total_amount FLOAT64,
    payment_type INT64,
    trip_type INT64,
    congestion_surcharge FLOAT64
  );
"""


create_tripdata_external_table = """
  CREATE OR REPLACE EXTERNAL TABLE `{table}`(
    VendorID INT64,
    lpep_pickup_datetime TIMESTAMP,
    lpep_dropoff_datetime TIMESTAMP,
    store_and_fwd_flag STRING,
    RatecodeID INT64,
    PULocationID INT64,
    DOLocationID INT64,
    passenger_count INT64,
    trip_distance FLOAT64,
    fare_amount FLOAT64,
    extra FLOAT64,
    mta_tax FLOAT64,
    tip_amount FLOAT64,
    tolls_amount FLOAT64,
    ehail_fee FLOAT64,
    improvement_surcharge FLOAT64,
    total_amount FLOAT64,
    payment_type INT64,
    trip_type INT64,
    congestion_surcharge FLOAT64
  )
  OPTIONS (
    uris = ['gs://{bucket_path}'],
    format = '{format}',
    field_delimiter = ',',
    skip_leading_rows = 1
  );
"""


copy_table_and_add_id_filename = """
  CREATE OR REPLACE TABLE `{dst}`
  AS
  SELECT
      MD5(CONCAT(
          COALESCE(CAST(VendorID AS STRING), ""),
          COALESCE(CAST(lpep_pickup_datetime AS STRING), ""),
          COALESCE(CAST(lpep_dropoff_datetime AS STRING), ""),
          COALESCE(CAST(PULocationID AS STRING), ""),
          COALESCE(CAST(DOLocationID AS STRING), "")
      )) AS unique_row_id,
      '{file_name}' AS filename,
      *
  FROM `{src}`
"""

truncate_table = """
  TRUNCATE TABLE `{table}`
"""


merge_table = """
  MERGE INTO `{dst}` T
  USING `{src}` S
  ON T.unique_row_id = S.unique_row_id
  WHEN NOT MATCHED THEN 
    INSERT (unique_row_id, filename, VendorID, lpep_pickup_datetime, lpep_dropoff_datetime, store_and_fwd_flag, RatecodeID, PULocationID, DOLocationID, passenger_count, trip_distance, fare_amount, extra, mta_tax, tip_amount, tolls_amount, ehail_fee, improvement_surcharge, total_amount, payment_type, trip_type, congestion_surcharge)
    VALUES (S.unique_row_id, S.filename, S.VendorID, S.lpep_pickup_datetime, S.lpep_dropoff_datetime, S.store_and_fwd_flag, S.RatecodeID, S.PULocationID, S.DOLocationID, S.passenger_count, S.trip_distance, S.fare_amount, S.extra, S.mta_tax, S.tip_amount, S.tolls_amount, S.ehail_fee, S.improvement_surcharge, S.total_amount, S.payment_type, S.trip_type, S.congestion_surcharge)
"""