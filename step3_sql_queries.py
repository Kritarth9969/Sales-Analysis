# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

"""
STEP 3 - SQL QUERIES (SQLite-compatible)
Superstore Sales Dataset
"""

import sqlite3
import pandas as pd

print("=" * 60)
print("STEP 3: SQL QUERIES")
print("=" * 60)

df = pd.read_csv("cleaned_sales.csv", parse_dates=["Order Date", "Ship Date"])
df["Order Date Str"] = df["Order Date"].dt.strftime("%Y-%m-%d")

conn = sqlite3.connect("superstore.db")
df.to_sql("sales", conn, if_exists="replace", index=False)
print(f"\n[OK] Data loaded into SQLite (superstore.db) - 'sales' table")
print(f"  Total rows: {len(df):,}")

SEP = "-" * 55

def run_query(title, sql):
    """Execute a SQL query, print results, return a DataFrame."""
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)
    print(f"SQL:\n{sql}\n")
    result = pd.read_sql_query(sql, conn)
    print(result.to_string(index=False))
    return result

# Query 1: Total Sales and Profit by Region
run_query(
    "QUERY 1: Total Sales & Profit by Region",
    """
    SELECT
        Region,
        ROUND(SUM(Sales), 2)                   AS Total_Sales,
        ROUND(SUM(Profit), 2)                  AS Total_Profit,
        ROUND(SUM(Profit)/SUM(Sales)*100, 2)   AS Profit_Margin_Pct,
        COUNT(*)                               AS Order_Count
    FROM sales
    GROUP BY Region
    ORDER BY Total_Sales DESC;
    """
)

# Query 2: Monthly Sales Trend by Year and Month
run_query(
    "QUERY 2: Monthly Sales Trend (Year x Month)",
    """
    SELECT
        "Order Year"                   AS Year,
        "Order Month"                  AS Month,
        ROUND(SUM(Sales), 2)           AS Monthly_Sales,
        ROUND(SUM(Profit), 2)          AS Monthly_Profit,
        COUNT(*)                       AS Orders
    FROM sales
    GROUP BY "Order Year", "Order Month"
    ORDER BY Year, Month;
    """
)

# Query 3: Top 5 Products by Profit
run_query(
    "QUERY 3: Top 5 Products by Profit",
    """
    SELECT
        "Product Name",
        ROUND(SUM(Sales), 2)                   AS Total_Sales,
        ROUND(SUM(Profit), 2)                  AS Total_Profit,
        ROUND(SUM(Profit)/SUM(Sales)*100, 2)   AS Profit_Margin_Pct
    FROM sales
    GROUP BY "Product Name"
    ORDER BY Total_Profit DESC
    LIMIT 5;
    """
)

# Query 4: Discount Impact per Category
run_query(
    "QUERY 4: Discount Impact - Avg Discount vs Avg Profit per Category",
    """
    SELECT
        Category,
        ROUND(AVG(Discount), 4)                                        AS Avg_Discount,
        ROUND(AVG(Profit), 2)                                          AS Avg_Profit,
        ROUND(SUM(CASE WHEN Discount > 0 THEN 1 ELSE 0 END)*100.0
              / COUNT(*), 1)                                           AS Pct_Discounted_Orders,
        ROUND(AVG(CASE WHEN Discount = 0 THEN Profit END), 2)          AS Avg_Profit_No_Discount,
        ROUND(AVG(CASE WHEN Discount > 0 THEN Profit END), 2)          AS Avg_Profit_With_Discount
    FROM sales
    GROUP BY Category
    ORDER BY Avg_Discount DESC;
    """
)

# Bonus: Bottom 5 Sub-Categories
run_query(
    "BONUS: Bottom 5 Sub-Categories by Profit (loss leaders)",
    """
    SELECT
        Category,
        "Sub-Category",
        ROUND(SUM(Sales), 2)    AS Total_Sales,
        ROUND(SUM(Profit), 2)   AS Total_Profit,
        ROUND(AVG(Discount), 3) AS Avg_Discount
    FROM sales
    GROUP BY Category, "Sub-Category"
    ORDER BY Total_Profit ASC
    LIMIT 5;
    """
)

conn.close()
print("\n[DONE] All SQL queries executed successfully!")
print("=" * 60)
