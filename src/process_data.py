import pandas as pd
import numpy as np
import os

def load_and_merge_data(raw_data_path):
    """Load and merge the two datasets."""
    print("Loading datasets...")
    df09 = pd.read_csv(os.path.join(raw_data_path, '2009-2010.csv'), encoding='ISO-8859-1', sep=';', decimal=',')
    df10 = pd.read_csv(os.path.join(raw_data_path, '2010-2011.csv'), encoding='ISO-8859-1', sep=';', decimal=',')
    
    print(f"2009-2010 shape: {df09.shape}")
    print(f"2010-2011 shape: {df10.shape}")
    
    df = pd.concat([df09, df10], ignore_index=True)
    print(f"Merged shape: {df.shape}")
    return df

def clean_data(df):
    """Clean the dataset according to requirements."""
    print("Cleaning data...")
    
    df.columns = df.columns.str.replace('ï»¿', '')  # Remove BOM character
    
    # 1. Remove rows with missing Customer ID
    initial_rows = len(df)
    df = df.dropna(subset=['Customer ID'])
    print(f"Dropped {initial_rows - len(df)} rows with missing Customer ID")
    
    # 2. Convert Customer ID to integer
    df['Customer ID'] = df['Customer ID'].astype(int)
    
    # 3. Convert InvoiceDate to datetime
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], dayfirst=True)

   
    
    # 4. Handle Cancellations (InvoiceNo starts with 'C')
    # We keep them for now but flag them, or handle as per specific logic.
    # The requirement says "Nettoyage : annulations (InvoiceNo 'C')... détection/traitement outliers"
    # Usually for sales analysis we might want to exclude them OR net them out.
    # For now, let's create a 'Quantity' that is negative for cancellations if not already?
    # In this dataset, 'C' invoices usually have negative quantity.
    # Let's verify if 'C' implies negative quantity.
    
    # 5. Remove outliers / invalid data
    # Remove records with Price < 0 (Adjust bad debt etc)
    df = df[df['Price'] >= 0]
    
    # Calculate TotalAmount
    df['TotalAmount'] = df['Quantity'] * df['Price']
    
    return df

def main():
    raw_path = 'data/raw'
    processed_path = 'data/processed'
    
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)
        
    df = load_and_merge_data(raw_path)
    df = clean_data(df)
    
    output_file = os.path.join(processed_path, 'online_retail_cleaned.csv')
    print(f"Saving cleaned data to {output_file}...")
    df.to_csv(output_file, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
