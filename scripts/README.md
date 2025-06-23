### Dataset and tables initialization
```bash
cd tables
python create_tables.py
```

### Generate initial load of data
```bash
cd data_generation
python run_bigquery_simulation.py --project-id prj-data-sds-lz-prd-411a --dataset-id bqdts_company_lz 
```

### Generate new data for orders and tweets
```bash
cd data_generation
python run_bigquery_simulation.py --project-id prj-data-sds-lz-dev-4542 --dataset-id bqdts_company_lz --new-data
```