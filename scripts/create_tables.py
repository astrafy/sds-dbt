from google.cloud import bigquery
import googleapiclient.discovery
import google.oauth2.credentials

import os

class BigQueryClient:
    """
    BigQuery Client that dynamically loads credentials based on environment (dev or prd).
    """

    CONFIG = {
        "dev": {
            "BQ_PROJECT": "prj-data-fulll-lz-dev-1c8b",
            "SERVICE_ACCOUNT": "sa-dbt-fulll-dev@prj-astrafy-main-courses.iam.gserviceaccount.com",
        },
        "prd": {
            "BQ_PROJECT": "prj-data-fulll-lz-prd-df5b",
            "SERVICE_ACCOUNT": "sa-dbt-fulll-prd@prj-astrafy-main-courses.iam.gserviceaccount.com",
        },
    }
    def __init__(self, environment):
        if environment not in self.CONFIG:
            raise ValueError(f"Invalid environment: {environment}. Use 'dev' or 'prd'.")

        self.environment = environment
        self.BQ_PROJECT = self.CONFIG[environment]["BQ_PROJECT"]
        self.SERVICE_ACCOUNT = self.CONFIG[environment]["SERVICE_ACCOUNT"]
        self.BQ_DATASET = "bqdts_company_lz"
        self.iam = googleapiclient.discovery.build("iamcredentials", "v1")
        self.credentials = self.create_credentials()
        self.client = self.create_client()



    # Create credentials from the JSON key file
    def create_credentials(self):
        try:
            token = (
                self.iam.projects()
                .serviceAccounts()
                .generateAccessToken(
                    name=f"projects/-/serviceAccounts/{self.SERVICE_ACCOUNT}",
                    body={
                        "lifetime": "3600s",
                        "scope": [
                            "https://www.googleapis.com/auth/bigquery",
                            "https://www.googleapis.com/auth/bigquery.insertdata",
                            "https://www.googleapis.com/auth/cloud-platform",
                            "https://www.googleapis.com/auth/devstorage.full_control",
                            "https://www.googleapis.com/auth/appengine.admin",
                            "https://www.googleapis.com/auth/cloudkms",
                            "https://www.googleapis.com/auth/logging.admin",
                            "https://www.googleapis.com/auth/monitoring",
                            "https://www.googleapis.com/auth/pubsub",
                            "https://www.googleapis.com/auth/compute",
                        ],
                    },
                )
            )

            token = token.execute()["accessToken"]
            credentials = google.oauth2.credentials.Credentials(token)
            return credentials
        except Exception as e:
            print(f'Error creating credentials: {e}')
            return None
    def create_client(self):
        """
        Create a BigQuery client with generated credentials.
        """
        try:
            return bigquery.Client(project=self.BQ_PROJECT, credentials=self.credentials)
        except Exception as e:
            print(f"Error creating BigQuery client: {e}")
            return None

    def create_dataset(self):
        """
        Create a BigQuery dataset.
        """
        if not self.client:
            print("BigQuery client is not initialized.")
            return

        dataset_ref = self.client.dataset(self.BQ_DATASET)
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "EU"

        try:
            self.client.create_dataset(dataset, timeout=30, exists_ok=True)
            print(f"Dataset '{self.BQ_DATASET}' created or already exists.")
        except Exception as e:
            print(f"Error creating dataset '{self.BQ_DATASET}': {e}")

    def get_table_schema(self, table_name):
        """
        Define schema for different tables.
        """
        schemas = {
            "transactions": [
                bigquery.SchemaField("id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("customer_id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("product_id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("amount", "NUMERIC", mode="NULLABLE"),
                bigquery.SchemaField("currency", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("transaction_date", "DATE", mode="NULLABLE"),
                bigquery.SchemaField("ingested_date", "DATE", mode="NULLABLE"),
            ],
            "customers": [
                bigquery.SchemaField("id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("email", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("country", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("signup_date", "DATE", mode="NULLABLE"),
                bigquery.SchemaField("ingested_date", "DATE", mode="NULLABLE"),
            ],
            "products": [
                bigquery.SchemaField("id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("category", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("price", "NUMERIC", mode="NULLABLE"),
                bigquery.SchemaField("in_stock", "BOOLEAN", mode="NULLABLE"),
                bigquery.SchemaField("ingested_date", "DATE", mode="NULLABLE"),
            ],
        }

        if "transactions" in table_name:
            return schemas["transactions"]

        return schemas.get(table_name, [])

    def create_table(self, table_name):
        """
        Create a table with the specified schema.
        """
        if not self.client:
            print("BigQuery client is not initialized.")
            return None

        table_id = f"{self.BQ_PROJECT}.{self.BQ_DATASET}.{table_name}"
        table_ref = bigquery.TableReference.from_string(table_id)

        # Check if the table exists and delete it
        try:
            table = self.client.get_table(table_ref)
            self.client.delete_table(table)
            print(f"Table {table_id} deleted.")
        except Exception:
            pass  # Table does not exist, no need to delete

        # Create the table
        table = bigquery.Table(table_ref, schema=self.get_table_schema(table_name))
        try:
            self.client.create_table(table)
            print(f"Table {table_id} created.")
            return table
        except Exception as e:
            print(f"Error creating table {table_id}: {e}")
            return None

    def setup_bigquery(self):
        """
        Create dataset and tables in BigQuery.
        """
        self.create_dataset()
        tables = ["customers", "products", "transactions_eu", "transactions_us", "transactions_uk"]
        for table_name in tables:
            self.create_table(table_name)

if __name__ == "__main__":
    # Set environment: "dev" or "prd"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")  # Default to "dev" if not set
    bq_manager = BigQueryClient(ENVIRONMENT)
    bq_manager.setup_bigquery()