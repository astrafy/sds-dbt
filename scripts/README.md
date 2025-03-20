### Dataset and tables initialization
```bash
cd tables
python create_tables.py
```

### Generate initial load of data
```bash
cd data_generation
python run_bigquery_simulation.py --project-id prj-data-fulll-lz-dev-1c8b --dataset-id bqdts_company_lz 
```

### Generate new data for orders and tweets
```bash
cd data_generation
python run_bigquery_simulation.py --project-id prj-data-fulll-lz-dev-1c8b --dataset-id bqdts_company_lz --new-data
```