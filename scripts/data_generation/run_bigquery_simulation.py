#!/usr/bin/env python3
"""
Script to run the Jaffle Shop simulation and upload results to BigQuery.
"""
import sys
import argparse
import datetime
import random
from simulation_bigquery import SimulationBQ
from google.cloud import bigquery
from faker import Faker

fake = Faker()

def fetch_max_dates():
    """Fetch the max order_date and tweet_at from BigQuery."""
    client = bigquery.Client()

    # Fetch max date for orders
    max_order_query = "SELECT MAX(ordered_at) as max_order_date FROM `prj-data-fulll-lz-dev-1c8b.bqdts_company_lz.orders`"
    max_order_result = client.query(max_order_query).result()
    max_order_date = list(max_order_result)[0].max_order_date

    # Fetch max date for tweets
    max_tweet_query = "SELECT MAX(tweeted_at) as max_tweet_date FROM `prj-data-fulll-lz-dev-1c8b.bqdts_company_lz.tweets`"
    max_tweet_result = client.query(max_tweet_query).result()
    max_tweet_date = list(max_tweet_result)[0].max_tweet_date

    return max_order_date, max_tweet_date

def fetch_existing_data():
    """Fetch the list of existing customers, stores, and users from BigQuery."""
    client = bigquery.Client()

    # Fetch existing customers
    customers_query = "SELECT id FROM `prj-data-fulll-lz-dev-1c8b.bqdts_company_lz.customers`"
    customers_result = client.query(customers_query).result()
    existing_customers = [row.id for row in customers_result]

    # Fetch existing stores
    stores_query = "SELECT id FROM `prj-data-fulll-lz-dev-1c8b.bqdts_company_lz.stores`"
    stores_result = client.query(stores_query).result()
    existing_stores = [row.id for row in stores_result]

    # Fetch existing users
    users_query = "SELECT user_id FROM `prj-data-fulll-lz-dev-1c8b.bqdts_company_lz.tweets`"  # Assuming a users table
    users_result = client.query(users_query).result()
    existing_users = [row.user_id for row in users_result]

    return existing_customers, existing_stores, existing_users

def generate_new_data(max_order_date, max_tweet_date, existing_customers, existing_stores, existing_users):
    """Generate new records for orders and tweets."""
    new_orders = []
    new_tweets = []

    if isinstance(max_order_date, str):
        # Adjust the format if needed; this example assumes ISO format.
        max_order_date = datetime.datetime.fromisoformat(max_order_date)
    
    if isinstance(max_tweet_date, str):
        max_tweet_date = datetime.datetime.fromisoformat(max_tweet_date)
    
    for _ in range(100):
        # Generate a new order
        customer_id = random.choice(existing_customers)
        store_id = random.choice(existing_stores)
        new_order_date = max_order_date + datetime.timedelta(days=random.randint(1, 30))
        new_orders.append({
            'id': fake.uuid4(),
            'customer': customer_id,
            'ordered_at': new_order_date.isoformat(), 
            'store_id': store_id,
            'subtotal': random.randint(10, 500),
            'tax_paid': random.randint(5, 25),
            'order_total': random.randint(15, 525)
        })

    for _ in range(500):
        # Generate a new tweet
        user_id = random.choice(existing_users)
        new_tweet_date = max_tweet_date + datetime.timedelta(days=random.randint(1, 30))
        new_tweets.append({
            'id': fake.uuid4(),
            'user_id': user_id,
            'tweeted_at': new_tweet_date.isoformat(),
            'content': fake.text(max_nb_chars=280)
        })
    
    return new_orders, new_tweets

def insert_into_bigquery(new_orders, new_tweets):
    """Insert the generated records into BigQuery."""
    # Assuming the BigQuery client is already initialized
    client = bigquery.Client()

    # Insert orders into the orders table
    orders_table = client.get_table("prj-data-fulll-lz-dev-1c8b.bqdts_company_lz.orders")
    errors = client.insert_rows_json(orders_table, new_orders)
    if errors:
        print("Error inserting orders:", errors)

    # Insert tweets into the tweets table
    tweets_table = client.get_table("prj-data-fulll-lz-dev-1c8b.bqdts_company_lz.tweets")
    errors = client.insert_rows_json(tweets_table, new_tweets)
    if errors:
        print("Error inserting tweets:", errors)

def main():
    """Run the Jaffle Shop simulation and upload results to BigQuery."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Run Jaffle Shop simulation and upload to BigQuery"
    )
    parser.add_argument(
        "--years", 
        type=int, 
        default=1,
        help="Number of years to simulate (default: 1)"
    )
    parser.add_argument(
        "--days", 
        type=int, 
        default=0,
        help="Additional days beyond years to simulate (default: 0)"
    )
    parser.add_argument(
        "--prefix", 
        type=str, 
        default="jaffle",
        help="Prefix for table names (default: 'jaffle')"
    )
    parser.add_argument(
        "--project-id", 
        type=str, 
        required=True,
        help="Google Cloud project ID"
    )
    parser.add_argument(
        "--dataset-id", 
        type=str, 
        required=True,
        help="BigQuery dataset ID"
    )
    parser.add_argument(
        "--if-exists", 
        type=str, 
        choices=["fail", "replace", "append"], 
        default="replace",
        help="Action if tables already exist (default: 'replace')"
    )
    parser.add_argument(
        "--save-csv", 
        action="store_true",
        help="Also save data to local CSV files"
    )
    parser.add_argument(
        "--new-data",
        action="store_true",
        help="Generate and append new orders and tweets with dates after the max existing dates"
    )
    
    args = parser.parse_args()
    
    # Create and run the simulation
    try:
        # Initialize simulation
        simulation = SimulationBQ(
            years=args.years,
            days=args.days,
            project_id=args.project_id,
            dataset_id=args.dataset_id,
            if_exists=args.if_exists
        )
        
        if args.new_data:
            print("Fetching max dates for orders and tweets...")
            max_order_date, max_tweet_date = fetch_max_dates()
            print(f"Max order date: {max_order_date}")
            print(f"Max tweet date: {max_tweet_date}")

            print("Fetching existing data (customers, stores, users)...")
            existing_customers, existing_stores, existing_users = fetch_existing_data()

            print("Generating new data...")
            new_orders, new_tweets = generate_new_data(max_order_date, max_tweet_date, existing_customers, existing_stores, existing_users)

            print(f"Inserting {len(new_orders)} new orders and {len(new_tweets)} new tweets into BigQuery...")
            insert_into_bigquery(new_orders, new_tweets)

        else:
            print(f"Starting Jaffle Shop simulation with the following parameters:")
            print(f"- Years: {args.years}")
            print(f"- Days: {args.days}")
            print(f"- Google Cloud project: {args.project_id}")
            print(f"- BigQuery dataset: {args.dataset_id}")
            print(f"- If tables exist: {args.if_exists}")
            print(f"- Save to CSV: {args.save_csv}")

            # Run the full simulation
            print("\nRunning simulation...")
            simulation.run_simulation()

            # Upload results to BigQuery
            print("\nUploading results to BigQuery...")
            simulation.save_results(save_local_csv=args.save_csv)

            print("\n✓ Simulation completed successfully!")
            print(f"Tables have been created in the {args.dataset_id} dataset in your BigQuery project.")
          
    except Exception as e:
        print(f"\n✗ Error during simulation: {str(e)}")
        sys.exit(1)



if __name__ == "__main__":
    main()