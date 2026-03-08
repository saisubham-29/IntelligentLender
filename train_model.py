#!/usr/bin/env python3
"""Train ML model from CSV data"""
import sys
import os
from credit_engine.ml_model import CreditDecisionModel
from credit_engine.csv_handler import CSVDataHandler

def train_model(csv_path: str):
    """Train model from CSV file"""
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return False
    
    print("="*60)
    print("🤖 TRAINING CREDIT DECISION MODEL")
    print("="*60)
    print(f"\n📂 Loading data from: {csv_path}\n")
    
    try:
        # Initialize model
        model = CreditDecisionModel()
        
        # Train from CSV
        handler = model.train_from_csv(csv_path)
        
        # Save model
        import joblib
        model_path = 'credit_engine/trained_model.pkl'
        handler_path = 'credit_engine/csv_handler.pkl'
        
        joblib.dump(model, model_path)
        joblib.dump(handler, handler_path)
        
        print(f"\n✓ Model saved to: {model_path}")
        print(f"✓ Handler saved to: {handler_path}")
        
        print("\n" + "="*60)
        print("✅ TRAINING COMPLETE")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_data():
    """Create sample CSV for testing"""
    handler = CSVDataHandler()
    csv_path = handler.create_sample_csv()
    print(f"\n✓ Sample CSV created: {csv_path}")
    print("\nSample format:")
    import pandas as pd
    df = pd.read_csv(csv_path)
    print(df.head())
    return csv_path

if __name__ == '__main__':
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        train_model(csv_path)
    else:
        print("Usage: python train_model.py <path_to_csv>")
        print("\nOr create sample data:")
        print("  python train_model.py --sample")
        
        if '--sample' in sys.argv or '-s' in sys.argv:
            csv_path = create_sample_data()
            print(f"\nNow train with: python train_model.py {csv_path}")
