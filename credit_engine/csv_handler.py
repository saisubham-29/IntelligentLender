"""CSV data handler for model training and optimization"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

class CSVDataHandler:
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        
    def load_training_data(self, csv_path: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Load and preprocess CSV training data"""
        df = pd.read_csv(csv_path)
        
        print(f"✓ Loaded {len(df)} records from CSV")
        print(f"✓ Columns: {list(df.columns)}")
        
        # Separate features and target
        if 'Target_Decision' in df.columns:
            X = df.drop('Target_Decision', axis=1)
            y = df['Target_Decision']
        else:
            raise ValueError("CSV must contain 'Target_Decision' column")
        
        # Preprocess features
        X_processed = self.preprocess_features(X)
        
        # Encode target (APPROVE=1, REJECT=0)
        y_encoded = y.map({'APPROVE': 1, 'APPROVED': 1, 'REJECT': 0, 'REJECTED': 0})
        
        return X_processed, y_encoded
    
    def preprocess_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess all features"""
        df = df.copy()
        
        # Numeric columns
        numeric_cols = [
            'Paid-up Capital', 'GSTR Variance %', 'ITC Availed', 
            'Audited Net Income', 'Inventory', 'Accounts Receivable',
            'EBITDA', 'Long-Term Debt', 'Cheque Bounces', 'NACH Returns',
            'OD Utilization', 'NACH Obligation %', 'CMR Rank',
            'Capacity Utilization', 'Promoter Experience', 
            'Contingent Liabilities', 'Shareholding Pledge', 'Risk Premium'
        ]
        
        # Categorical columns
        categorical_cols = [
            'Entity Status', 'Asset Classification', 'Wilful Defaulter',
            'Machinery Status', 'Auditor Qualifications'
        ]
        
        # Handle numeric columns
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Handle categorical columns
        for col in categorical_cols:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col].fillna('Unknown'))
                else:
                    df[col] = self.label_encoders[col].transform(df[col].fillna('Unknown'))
        
        # Handle date column
        if 'Date of Incorporation' in df.columns:
            df['Date of Incorporation'] = pd.to_datetime(df['Date of Incorporation'], errors='coerce')
            df['Company Age (Years)'] = (pd.Timestamp.now() - df['Date of Incorporation']).dt.days / 365.25
            df = df.drop('Date of Incorporation', axis=1)
        
        # Drop identifier columns
        id_cols = ['CIN', 'LLPIN', 'PAN', 'GSTIN']
        df = df.drop([col for col in id_cols if col in df.columns], axis=1)
        
        # Store feature columns
        self.feature_columns = df.columns.tolist()
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer additional features from CSV data"""
        df = df.copy()
        
        # Financial ratios
        if 'EBITDA' in df.columns and 'Long-Term Debt' in df.columns:
            df['Debt_to_EBITDA'] = df['Long-Term Debt'] / (df['EBITDA'] + 1)
        
        if 'Accounts Receivable' in df.columns and 'Audited Net Income' in df.columns:
            df['Receivables_to_Income'] = df['Accounts Receivable'] / (df['Audited Net Income'] + 1)
        
        if 'Inventory' in df.columns and 'Audited Net Income' in df.columns:
            df['Inventory_to_Income'] = df['Inventory'] / (df['Audited Net Income'] + 1)
        
        # Risk indicators
        if 'Cheque Bounces' in df.columns and 'NACH Returns' in df.columns:
            df['Total_Payment_Failures'] = df['Cheque Bounces'] + df['NACH Returns']
        
        if 'GSTR Variance %' in df.columns:
            df['High_GSTR_Variance'] = (df['GSTR Variance %'] > 10).astype(int)
        
        if 'Shareholding Pledge' in df.columns:
            df['High_Pledge_Risk'] = (df['Shareholding Pledge'] > 50).astype(int)
        
        # Operational efficiency
        if 'Capacity Utilization' in df.columns:
            df['Low_Capacity_Risk'] = (df['Capacity Utilization'] < 60).astype(int)
        
        return df
    
    def prepare_for_training(self, csv_path: str, test_size: float = 0.2) -> Dict:
        """Prepare complete training dataset"""
        # Load data
        X, y = self.load_training_data(csv_path)
        
        # Engineer features
        X = self.engineer_features(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = pd.DataFrame(
            self.scaler.fit_transform(X_train),
            columns=X_train.columns,
            index=X_train.index
        )
        
        X_test_scaled = pd.DataFrame(
            self.scaler.transform(X_test),
            columns=X_test.columns,
            index=X_test.index
        )
        
        print(f"\n✓ Training set: {len(X_train)} samples")
        print(f"✓ Test set: {len(X_test)} samples")
        print(f"✓ Features: {len(X_train.columns)}")
        print(f"✓ Approval rate: {y_train.mean()*100:.1f}%")
        
        return {
            'X_train': X_train_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train,
            'y_test': y_test,
            'feature_names': X_train.columns.tolist()
        }
    
    def transform_new_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform new data using fitted encoders and scaler"""
        df = self.preprocess_features(df)
        df = self.engineer_features(df)
        
        # Ensure same columns as training
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        df = df[self.feature_columns]
        
        # Scale
        df_scaled = pd.DataFrame(
            self.scaler.transform(df),
            columns=df.columns,
            index=df.index
        )
        
        return df_scaled
    
    def create_sample_csv(self, output_path: str = 'sample_training_data.csv'):
        """Create sample CSV with correct format"""
        sample_data = {
            'CIN': ['U12345MH2020PTC123456', 'U67890DL2018PTC789012'],
            'LLPIN': ['AAA-1234', 'BBB-5678'],
            'Entity Status': ['Active', 'Active'],
            'Date of Incorporation': ['2020-01-15', '2018-06-20'],
            'Paid-up Capital': [10000000, 5000000],
            'PAN': ['AABCU1234C', 'AABCU5678D'],
            'GSTIN': ['27AABCU1234C1Z5', '07AABCU5678D1Z9'],
            'GSTR Variance %': [5.2, 15.8],
            'ITC Availed': [500000, 300000],
            'Audited Net Income': [8000000, 3000000],
            'Inventory': [2000000, 1500000],
            'Accounts Receivable': [3000000, 2000000],
            'EBITDA': [12000000, 4000000],
            'Long-Term Debt': [15000000, 8000000],
            'Cheque Bounces': [0, 2],
            'NACH Returns': [0, 1],
            'OD Utilization': [45.5, 85.2],
            'NACH Obligation %': [30.0, 75.0],
            'CMR Rank': [2, 4],
            'Asset Classification': ['Standard', 'Sub-Standard'],
            'Wilful Defaulter': ['No', 'No'],
            'Capacity Utilization': [75.0, 55.0],
            'Machinery Status': ['Good', 'Average'],
            'Promoter Experience': [15, 8],
            'Contingent Liabilities': [500000, 1000000],
            'Auditor Qualifications': ['Unqualified', 'Qualified'],
            'Shareholding Pledge': [25.0, 65.0],
            'Risk Premium': [2.5, 5.0],
            'Target_Decision': ['APPROVE', 'REJECT']
        }
        
        df = pd.DataFrame(sample_data)
        df.to_csv(output_path, index=False)
        print(f"✓ Sample CSV created: {output_path}")
        return output_path
