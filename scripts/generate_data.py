import random
import datetime
import string
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
            "BQ_PROJECT": "prj-data-fulll-data-dev-bf85",
            "SERVICE_ACCOUNT": "sa-dbt-fulll-dev@prj-astrafy-main-courses.iam.gserviceaccount.com",
        },
        "prd": {
            "BQ_PROJECT": "prj-data-fulll-data-prd-f6de",
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

    # Create a client
    def create_client(self):
        try:
            return bigquery.Client(
                project=self.BQ_PROJECT,
                credentials=self.credentials
            )
        except Exception as e:
            print(f'Error creating client: {e}')
            return None
    
    def insert_data_to_bq(self, data, table_name):
        """
        Insert data into BigQuery table.
        """
        if not self.client:
            print("BigQuery client is not initialized.")
            return

        table_id = f"{self.BQ_PROJECT}.{self.BQ_DATASET}.{table_name}"
        errors = self.client.insert_rows_json(table_id, data)

        if errors:
            print("Error inserting into {table_name}: {errors}")
        else:
            print(f"Successfully loaded {len(data)} rows into {table_name}")

# Helper Functions
def random_string(length):
    return "".join(random.choices(string.ascii_uppercase, k=length))

def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + datetime.timedelta(days=random_days)

def generate_customer(num_rows):
    return [
        {
            "id": f"CUST{str(i).zfill(4)}",
            "name": f"{random_string(5)} {random_string(7)}",
            "email": f"{random_string(5).lower()}@example.com",
            "country": random.choice(["US", "EU", "UK"]),
            "signup_date": random_date(datetime.date(2020, 1, 1), datetime.date(2023, 10, 1)).isoformat(),
            "ingested_date": datetime.date.today().isoformat(),
        }
        for i in range(1, num_rows + 1)
    ]

def generate_products(num_rows):
    categories = ["Electronics", "Clothing", "Home", "Sports", "Books"]
    return [
        {
            "id": f"PROD{str(i).zfill(4)}",
            "name": f"Product {random_string(5)}",
            "category": random.choice(categories),
            "price": round(random.uniform(10, 500), 2),
            "in_stock": random.choice([True, False]),
            "ingested_date": datetime.date.today().isoformat(),
        }
        for i in range(1, num_rows + 1)
    ]

def generate_transactions(num_rows, customer_ids, product_ids):
    return [
        {
            "id": f"TXN{str(i).zfill(4)}",
            "customer_id": random.choice(customer_ids),
            "product_id": random.choice(product_ids),
            "amount": round(random.uniform(20, 500), 2),
            "currency": random.choice(["USD", "EUR", "GBP"]),
            "transaction_date": random_date(datetime.date(2023, 1, 1), datetime.date(2023, 10, 31)).isoformat(),
            "ingested_date": datetime.date.today().isoformat(),
        }
        for i in range(1, num_rows + 1)
    ]



def generate_and_load(rows_per_table, environment):
    bq_client = BigQueryClient(environment)
    # Generate customer
    customer = generate_customer(rows_per_table)
    bq_client.insert_data_to_bq(customer, "customers")

    # Products
    products = generate_products(rows_per_table)
    bq_client.insert_data_to_bq(products, "products")

    # Transactions
    transactions = generate_transactions(
        rows_per_table,
        [c["id"] for c in customer],
        [p["id"] for p in products],
    )
     # Split transactions based on currency
    uk_transactions = [t for t in transactions if t["currency"] == "GBP"]
    us_transactions = [t for t in transactions if t["currency"] == "USD"]
    eu_transactions = [t for t in transactions if t["currency"] == "EUR"]

    # Insert transactions into relevant tables
    bq_client.insert_data_to_bq(uk_transactions, "transactions_uk")
    bq_client.insert_data_to_bq(us_transactions, "transactions_us")
    bq_client.insert_data_to_bq(eu_transactions, "transactions_eu")

if __name__ == "__main__":
    # Set environment: "dev" or "prd"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")  # Default to "dev" if not set
    generate_and_load(50, ENVIRONMENT)