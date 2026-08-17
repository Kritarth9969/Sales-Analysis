"""
=============================================================
STEP 5 — INTERACTIVE DASHBOARD (Plotly Dash)
Superstore Sales Dataset
Run: python step5_dashboard.py
Then open: http://127.0.0.1:8050
=============================================================
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

# ── Load data ──────────────────────────────────────────────
df = pd.read_csv("cleaned_sales.csv", parse_dates=["Order Date", "Ship Date"])

if "Order Year" not in df.columns:
    df["Order Year"]    = df["Order Date"].dt.year
    df["Order Month"]   = df["Order Date"].dt.month
    df["Order Quarter"] = df["Order Date"].dt.quarter
    df["Year-Month"]    = df["Order Date"].dt.to_period("M").astype(str)
if "Profit Margin %" not in df.columns:
    df["Profit Margin %"] = (df["Profit"] / df["Sales"] * 100).round(2)

# ── Constants ──────────────────────────────────────────────
REGIONS    = sorted(df["Region"].unique())
CATEGORIES = sorted(df["Category"].unique())
YEARS      = sorted(df["Order Year"].unique())

# Colour palette
C_BLUE   = "#4361EE"
C_PINK   = "#F72585"
C_PURPLE = "#7209B7"
C_CYAN   = "#4CC9F0"
C_ORANGE = "#F77F00"
BG       = "#F8FAFC"
CARD_BG  = "#FFFFFF"

# ── App setup ──────────────────────────────────────────────
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="Superstore Sales Dashboard",
    meta_tags=[{"name":"viewport","content":"width=device-width, initial-scale=1"}],
)
server = app.server   # expose Flask server if needed

# ── Helper: KPI Card ───────────────────────────────────────
def kpi_card(card_id, title, icon, color):
    return html.Div([
        html.Div([
            html.Span(icon, style={"fontSize":"28px"}),
            html.H4(title, style={"margin":"0","fontSize":"13px",
                                   "color":"#6B7280","fontWeight":"500"}),
        ], style={"display":"flex","alignItems":"center","gap":"10px","marginBottom":"8px"}),
        html.H2(id=card_id, style={"margin":"0","fontSize":"26px",
                                    "fontWeight":"700","color":color}),
    ], style={
        "background": CARD_BG,
        "borderRadius": "14px",
        "padding": "20px 24px",
        "boxShadow": "0 1px 6px rgba(0,0,0,0.08)",
        "borderLeft": f"4px solid {color}",
        "flex": "1",
        "minWidth": "200px",
    })

# ── Layout ─────────────────────────────────────────────────
app.layout = html.Div(style={"background": BG, "minHeight": "100vh",
                               "fontFamily": "'Inter', sans-serif"}, children=[

    # ── Google Fonts
    html.Link(rel="stylesheet",
              href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"),

    # ── Header ────────────────────────────────────────────
    html.Div([
        html.Div([
            html.H1("📊 Superstore Sales Dashboard",
                    style={"margin":"0","fontSize":"22px","fontWeight":"700","color":"#1E293B"}),
            html.P("Interactive analytics · 2014–2017",
                   style={"margin":"0","color":"#64748B","fontSize":"13px"}),
        ]),
        html.Div("Portfolio Project · Data Analysis",
                 style={"color":"#94A3B8","fontSize":"12px","alignSelf":"flex-end"}),
    ], style={
        "background": CARD_BG,
        "padding": "18px 32px",
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "center",
        "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
        "borderBottom": "1px solid #E2E8F0",
    }),

    # ── Main body ─────────────────────────────────────────
    html.Div(style={"display":"flex","gap":"0"}, children=[

        # ── Sidebar ───────────────────────────────────────
        html.Div([
            html.H3("Filters", style={"fontSize":"14px","fontWeight":"600",
                                       "color":"#374151","marginBottom":"20px",
                                       "textTransform":"uppercase","letterSpacing":"1px"}),
            html.Label("Region", style={"fontSize":"12px","color":"#6B7280","fontWeight":"500"}),
            dcc.Checklist(
                id="filter-region",
                options=[{"label":f" {r}","value":r} for r in REGIONS],
                value=REGIONS,
                style={"fontSize":"13px","color":"#374151","lineHeight":"1.9"},
                inputStyle={"accentColor": C_BLUE, "marginRight":"6px"},
            ),
            html.Hr(style={"margin":"16px 0","borderColor":"#E5E7EB"}),
            html.Label("Category", style={"fontSize":"12px","color":"#6B7280","fontWeight":"500"}),
            dcc.Checklist(
                id="filter-category",
                options=[{"label":f" {c}","value":c} for c in CATEGORIES],
                value=CATEGORIES,
                style={"fontSize":"13px","color":"#374151","lineHeight":"1.9"},
                inputStyle={"accentColor": C_BLUE, "marginRight":"6px"},
            ),
            html.Hr(style={"margin":"16px 0","borderColor":"#E5E7EB"}),
            html.Label("Year", style={"fontSize":"12px","color":"#6B7280","fontWeight":"500"}),
            dcc.Checklist(
                id="filter-year",
                options=[{"label":f" {int(y)}","value":y} for y in YEARS],
                value=YEARS,
                style={"fontSize":"13px","color":"#374151","lineHeight":"1.9"},
                inputStyle={"accentColor": C_BLUE, "marginRight":"6px"},
            ),
        ], style={
            "width": "200px",
            "minWidth": "200px",
            "background": CARD_BG,
            "padding": "24px 20px",
            "borderRight": "1px solid #E2E8F0",
            "minHeight": "calc(100vh - 70px)",
        }),

        # ── Content ───────────────────────────────────────
        html.Div([

            # KPI Row
            html.Div([
                kpi_card("kpi-sales",    "Total Sales",    "💰", C_BLUE),
                kpi_card("kpi-profit",   "Total Profit",   "📈", "#10B981"),
                kpi_card("kpi-margin",   "Profit Margin",  "🎯", C_PURPLE),
                kpi_card("kpi-orders",   "Total Orders",   "🛒", C_ORANGE),
            ], style={"display":"flex","gap":"16px","flexWrap":"wrap","marginBottom":"20px"}),

            # Tabs
            dcc.Tabs(id="tabs", value="tab1", children=[
                dcc.Tab(label="📈 Monthly Trend",    value="tab1",
                        style={"fontFamily":"Inter","fontSize":"13px"},
                        selected_style={"fontFamily":"Inter","fontSize":"13px",
                                        "borderTop":f"3px solid {C_BLUE}","fontWeight":"600"}),
                dcc.Tab(label="🏆 Top Products",     value="tab2",
                        style={"fontFamily":"Inter","fontSize":"13px"},
                        selected_style={"fontFamily":"Inter","fontSize":"13px",
                                        "borderTop":f"3px solid {C_PINK}","fontWeight":"600"}),
                dcc.Tab(label="🗺️ Regional Map",     value="tab3",
                        style={"fontFamily":"Inter","fontSize":"13px"},
                        selected_style={"fontFamily":"Inter","fontSize":"13px",
                                        "borderTop":f"3px solid {C_PURPLE}","fontWeight":"600"}),
                dcc.Tab(label="📊 Profit Analysis",  value="tab4",
                        style={"fontFamily":"Inter","fontSize":"13px"},
                        selected_style={"fontFamily":"Inter","fontSize":"13px",
                                        "borderTop":f"3px solid {C_ORANGE}","fontWeight":"600"}),
            ], style={"marginBottom":"16px"}),

            html.Div(id="tab-content"),

        ], style={"flex":"1","padding":"24px","overflow":"auto"}),
    ]),
])

# ── Filtered data helper ────────────────────────────────────
def filter_df(regions, categories, years):
    mask = (
        df["Region"].isin(regions) &
        df["Category"].isin(categories) &
        df["Order Year"].isin(years)
    )
    return df[mask]

# ── KPI Callbacks ───────────────────────────────────────────
@callback(
    Output("kpi-sales",  "children"),
    Output("kpi-profit", "children"),
    Output("kpi-margin", "children"),
    Output("kpi-orders", "children"),
    Input("filter-region",   "value"),
    Input("filter-category", "value"),
    Input("filter-year",     "value"),
)
def update_kpis(regions, categories, years):
    d = filter_df(regions or [], categories or [], years or [])
    sales   = d["Sales"].sum()
    profit  = d["Profit"].sum()
    margin  = (profit / sales * 100) if sales else 0
    orders  = d["Order ID"].nunique() if "Order ID" in d.columns else len(d)
    return (f"${sales/1e6:.2f}M", f"${profit/1e3:.1f}K",
            f"{margin:.1f}%",     f"{orders:,}")

# ── Tab Content Callback ────────────────────────────────────
@callback(
    Output("tab-content", "children"),
    Input("tabs",            "value"),
    Input("filter-region",   "value"),
    Input("filter-category", "value"),
    Input("filter-year",     "value"),
)
def update_tabs(tab, regions, categories, years):
    d = filter_df(regions or [], categories or [], years or [])

    PLOT_LAYOUT = dict(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter, sans-serif", size=12, color="#374151"),
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", showline=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", showline=False),
    )

    # ── Tab 1: Monthly trend ─────────────────────────────
    if tab == "tab1":
        ym = d.groupby("Year-Month")["Sales"].sum().reset_index().sort_values("Year-Month")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ym["Year-Month"], y=ym["Sales"],
            mode="lines+markers",
            line=dict(color=C_BLUE, width=2.5),
            marker=dict(size=5, color=C_BLUE),
            fill="tozeroy", fillcolor="rgba(67,97,238,0.1)",
            name="Sales",
            hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(title="Monthly Sales Trend", **PLOT_LAYOUT,
                          xaxis_tickangle=-45)
        return dcc.Graph(figure=fig, style={"height":"480px"})

    # ── Tab 2: Top products ──────────────────────────────
    elif tab == "tab2":
        top = d.groupby("Product Name")["Sales"].sum().sort_values(ascending=False).head(15).reset_index()
        top.columns = ["Product", "Sales"]
        top["Product"] = top["Product"].str[:40]
        fig = px.bar(top[::-1], x="Sales", y="Product", orientation="h",
                     color="Sales", color_continuous_scale=["#93C5FD","#1D4ED8"],
                     title="Top 15 Products by Revenue",
                     labels={"Sales":"Total Sales ($)","Product":""},
                     text=top[::-1]["Sales"].apply(lambda v: f"${v:,.0f}"))
        fig.update_traces(textposition="outside")
        fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False,
                          xaxis_tickprefix="$", height=520)
        return dcc.Graph(figure=fig, style={"height":"540px"})

    # ── Tab 3: Regional choropleth map ───────────────────
    elif tab == "tab3":
        state_data = d.groupby("State").agg(
            Sales=("Sales","sum"),
            Profit=("Profit","sum")
        ).reset_index()
        state_data["Profit Margin %"] = (state_data["Profit"] / state_data["Sales"] * 100).round(2)

        fig = px.choropleth(
            state_data,
            locations="State",
            locationmode="USA-states",
            color="Sales",
            scope="usa",
            hover_name="State",
            hover_data={"Sales":":.0f","Profit":":.0f","Profit Margin %":":.1f"},
            color_continuous_scale=px.colors.sequential.Blues,
            title="Sales by State (Choropleth Map)",
            labels={"Sales":"Total Sales ($)"},
        )
        fig.update_layout(
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif", size=12),
            margin=dict(l=0, r=0, t=50, b=0),
            geo=dict(bgcolor="white", lakecolor="white",
                     landcolor="#F1F5F9", showlakes=True),
        )

        # Regional bar below map
        reg = d.groupby("Region").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
        fig2 = px.bar(reg, x="Region", y=["Sales","Profit"],
                      barmode="group",
                      color_discrete_map={"Sales":C_BLUE,"Profit":"#10B981"},
                      title="Sales vs Profit by Region",
                      labels={"value":"Amount ($)","variable":"Metric"},
                      text_auto=".2s")
        fig2.update_layout(**PLOT_LAYOUT)

        return html.Div([
            dcc.Graph(figure=fig, style={"height":"400px"}),
            dcc.Graph(figure=fig2, style={"height":"380px","marginTop":"12px"}),
        ])

    # ── Tab 4: Profit Analysis ───────────────────────────
    elif tab == "tab4":
        # Subcat treemap
        sub = d.groupby(["Category","Sub-Category"]).agg(
            Sales=("Sales","sum"), Profit=("Profit","sum")
        ).reset_index()
        sub["Margin %"] = (sub["Profit"] / sub["Sales"] * 100).round(1)

        fig1 = px.treemap(sub, path=["Category","Sub-Category"],
                          values="Sales", color="Margin %",
                          color_continuous_scale="RdYlGn",
                          color_continuous_midpoint=0,
                          title="Profit Margin by Category / Sub-Category (Treemap)",
                          hover_data={"Margin %":":.1f","Sales":":.0f","Profit":":.0f"})
        fig1.update_layout(paper_bgcolor="white",
                           font=dict(family="Inter",size=12),
                           margin=dict(l=10,r=10,t=50,b=10))

        # Discount impact scatter
        prod = d.groupby("Sub-Category").agg(
            Avg_Discount=("Discount","mean"),
            Avg_Profit=("Profit","mean"),
            Sales=("Sales","sum")
        ).reset_index()

        fig2 = px.scatter(prod, x="Avg_Discount", y="Avg_Profit",
                          size="Sales", text="Sub-Category",
                          color="Avg_Profit",
                          color_continuous_scale="RdYlGn",
                          title="Discount vs Avg Profit per Sub-Category",
                          labels={"Avg_Discount":"Average Discount","Avg_Profit":"Average Profit ($)"})
        fig2.update_traces(textposition="top center", textfont_size=9)
        fig2.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False)

        return html.Div([
            dcc.Graph(figure=fig1, style={"height":"420px"}),
            dcc.Graph(figure=fig2, style={"height":"400px","marginTop":"12px"}),
        ])

    return html.Div("Select a tab.")

# ── Run ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print(" Superstore Sales Dashboard")
    print(" Open: http://127.0.0.1:8050")
    print("=" * 60)
    app.run(debug=False, host="127.0.0.1", port=8050)
