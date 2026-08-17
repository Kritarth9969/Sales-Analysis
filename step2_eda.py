# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

"""
STEP 2 - EXPLORATORY DATA ANALYSIS
Superstore Sales Dataset
"""

import pandas as pd
import numpy as np

print("=" * 60)
print("STEP 2: EXPLORATORY DATA ANALYSIS")
print("=" * 60)

df = pd.read_csv("cleaned_sales.csv", parse_dates=["Order Date", "Ship Date"])

if "Order Year" not in df.columns:
    df["Order Month"]     = df["Order Date"].dt.month
    df["Order Year"]      = df["Order Date"].dt.year
    df["Order Quarter"]   = df["Order Date"].dt.quarter
    df["Year-Month"]      = df["Order Date"].dt.to_period("M").astype(str)
    df["Profit Margin %"] = ((df["Profit"] / df["Sales"]) * 100).round(2)

SEP = "-" * 50

# Q1: Monthly and Yearly Sales Trends
print("\n" + SEP)
print("Q1: MONTHLY & YEARLY SALES TRENDS")
print(SEP)

yearly = df.groupby("Order Year")["Sales"].sum().reset_index()
yearly.columns = ["Year", "Total Sales"]
yearly["Total Sales"] = yearly["Total Sales"].round(2)
yearly["YoY Growth %"] = yearly["Total Sales"].pct_change().mul(100).round(2)
print("\n  Yearly Sales:")
print(yearly.to_string(index=False))

monthly = df.groupby("Order Month")["Sales"].sum().reset_index()
monthly.columns = ["Month", "Total Sales"]
month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
             7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
monthly["Month Name"] = monthly["Month"].map(month_map)
print("\n  Monthly Sales (all years combined):")
print(monthly[["Month Name", "Total Sales"]].to_string(index=False))

ym_trend = df.groupby("Year-Month")["Sales"].sum().reset_index()
ym_trend.columns = ["Year-Month", "Sales"]
ym_trend = ym_trend.sort_values("Year-Month")
print(f"\n  Year-Month trend: {len(ym_trend)} data points from "
      f"{ym_trend['Year-Month'].iloc[0]} to {ym_trend['Year-Month'].iloc[-1]}")

# Q2: Top 10 Best-Selling Products
print("\n" + SEP)
print("Q2: TOP 10 BEST-SELLING PRODUCTS BY REVENUE")
print(SEP)

top10_products = (
    df.groupby("Product Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
top10_products.columns = ["Product Name", "Total Sales"]
top10_products["Total Sales"] = top10_products["Total Sales"].round(2)
top10_products.index = top10_products.index + 1
print(top10_products.to_string())

# Q3: Profit Margin by Category and Sub-Category
print("\n" + SEP)
print("Q3: PROFIT MARGIN BY CATEGORY & SUB-CATEGORY")
print(SEP)

cat_margin = df.groupby("Category").agg(
    Total_Sales=("Sales", "sum"),
    Total_Profit=("Profit", "sum")
).reset_index()
cat_margin["Profit Margin %"] = (cat_margin["Total_Profit"] / cat_margin["Total_Sales"] * 100).round(2)
print("\n  By Category:")
print(cat_margin.to_string(index=False))

subcat_margin = df.groupby(["Category", "Sub-Category"]).agg(
    Total_Sales=("Sales", "sum"),
    Total_Profit=("Profit", "sum")
).reset_index()
subcat_margin["Profit Margin %"] = (subcat_margin["Total_Profit"] / subcat_margin["Total_Sales"] * 100).round(2)
subcat_margin = subcat_margin.sort_values("Profit Margin %", ascending=False)
print("\n  By Sub-Category (sorted by Profit Margin %):")
print(subcat_margin.to_string(index=False))

# Q4: Regional Performance
print("\n" + SEP)
print("Q4: REGIONAL PERFORMANCE - SALES vs PROFIT")
print(SEP)

regional = df.groupby("Region").agg(
    Total_Sales=("Sales", "sum"),
    Total_Profit=("Profit", "sum"),
    Orders=("Order ID" if "Order ID" in df.columns else "Sales", "count")
).reset_index()
regional["Profit Margin %"] = (regional["Total_Profit"] / regional["Total_Sales"] * 100).round(2)
regional = regional.sort_values("Total_Sales", ascending=False)
print(regional.to_string(index=False))

best_sales  = regional.iloc[0]["Region"]
best_profit = regional.sort_values("Total_Profit", ascending=False).iloc[0]["Region"]
print(f"\n  Best region by Sales:  {best_sales}")
print(f"  Best region by Profit: {best_profit}")

# Q5: Segment Revenue
print("\n" + SEP)
print("Q5: CUSTOMER SEGMENT REVENUE BREAKDOWN")
print(SEP)

segment = df.groupby("Segment").agg(
    Total_Sales=("Sales", "sum"),
    Total_Profit=("Profit", "sum"),
    Orders=("Sales", "count")
).reset_index()
segment["Revenue Share %"]  = (segment["Total_Sales"] / segment["Total_Sales"].sum() * 100).round(2)
segment["Profit Margin %"]  = (segment["Total_Profit"] / segment["Total_Sales"] * 100).round(2)
segment = segment.sort_values("Total_Sales", ascending=False)
print(segment.to_string(index=False))
print(f"\n  Top segment by revenue: {segment.iloc[0]['Segment']}")

print("\n[DONE] EDA complete!")
print("=" * 60)

# Save summaries
yearly.to_csv("out_yearly_sales.csv", index=False)
ym_trend.to_csv("out_monthly_trend.csv", index=False)
top10_products.to_csv("out_top10_products.csv", index=False)
subcat_margin.to_csv("out_subcat_margin.csv", index=False)
regional.to_csv("out_regional.csv", index=False)
segment.to_csv("out_segment.csv", index=False)
print("Summary CSVs saved.")
