# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

"""
=============================================================
STEP 1 - DATA CLEANING
Superstore Sales Dataset
=============================================================
"""

import pandas as pd
import numpy as np
import os

# -- 1. Load the dataset -------------------------------------------
print("=" * 60)
print("STEP 1: DATA CLEANING")
print("=" * 60)

try:
    df = pd.read_csv("Sample - Superstore.csv", encoding="latin-1")
    print("Dataset loaded from file.")
except FileNotFoundError:
    print("Local file not found - generating synthetic Superstore data...")

    np.random.seed(42)
    n = 9994

    categories = {
        "Furniture":       ["Bookcases", "Chairs", "Furnishings", "Tables"],
        "Office Supplies": ["Appliances", "Art", "Binders", "Envelopes",
                            "Fasteners", "Labels", "Paper", "Storage", "Supplies"],
        "Technology":      ["Accessories", "Copiers", "Machines", "Phones"],
    }
    regions  = ["East", "West", "Central", "South"]
    segments = ["Consumer", "Corporate", "Home Office"]
    states   = {
        "East":    ["New York", "Pennsylvania", "Ohio", "Virginia", "Massachusetts"],
        "West":    ["California", "Washington", "Oregon", "Nevada", "Colorado"],
        "Central": ["Illinois", "Texas", "Michigan", "Indiana", "Wisconsin"],
        "South":   ["Florida", "North Carolina", "Georgia", "Tennessee", "Alabama"],
    }

    rows = []
    order_num = 1
    base_date = pd.Timestamp("2014-01-01")

    for _ in range(n):
        region   = np.random.choice(regions)
        state    = np.random.choice(states[region])
        segment  = np.random.choice(segments)
        cat      = np.random.choice(list(categories.keys()))
        subcat   = np.random.choice(categories[cat])
        order_date = base_date + pd.Timedelta(days=int(np.random.randint(0, 1461)))
        ship_date  = order_date + pd.Timedelta(days=int(np.random.randint(1, 8)))
        sales    = round(np.random.lognormal(4.5, 1.2), 2)
        qty      = int(np.random.randint(1, 14))
        discount = round(np.random.choice(
            [0, 0.1, 0.2, 0.3, 0.4, 0.5],
            p=[0.5, 0.15, 0.15, 0.1, 0.05, 0.05]
        ), 2)
        margin = np.random.uniform(0.05, 0.45) - discount * 0.8
        profit = round(sales * margin, 2)
        product_name = f"{subcat} Model-{np.random.randint(100, 999)}"
        rows.append({
            "Row ID":       order_num,
            "Order ID":     f"CA-{order_date.year}-{order_num:05d}",
            "Order Date":   order_date.strftime("%d/%m/%Y"),
            "Ship Date":    ship_date.strftime("%d/%m/%Y"),
            "Ship Mode":    np.random.choice(["Second Class","Standard Class","First Class","Same Day"]),
            "Customer ID":  f"CUST-{np.random.randint(1000,9999)}",
            "Customer Name":f"Customer {np.random.randint(1,800)}",
            "Segment":      segment,
            "Country":      "United States",
            "City":         state + " City",
            "State":        state,
            "Postal Code":  str(np.random.randint(10000, 99999)),
            "Region":       region,
            "Product ID":   f"PROD-{np.random.randint(1000,9999)}",
            "Category":     cat,
            "Sub-Category": subcat,
            "Product Name": product_name,
            "Sales":        sales,
            "Quantity":     qty,
            "Discount":     discount,
            "Profit":       profit,
        })
        order_num += 1

    df = pd.DataFrame(rows)
    df.to_csv("Sample - Superstore.csv", index=False)
    print("Synthetic dataset created and saved.")

# -- 2. Inspect the dataset ----------------------------------------
print("\n[ Shape ]")
print(f"  Rows: {df.shape[0]:,}  |  Columns: {df.shape[1]}")

print("\n[ Column Data Types ]")
print(df.dtypes.to_string())

print("\n[ Missing Values ]")
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_summary = pd.DataFrame({"count": missing, "pct_%": missing_pct})
if missing_summary["count"].sum() > 0:
    print(missing_summary[missing_summary["count"] > 0].to_string())
else:
    print("  No missing values found [OK]")

print(f"\n[ Duplicate Rows ]: {df.duplicated().sum():,}")

print("\n[ Sample Records ]")
print(df.head(3).to_string())

# -- 3. Convert date columns ---------------------------------------
for fmt in ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", None]:
    try:
        df["Order Date"] = pd.to_datetime(df["Order Date"], format=fmt, dayfirst=True)
        df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  format=fmt, dayfirst=True)
        print(f"\n[ Date Conversion ] Parsed using format: {fmt or 'auto'} [OK]")
        break
    except Exception:
        continue

# -- 4. Extract temporal features ----------------------------------
df["Order Month"]   = df["Order Date"].dt.month
df["Order Year"]    = df["Order Date"].dt.year
df["Order Quarter"] = df["Order Date"].dt.quarter
df["Month Name"]    = df["Order Date"].dt.strftime("%b")
df["Year-Month"]    = df["Order Date"].dt.to_period("M").astype(str)

print("\n[ Temporal Features Extracted ]")
print(df[["Order Date", "Order Month", "Order Year",
          "Order Quarter", "Month Name", "Year-Month"]].head(4).to_string())

# -- 5. Handle missing values --------------------------------------
if "Postal Code" in df.columns:
    df["Postal Code"].fillna(0, inplace=True)

for col in ["Sales", "Profit", "Quantity", "Discount"]:
    if col in df.columns and df[col].isnull().sum() > 0:
        df[col].fillna(df[col].median(), inplace=True)

before = len(df)
df.dropna(how="all", inplace=True)
print(f"\n[ Null Handling ] Removed {before - len(df)} fully-null rows.")

# -- 6. Remove duplicates ------------------------------------------
before = len(df)
df.drop_duplicates(inplace=True)
print(f"[ Deduplication ] Removed {before - len(df)} duplicate rows.")

# -- 7. Add derived columns ----------------------------------------
df["Profit Margin %"]  = ((df["Profit"] / df["Sales"]) * 100).round(2)
df["Revenue per Unit"] = (df["Sales"] / df["Quantity"]).round(2)

# -- 8. Final inspection -------------------------------------------
print(f"\n[ Final Shape ] Rows: {len(df):,}  |  Columns: {df.shape[1]}")
print("\n[ Descriptive Statistics ]")
print(df[["Sales", "Profit", "Quantity", "Discount", "Profit Margin %"]].describe().round(2).to_string())

# -- 9. Save cleaned data ------------------------------------------
df.to_csv("cleaned_sales.csv", index=False)
print("\n[DONE] cleaned_sales.csv saved successfully!")
print("=" * 60)
