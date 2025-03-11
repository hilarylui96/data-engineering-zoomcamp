DEFAULT_ARGS = {
  "gcp_conn_id": "google_cloud_default",
  "project_id": "durable-isotope-450722-i2",
  "dataset_id": "airflow_de_zoomcamp",
  "location": "US",
  "bucket": "de-zoomcamp-airflow-hlui"
}

AIRFLOW_PATH = "/opt/airflow/data"
DEFAULT_BQ_PROJECT = DEFAULT_ARGS['project_id']
DEFAULT_BQ_DATASET = DEFAULT_ARGS['dataset_id']
RAW_DATA_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}"
FILE_NAME_BASE = "{color}_tripdata_{year_month}"
BQ_PROD_TABLE = "{color}_tripdata"
BQ_STAG_TABLE = "{color}_tripdata_staging" 
BQ_EXT_TABLE = "{color}_tripdata_{year_month}_ext"
