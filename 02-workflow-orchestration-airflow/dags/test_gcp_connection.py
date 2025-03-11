from datetime import datetime

#https://registry.astronomer.io/providers
from airflow.models.dag import DAG
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator
from airflow.operators.python import PythonOperator

from utilities.constants import DEFAULT_ARGS


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

  test_gcp_task >> create_new_dataset_task 