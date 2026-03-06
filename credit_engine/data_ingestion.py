"""Data ingestion from Databricks"""
from databricks import sql
from typing import Dict, Any
import pandas as pd
from .config import DATABRICKS_CONFIG

class DataIngestion:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        self.connection = sql.connect(
            server_hostname=DATABRICKS_CONFIG["host"],
            http_path=f"/sql/1.0/warehouses/{DATABRICKS_CONFIG['warehouse_id']}",
            access_token=DATABRICKS_CONFIG["token"]
        )
    
    def fetch_applicant_data(self, applicant_id: str) -> Dict[str, Any]:
        """Fetch primary applicant data"""
        query = f"""
        SELECT * FROM credit_applications 
        WHERE applicant_id = '{applicant_id}'
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description]).to_dict('records')[0]
    
    def fetch_financial_data(self, applicant_id: str) -> pd.DataFrame:
        """Fetch financial statements and ratios"""
        query = f"""
        SELECT * FROM financial_statements 
        WHERE applicant_id = '{applicant_id}'
        ORDER BY statement_date DESC
        """
        return pd.read_sql(query, self.connection)
    
    def fetch_credit_history(self, applicant_id: str) -> pd.DataFrame:
        """Fetch credit bureau data"""
        query = f"""
        SELECT * FROM credit_bureau_data 
        WHERE applicant_id = '{applicant_id}'
        """
        return pd.read_sql(query, self.connection)
    
    def close(self):
        if self.connection:
            self.connection.close()
