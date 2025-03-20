from google.cloud import bigquery

SCHEMAS = {
    "customers": [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE")
    ],
    "items": [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("order_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("sku", "STRING", mode="NULLABLE")
    ],
    "orders": [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("customer", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("ordered_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("store_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("subtotal", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("tax_paid", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("order_total", "INT64", mode="NULLABLE")
    ],
    "products": [
        bigquery.SchemaField("sku", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("price", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("description", "STRING", mode="NULLABLE")
    ],
    "stores": [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("opened_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("tax_rate", "FLOAT64", mode="NULLABLE")
    ],
    "supplies": [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("cost", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("perishable", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("sku", "STRING", mode="NULLABLE")
    ],
    "tweets": [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("tweeted_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("content", "STRING", mode="NULLABLE")
    ]
}

def get_table_schema(table_name):
    """
    Get the schema for a specific table.
    
    Args:
        table_name (str): Name of the table to get schema for
        
    Returns:
        list: List of bigquery.SchemaField objects defining the table schema
    """
    
    return SCHEMAS.get(table_name, []) 