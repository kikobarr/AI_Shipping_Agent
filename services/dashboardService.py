import pandas as pd

def load_and_clean_data(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    amount_cols = ['Goods (Amt)', 'Services (Amt)', 'Construction (Amt)', 'IT (Amt)']
    for col in amount_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def split_by_category(df):
    return {
        'goods': df[df['Goods (Amt)'].notna() & df['Goods (Amt)'] != 0],
        'services': df[df['Services (Amt)'].notna() & df['Services (Amt)'] != 0],
        'construction': df[df['Construction (Amt)'].notna() & df['Construction (Amt)'] != 0],
        'it': df[df['IT (Amt)'].notna() & df['IT (Amt)'] != 0],
    }