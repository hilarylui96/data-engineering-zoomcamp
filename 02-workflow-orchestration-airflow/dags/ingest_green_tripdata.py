from datetime import datetime

#https://registry.astronomer.io/providers
from airflow.models.dag import DAG
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.transfers.bigquery_to_bigquery import BigQueryToBigQueryOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

import pyarrow.parquet as pq
import pandas as pd
from utilities.queries import (create_tripdata_table, create_tripdata_external_table, 
                               truncate_table, copy_table_and_add_id_filename, truncate_table, merge_table)
from utilities.constants import (DEFAULT_ARGS, AIRFLOW_PATH, DEFAULT_BQ_PROJECT, DEFAULT_BQ_DATASET, 
                       RAW_DATA_URL, FILE_NAME_BASE, BQ_PROD_TABLE, BQ_STAG_TABLE, BQ_EXT_TABLE)


def test_gcp_connection():
    """
    gcp credentials are saved in /.google locally which is mount to /opt/airflow/google in the container (see docker-compose.yaml)
    set up Google Cloud connection in Airflow UI and set Keyfile Path to /opt/airflow/google/credentials.json 
    """
    hook = GCSHook(gcp_conn_id="google_cloud_default")
    project_id = hook.project_id
    print(f"Using GCP Project ID: {project_id}")
    client = hook.get_conn()
    buckets = list(client.list_buckets())  # Convert iterator to list
    print(f"Buckets in project {project_id}: {[bucket.name for bucket in buckets]}")
   
with DAG ( 
  dag_id="gcp_setup",
  default_args=DEFAULT_ARGS,
  schedule=None,
  catchup=False,
) as dag:
  
  test_gcp_task = PythonOperator(
      task_id="test_gcp_connection",
      python_callable=test_gcp_connection,
      dag=dag
  )

  create_new_dataset_task = BigQueryCreateEmptyDatasetOperator(
    # Using default_args for required fields such as project_id and dataset_id
    task_id="create_new_dataset",
    if_exists="log",
    exists_ok="ignore"
  )

with DAG ( 
  dag_id="ingest_green_tripdata",
  default_args=DEFAULT_ARGS,
  start_date=datetime(2019,1,1),
  end_date=datetime(2021,7,31),
  schedule="@monthly",
  max_active_runs=1,
  catchup=True
  ) as dag2:

  file_name_base = FILE_NAME_BASE.format(year_month="{{ execution_date.strftime('%Y-%m') }}")
  bq_extension_table = BQ_EXT_TABLE.format(year_month="{{ execution_date.strftime('%Y-%m') }}")

  download_data_task = BashOperator(
    task_id="download_data",
    bash_command=f"""
      wget -qO- {RAW_DATA_URL}/{file_name_base}.csv.gz \
      | gunzip > ./"{file_name_base}.csv"
      """,
      cwd= AIRFLOW_PATH
  )

  upload_to_gcs_task = LocalFilesystemToGCSOperator(
     task_id="upload_to_gcs",
     src=f"/opt/airflow/data/{file_name_base}.csv",
     dst="green_taxi/"
  )

  create_prod_table_task = BigQueryInsertJobOperator(
    task_id="create_prod_table",
    configuration={
      "query": {
        "query": create_tripdata_table.format(
            table=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{BQ_PROD_TABLE}"
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
            table=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{BQ_STAG_TABLE}"
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
           bucket_path=f"{DEFAULT_ARGS['bucket']}/green_taxi/{file_name_base}.csv",
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
           table=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{BQ_STAG_TABLE}"
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
            dst=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{BQ_STAG_TABLE}",
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
            dst=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{BQ_PROD_TABLE}",
            src=f"{DEFAULT_BQ_PROJECT}.{DEFAULT_BQ_DATASET}.{BQ_STAG_TABLE}"
        ),
        "useLegacySql": False
      }
    }
  )

  purge_file_task = BashOperator(
     task_id="purge_file",
     bash_command="rm -rf {file_name_base}.csv",
     cwd= AIRFLOW_PATH
  )

test_gcp_task >> create_new_dataset_task 

download_data_task >> upload_to_gcs_task >> [create_prod_table_task, create_staging_table_task, create_external_table_task] 
create_staging_table_task >> truncate_staging_table_task
[truncate_staging_table_task, create_external_table_task]  >> copy_to_staging_table_task 
[create_prod_table_task, copy_to_staging_table_task] >> merge_to_prod_table_task >>  purge_file_task