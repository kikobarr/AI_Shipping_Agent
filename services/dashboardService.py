# import pandas as pd
# import os

# CSV_PATH = "slo-data/data.csv"

# def save_uploaded_file(uploaded_file):
#     """Save uploaded file as CSV, even if originally .xlsx"""
#     os.makedirs("slo-data", exist_ok=True)
#     if uploaded_file.name.endswith(".xlsx"):
#         df = pd.read_excel(uploaded_file)
#         df.to_csv(CSV_PATH, index=False)
#     elif uploaded_file.name.endswith(".csv"):
#         with open(CSV_PATH, "wb") as f:
#             f.write(uploaded_file.getbuffer())
#     else:
#         raise ValueError("Only .csv and .xlsx files are supported.")

# def load_and_clean_data():
#     """Load and clean from converted CSV"""
#     if not os.path.exists(CSV_PATH):
#         raise FileNotFoundError("No uploaded file found.")

#     df = pd.read_csv(CSV_PATH)

#     # Fix column naming consistency
#     df["Supplier Type"] = df["Supplier Type"].replace("DVB", "DVBE")
#     df["PO Date"] = pd.to_datetime(df["PO Date"], errors='coerce')

#     amount_cols = ['Goods (Amt)', 'Services (Amt)', 'Construction (Amt)', 'IT (Amt)']
#     for col in amount_cols:
#         df[col] = pd.to_numeric(df[col], errors='coerce')

#     df["Total Spend"] = df[amount_cols].sum(axis=1)

#     return df

# def split_by_category(df):
#     return {
#         'goods': df[df['Goods (Amt)'].notna() & df['Goods (Amt)'] != 0],
#         'services': df[df['Services (Amt)'].notna() & df['Services (Amt)'] != 0],
#         'construction': df[df['Construction (Amt)'].notna() & df['Construction (Amt)'] != 0],
#         'it': df[df['IT (Amt)'].notna() & df['IT (Amt)'] != 0],
#     }

# def summarize_by_supplier_type(df):
#     df["Supplier Type"] = df["Supplier Type"].fillna("None")  # Handle missing types
#     summary = df.groupby("Supplier Type").agg(
#         Total_Suppliers=("Supplier Name", "nunique"),
#         Total_Spend=("Total Spend", "sum")
#     ).reset_index()

#     total_spend = df["Total Spend"].sum()
#     summary["Percent of Total"] = (summary["Total_Spend"] / total_spend) * 100
#     summary["Total_Spend"] = summary["Total_Spend"].round(2)
#     summary["Percent of Total"] = summary["Percent of Total"].round(2)

#     return summary

# def melt_category_spend(df):
#     spend_cols = ['Goods (Amt)', 'Services (Amt)', 'Construction (Amt)', 'IT (Amt)']
#     df["Supplier Type"] = df["Supplier Type"].fillna("None")  # Handle missing types
#     melted = df.melt(id_vars=["Supplier Type"], value_vars=spend_cols, 
#                      var_name="Category", value_name="Amount")
#     melted["Amount"] = pd.to_numeric(melted["Amount"], errors="coerce")
#     melted.dropna(subset=["Amount"], inplace=True)
#     return melted
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