from google.cloud import bigquery
import os
from schemas import get_table_schema

class BigQueryClient:
    """
    BigQuery Client that uses application default credentials.
    """

    CONFIG = {
        "dev": {
            "BQ_PROJECT": "prj-data-fulll-lz-dev-1c8b",
        },
        "prd": {
            "BQ_PROJECT": "prj-data-fulll-lz-prd-df5b",
        },
    }
    def __init__(self, environment):
        if environment not in self.CONFIG:
            raise ValueError(f"Invalid environment: {environment}. Use 'dev' or 'prd'.")

        self.environment = environment
        self.BQ_PROJECT = self.CONFIG[environment]["BQ_PROJECT"]
        self.BQ_DATASET = "bqdts_create_table"
        self.client = self.create_client()

    def create_client(self):
        """
        Create a BigQuery client using application default credentials.
        """
        try:
            return bigquery.Client(project=self.BQ_PROJECT)
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
        table = bigquery.Table(table_ref, schema=get_table_schema(table_name))
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
        tables = ["customers", "items", "orders", "products", "stores", "supplies", "tweets"]
        for table_name in tables:
            self.create_table(table_name)

if __name__ == "__main__":
    # Set environment: "dev" or "prd"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")  # Default to "dev" if not set
    bq_manager = BigQueryClient(ENVIRONMENT)
    bq_manager.setup_bigquery()