create_tripdata_table = """
  CREATE TABLE IF NOT EXISTS `{table}`(
    unique_row_id BYTES,
    filename STRING,
    dispatching_base_num STRING,
    pickup_datetime  TIMESTAMP,
    dropOff_datetime  TIMESTAMP,
    PULocationID INT64,
    DOLocationID INT64,
    SR_Flag INT64,
    Affiliated_base_number STRING
  );
"""


create_tripdata_external_table = """
  CREATE OR REPLACE EXTERNAL TABLE `{table}`(
    dispatching_base_num STRING,
    pickup_datetime  TIMESTAMP,
    dropOff_datetime  TIMESTAMP,
    PULocationID INT64,
    DOLocationID INT64,
    SR_Flag INT64,
    Affiliated_base_number STRING
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
          COALESCE(CAST(dispatching_base_num AS STRING), ""),
          COALESCE(CAST(pickup_datetime AS STRING), ""),
          COALESCE(CAST(dropoff_datetime AS STRING), ""),
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
    INSERT (unique_row_id, filename, dispatching_base_num, pickup_datetime, dropoff_datetime, PULocationID, DOLocationID, SR_Flag, Affiliated_base_number)
    VALUES (S.unique_row_id, S.filename, S.dispatching_base_num, S.pickup_datetime, S.dropoff_datetime, S.PULocationID, S.DOLocationID, S.SR_Flag, S.Affiliated_base_number)
"""