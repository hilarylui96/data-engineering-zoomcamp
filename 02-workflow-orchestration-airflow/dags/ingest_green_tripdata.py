from datetime import datetime

#https://registry.astronomer.io/providers
from airflow.models.dag import DAG
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

import pyarrow.parquet as pq
import pandas as pd
from utilities.green_queries import (create_tripdata_table, create_tripdata_external_table, 
                               truncate_table, copy_table_and_add_id_filename, truncate_table, merge_table)
from utilities.constants import (DEFAULT_ARGS, AIRFLOW_PATH, DEFAULT_BQ_PROJECT, DEFAULT_BQ_DATASET, 
                       RAW_DATA_URL, FILE_NAME_BASE, BQ_PROD_TABLE, BQ_STAG_TABLE, BQ_EXT_TABLE)

with DAG ( 
  dag_id="ingest_green_tripdata",
  default_args=DEFAULT_ARGS,
  start_date=datetime(2019,1,1),
  end_date=datetime(2020,12,31),
  schedule_interval="0 8 2 * *",
  max_active_runs=1,
  catchup=True
  ) as dag2:

  color = "green"
  raw_data_url = RAW_DATA_URL.format(color=color)
  file_name_base = FILE_NAME_BASE.format(color=color, year_month="{{ execution_date.strftime('%Y-%m') }}")
  bq_prod_table = BQ_PROD_TABLE.format(color=color)
  bq_stag_table = BQ_STAG_TABLE.format(color=color)
  bq_extension_table = BQ_EXT_TABLE.format(color=color, year_month="{{ execution_date.strftime('%Y-%m') }}")

  download_data_task = BashOperator(
    task_id="download_data",
    bash_command=f"""
      wget -qO- {raw_data_url}/{file_name_base}.csv.gz \
      | gunzip > ./"{file_name_base}.csv"
      """,
    cwd= AIRFLOW_PATH
  )

  upload_to_gcs_task = LocalFilesystemToGCSOperator(
     task_id="upload_to_gcs",
     src=f"/opt/airflow/data/{file_name_base}.csv",
     dst=f"{color}_taxi/"
  )

  create_prod_table_task = BigQueryInsertJobOperator(
    task_id="create_prod_table",
    configuration={
      "query": {
        "query": create_tripdata_table.format(
            table=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{bq_prod_table}"
        ),
        "useLegacySql": False
      }
    }
  )

  create_staging_table_task = BigQueryInsertJobOperator(
    task_id="create_staging_table",
    configuration={
      "query": {
        "query": create_tripdata_table.format(
            table=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{bq_stag_table}"
        ),
        "useLegacySql": False
      }
    }
  )

  create_external_table_task = BigQueryInsertJobOperator(
    task_id="create_external_table",
    configuration={
      "query": {
        "query": create_tripdata_external_table.format(
           table=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{bq_extension_table}",
           bucket_path=f"{DEFAULT_ARGS['bucket']}/{color}_taxi/{file_name_base}.csv",
           format="CSV"
        ),
        "useLegacySql": False
      }
    }
  )

  truncate_staging_table_task = BigQueryInsertJobOperator(
     task_id="truncate_staging_table",
     configuration={
      "query": {
        "query": truncate_table.format(
           table=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{bq_stag_table}"
        ),
        "useLegacySql": False
      }
     }
  )

  copy_to_staging_table_task = BigQueryInsertJobOperator(
    task_id="copy_to_staging_table",
    configuration={
      "query": {
        "query": copy_table_and_add_id_filename.format(
            dst=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{bq_stag_table}",
            src=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{bq_extension_table}",
            file_name=f"{file_name_base}.csv"
        ),
        "useLegacySql": False
      }
    }
  )

  merge_to_prod_table_task = BigQueryInsertJobOperator(
    task_id="merge_to_prod_table",
    configuration={
      "query": {
        "query": merge_table.format(
            dst=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{bq_prod_table}",
            src=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{bq_stag_table}"
        ),
        "useLegacySql": False
      }
    }
  )

  purge_file_task = BashOperator(
     task_id="purge_file",
     bash_command=f"rm -rf {file_name_base}.csv",
     cwd= AIRFLOW_PATH
  )


download_data_task >> upload_to_gcs_task >> [create_prod_table_task, create_staging_table_task, create_external_table_task] 
create_staging_table_task >> truncate_staging_table_task
[truncate_staging_table_task, create_external_table_task]  >> copy_to_staging_table_task 
[create_prod_table_task, copy_to_staging_table_task] >> merge_to_prod_table_task >>  purge_file_task