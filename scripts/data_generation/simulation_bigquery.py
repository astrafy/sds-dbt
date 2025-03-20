import os
import pandas as pd
from typing import Any, Optional
from rich.progress import track
from jafgen.customers.customers import Customer
from jafgen.customers.order import Order
from jafgen.customers.tweet import Tweet
from jafgen.stores.inventory import Inventory
from jafgen.stores.market import Market
from jafgen.stores.stock import Stock
from jafgen.stores.store import Store
from jafgen.time import (
    Day,
    DayHoursOfOperation,
    WeekHoursOfOperation,
    time_from_total_minutes,
)

# Import pandas_gbq for BigQuery integration
import pandas_gbq

T_7AM = time_from_total_minutes(60 * 7)
T_8AM = time_from_total_minutes(60 * 8)
T_3PM = time_from_total_minutes(60 * 15)
T_8PM = time_from_total_minutes(60 * 20)

class SimulationBQ:
    def __init__(
        self, 
        years: int, 
        days: int, 
        project_id: str,
        dataset_id: str,
        if_exists: str = 'replace'
    ):
        self.years = years
        self.days = days
        self.scale = 100
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.if_exists = if_exists  # Options: 'fail', 'replace', or 'append'
        
        self.stores = [
            # name | popularity | opened | TAM | tax
            ("Philadelphia", 0.85, 0, 9 * self.scale, 0.06),
            ("Brooklyn", 0.95, 192, 14 * self.scale, 0.04),
            ("Chicago", 0.92, 605, 12 * self.scale, 0.0625),
            ("San Francisco", 0.87, 615, 11 * self.scale, 0.075),
            ("New Orleans", 0.92, 920, 8 * self.scale, 0.04),
            ("Los Angeles", 0.87, 1107, 8 * self.scale, 0.08),
        ]
        self.markets: list[Market] = [
            Market(
                Store(
                    name=store_name,
                    base_popularity=popularity,
                    hours_of_operation=WeekHoursOfOperation(
                        week_days=DayHoursOfOperation(opens_at=T_7AM, closes_at=T_8PM),
                        weekends=DayHoursOfOperation(opens_at=T_8AM, closes_at=T_3PM),
                    ),
                    opened_day=Day(opened_date),
                    tax_rate=tax,
                ),
                num_customers=market_size,
            )
            for store_name, popularity, opened_date, market_size, tax in self.stores
        ]
        self.customers: dict[CustomerId, Customer] = {}
        self.orders: list[Order] = []
        self.tweets: list[Tweet] = []
        self.sim_days = 365 * self.years + self.days
        
    def run_simulation(self):
        for i in track(
            range(self.sim_days), description=f"🥪 Pressing {self.sim_days} days of fresh jaffles..."
        ):
            for market in self.markets:
                day = Day(i)
                for order, tweet in market.sim_day(day):
                    if order:
                        self.orders.append(order)
                        if order.customer.id not in self.customers:
                            self.customers[order.customer.id] = order.customer
                    if tweet:
                        self.tweets.append(tweet)
    
    def save_results(self, save_local_csv: bool = False) -> None:
        """
        Save the simulation results to BigQuery tables.
        
        Args:
            save_local_csv: If True, also save local CSV files (default: False)
        """
        stock: Stock = Stock()
        inventory: Inventory = Inventory()
        
        # Create dictionaries for each entity
        entities_data: dict[str, list[dict[str, Any]]] = {
            "customers": [customer.to_dict() for customer in self.customers.values()],
            "orders": [order.to_dict() for order in self.orders],
            "items": [item.to_dict() for order in self.orders for item in order.items],
            "stores": [market.store.to_dict() for market in self.markets],
            "supplies": stock.to_dict(),
            "products": inventory.to_dict(),
            "tweets": [tweet.to_dict() for tweet in self.tweets],
        }
        
        # Convert to pandas DataFrames and upload to BigQuery
        for entity, data in track(
            entities_data.items(), description="📤 Uploading data to BigQuery..."
        ):
            if data:
                # Convert to DataFrame
                df = pd.DataFrame(data)
                
                # Define the BigQuery table name
                table_id = f"{self.dataset_id}.{entity}"
                
                # Upload to BigQuery
                try:
                    print(f"Uploading {len(df)} rows to {table_id}...")
                    pandas_gbq.to_gbq(
                        df,
                        table_id,
                        project_id=self.project_id,
                        if_exists=self.if_exists
                    )
                    print(f"✓ Successfully uploaded {entity} to BigQuery")
                except Exception as e:
                    print(f"✗ Error uploading {entity} to BigQuery: {str(e)}")
                
                # Optional: Save to local CSV
                if save_local_csv:
                    if not os.path.exists("./jaffle-data"):
                        os.makedirs("./jaffle-data")
                    file = f"./jaffle-data/{entity}.csv"
                    df.to_csv(file, index=False)
                    print(f"✓ Also saved {entity} to {file}")
    
    def get_dataframes(self) -> dict[str, pd.DataFrame]:
        """
        Return all data as pandas DataFrames without saving to BigQuery or CSV.
        
        Returns:
            A dictionary of DataFrames for each entity type
        """
        stock: Stock = Stock()
        inventory: Inventory = Inventory()
        
        # Create dictionaries for each entity
        entities_data: dict[str, list[dict[str, Any]]] = {
            "customers": [customer.to_dict() for customer in self.customers.values()],
            "orders": [order.to_dict() for order in self.orders],
            "items": [item.to_dict() for order in self.orders for item in order.items],
            "stores": [market.store.to_dict() for market in self.markets],
            "supplies": stock.to_dict(),
            "products": inventory.to_dict(),
            "tweets": [tweet.to_dict() for tweet in self.tweets],
        }
        
        # Convert to DataFrames
        return {entity: pd.DataFrame(data) if data else pd.DataFrame() 
                for entity, data in entities_data.items()}