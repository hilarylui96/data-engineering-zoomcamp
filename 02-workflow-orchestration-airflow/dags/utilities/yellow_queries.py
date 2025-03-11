create_tripdata_table = """
  CREATE TABLE IF NOT EXISTS `{table}`(
    unique_row_id BYTES,
    filename STRING,      
    VendorID INT64,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count INT64,
    trip_distance FLOAT64,
    RatecodeID INT64,
    store_and_fwd_flag STRING,  
    PULocationID INT64,
    DOLocationID INT64,   
    payment_type INT64,   
    fare_amount FLOAT64,
    extra FLOAT64,
    mta_tax FLOAT64,
    tip_amount FLOAT64,
    tolls_amount FLOAT64,
    improvement_surcharge FLOAT64,
    total_amount FLOAT64,
    congestion_surcharge FLOAT64
  );
"""


create_tripdata_external_table = """
  CREATE OR REPLACE EXTERNAL TABLE `{table}`(
    VendorID INT64,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count INT64,
    trip_distance FLOAT64,
    RatecodeID INT64,
    store_and_fwd_flag STRING,  
    PULocationID INT64,
    DOLocationID INT64,   
    payment_type INT64,   
    fare_amount FLOAT64,
    extra FLOAT64,
    mta_tax FLOAT64,
    tip_amount FLOAT64,
    tolls_amount FLOAT64,
    improvement_surcharge FLOAT64,
    total_amount FLOAT64,
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
          COALESCE(CAST(tpep_pickup_datetime AS STRING), ""),
          COALESCE(CAST(tpep_dropoff_datetime AS STRING), ""),
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
    INSERT (unique_row_id, filename, VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge)
    VALUES (S.unique_row_id, S.filename, S.VendorID, S.tpep_pickup_datetime, S.tpep_dropoff_datetime, S.passenger_count, S.trip_distance, S.RatecodeID, S.store_and_fwd_flag, S.PULocationID, S.DOLocationID, S.payment_type, S.fare_amount, S.extra, S.mta_tax, S.tip_amount, S.tolls_amount, S.improvement_surcharge, S.total_amount, S.congestion_surcharge);
"""