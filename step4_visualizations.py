"""
STEP 4 — VISUALIZATIONS (Matplotlib / Seaborn)
Outputs: 5 PNG charts saved to ./charts/
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import os

os.makedirs("charts", exist_ok=True)
df = pd.read_csv("cleaned_sales.csv", parse_dates=["Order Date", "Ship Date"])

if "Order Year" not in df.columns:
    df["Order Year"]  = df["Order Date"].dt.year
    df["Order Month"] = df["Order Date"].dt.month
    df["Year-Month"]  = df["Order Date"].dt.to_period("M").astype(str)
if "Profit Margin %" not in df.columns:
    df["Profit Margin %"] = (df["Profit"] / df["Sales"] * 100).round(2)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
    "figure.dpi": 150,
})
BG = "#F8F9FA"

print("Generating charts...")

# Chart 1: Monthly Sales Trend
ym = df.groupby("Year-Month")["Sales"].sum().reset_index().sort_values("Year-Month")
ym_vals = ym["Sales"].values / 1000

fig, ax = plt.subplots(figsize=(14, 5), facecolor=BG)
ax.set_facecolor(BG)
ax.plot(range(len(ym)), ym_vals, color="#4361EE", lw=2.5, marker="o", markersize=4, markevery=3)
ax.fill_between(range(len(ym)), ym_vals, alpha=0.15, color="#4361EE")
for yr in [2015, 2016, 2017]:
    idxs = [i for i, v in enumerate(ym["Year-Month"]) if v.startswith(str(yr))]
    if idxs:
        ax.axvline(idxs[0], color="#888", lw=1, ls=":")
        ax.text(idxs[0]+0.2, max(ym_vals)*0.95, str(yr), color="#888", fontsize=9)
tick_idx = list(range(0, len(ym), 4))
ax.set_xticks(tick_idx)
ax.set_xticklabels([ym["Year-Month"].iloc[i] for i in tick_idx], rotation=45, ha="right", fontsize=8)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x:.0f}K"))
ax.set_title("Monthly Sales Trend (2014–2017)", fontsize=15, fontweight="bold", pad=12)
ax.set_xlabel("Month"); ax.set_ylabel("Sales (USD thousands)")
plt.tight_layout()
plt.savefig("charts/chart1_monthly_sales_trend.png", bbox_inches="tight")
plt.close()
print("1/5 chart1_monthly_sales_trend.png saved")

# Chart 2: Top 10 Products
top10 = df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False).head(10).reset_index()
top10.columns = ["Product", "Sales"]
top10["Product"] = top10["Product"].str[:35]
colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(top10)))[::-1]

fig, ax = plt.subplots(figsize=(12, 6), facecolor=BG)
ax.set_facecolor(BG)
bars = ax.barh(top10["Product"], top10["Sales"]/1000, color=colors, edgecolor="white")
for bar in bars:
    w = bar.get_width()
    ax.text(w+0.3, bar.get_y()+bar.get_height()/2, f"${w:.1f}K", va="center", fontsize=8)
ax.set_xlabel("Total Sales (USD thousands)")
ax.set_title("Top 10 Best-Selling Products by Revenue", fontsize=15, fontweight="bold", pad=12)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x,_: f"${x:.0f}K"))
ax.invert_yaxis()
plt.tight_layout()
plt.savefig("charts/chart2_top10_products.png", bbox_inches="tight")
plt.close()
print("2/5 chart2_top10_products.png saved")

# Chart 3: Sales vs Profit by Region
reg = df.groupby("Region").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
reg = reg.sort_values("Sales", ascending=False)
x = np.arange(len(reg)); w = 0.38

fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG)
ax.set_facecolor(BG)
b1 = ax.bar(x-w/2, reg["Sales"]/1e6,  width=w, color="#4361EE", label="Sales",  edgecolor="white")
b2 = ax.bar(x+w/2, reg["Profit"]/1e6, width=w, color="#F72585", label="Profit", edgecolor="white")
for b in list(b1)+list(b2):
    h = b.get_height()
    ax.text(b.get_x()+b.get_width()/2, h+0.005, f"${h:.2f}M", ha="center", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(reg["Region"], fontsize=11)
ax.set_ylabel("Amount (USD millions)")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,_: f"${x:.1f}M"))
ax.set_title("Sales vs Profit by Region", fontsize=15, fontweight="bold", pad=12)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("charts/chart3_sales_profit_region.png", bbox_inches="tight")
plt.close()
print("3/5 chart3_sales_profit_region.png saved")

# Chart 4: Heatmap — Profit Margin by Sub-Category
pivot = df.pivot_table(values="Profit Margin %", index="Sub-Category", columns="Category", aggfunc="mean").round(1)

fig, ax = plt.subplots(figsize=(9, max(6, len(pivot)*0.55)), facecolor=BG)
ax.set_facecolor(BG)
sns.heatmap(pivot, ax=ax, annot=True, fmt=".1f", cmap="RdYlGn", center=0,
            linewidths=0.5, linecolor="#DDD", annot_kws={"fontsize":9},
            cbar_kws={"label":"Profit Margin %","shrink":0.8})
ax.set_title("Profit Margin % by Sub-Category & Category", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Category"); ax.set_ylabel("Sub-Category")
plt.tight_layout()
plt.savefig("charts/chart4_profit_margin_heatmap.png", bbox_inches="tight")
plt.close()
print("4/5 chart4_profit_margin_heatmap.png saved")

# Chart 5: Pie — Sales by Segment
seg = df.groupby("Segment")["Sales"].sum()
colors_pie = ["#4361EE","#F72585","#4CC9F0"]

fig, ax = plt.subplots(figsize=(8, 6), facecolor=BG)
ax.set_facecolor(BG)
wedges, texts, autotexts = ax.pie(seg, labels=seg.index, autopct="%1.1f%%",
    colors=colors_pie, explode=[0.04]*len(seg), startangle=140,
    wedgeprops={"edgecolor":"white","linewidth":2}, textprops={"fontsize":11})
for at in autotexts:
    at.set_fontsize(10); at.set_fontweight("bold")
ax.set_title("Sales Distribution by Customer Segment", fontsize=15, fontweight="bold", pad=16)
legend_labels = [f"{s}: ${v/1e6:.2f}M" for s,v in zip(seg.index, seg)]
ax.legend(wedges, legend_labels, loc="lower right", fontsize=9)
plt.tight_layout()
plt.savefig("charts/chart5_sales_share_segment.png", bbox_inches="tight")
plt.close()
print("5/5 chart5_sales_share_segment.png saved")
print("All 5 charts saved to ./charts/")
