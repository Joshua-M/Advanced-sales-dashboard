import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
import os

# Set page config
st.set_page_config(page_title="Advanced Data Dashboard", page_icon="📊", layout="wide")

# Title
st.title("📊 Advanced Data Analytics Dashboard")

# Sidebar: File Upload
st.sidebar.header("Upload Dataset")
fl = st.sidebar.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])
df = None

# Load Data
if fl is not None:
    file_extension = fl.name.split(".")[-1]
    if file_extension == "xlsx":
        df = pd.read_excel(fl, engine="openpyxl")
    elif file_extension == "xls":
        df = pd.read_excel(fl, engine="xlrd")
    else:
        df = pd.read_csv(fl)
    st.sidebar.success(f"✅ Loaded {fl.name}")
else:
    sample_file = "Sample - Superstore.xls"
    if os.path.exists(sample_file):
        df = pd.read_excel(sample_file, engine='xlrd')
        st.sidebar.info("Using Sample Dataset")
    else:
        st.sidebar.warning("⚠ No file uploaded. Please upload a dataset.")
        st.stop()

# Convert Date Column
df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

# Sidebar Filters
st.sidebar.header("🔍 Filters")
startDate, endDate = df["Order Date"].min(), df["Order Date"].max()
date1 = st.sidebar.date_input("Start Date", startDate)
date2 = st.sidebar.date_input("End Date", endDate)

# Apply Date Filter
df_filtered = df[(df["Order Date"] >= pd.to_datetime(date1)) & (df["Order Date"] <= pd.to_datetime(date2))]

# Additional Filters
category = st.sidebar.multiselect("Select Category", df_filtered["Category"].dropna().unique())
segment = st.sidebar.multiselect("Select Segment", df_filtered["Segment"].dropna().unique())
profit_range = st.sidebar.slider("Profit Range", float(df_filtered["Profit"].min()), float(df_filtered["Profit"].max()), (float(df_filtered["Profit"].min()), float(df_filtered["Profit"].max())))

# Apply Additional Filters
if category:
    df_filtered = df_filtered[df_filtered["Category"].isin(category)]
if segment:
    df_filtered = df_filtered[df_filtered["Segment"].isin(segment)]
df_filtered = df_filtered[(df_filtered["Profit"] >= profit_range[0]) & (df_filtered["Profit"] <= profit_range[1])]

# Metrics Display
total_sales = df_filtered["Sales"].sum()
avg_order_value = df_filtered["Sales"].mean()
total_profit = df_filtered["Profit"].sum()
total_orders = len(df_filtered)

st.markdown("### 📌 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Avg. Order Value", f"${avg_order_value:,.2f}")
col3.metric("Total Profit", f"${total_profit:,.2f}")
col4.metric("Total Orders", total_orders)

# Tabs for Visualization
st.markdown("### 📊 Data Visualizations")
tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales Trends", "📊 Category Sales", "🗺️ Heatmaps", "🔍 Detailed Data"])

with tab1:
    st.subheader("📈 Sales Over Time")
    df_filtered["month_year"] = df_filtered["Order Date"].dt.to_period("M")
    sales_trend = df_filtered.groupby(df_filtered["month_year"].astype(str))["Sales"].sum().reset_index()
    fig = px.line(sales_trend, x="month_year", y="Sales", title="Monthly Sales Trend")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📊 Sales by Category")
    category_sales = df_filtered.groupby("Category")["Sales"].sum().reset_index()
    fig = px.bar(category_sales, x="Category", y="Sales", text=category_sales["Sales"].map("${:,.2f}".format), template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("🗺️ Profit vs. Sales Heatmap")
    
    # Prepare data for heatmap
    heatmap_data = df_filtered.pivot_table(index="Category", columns="Segment", values="Profit", aggfunc="sum")
    
    if heatmap_data.empty:
        st.warning("⚠ No data available for the heatmap. Try adjusting the filters.")
    else:
        fig = ff.create_annotated_heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns.tolist(),
            y=heatmap_data.index.tolist(),
            colorscale="Viridis",
            showscale=True
        )
        st.plotly_chart(fig, use_container_width=True)


with tab4:
    st.subheader("🔍 Detailed Data")
    st.write(df_filtered)
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download Processed Data", data=csv, file_name="Processed_Data.csv", mime="text/csv")

# AI Insights Panel
st.markdown("### 🤖 AI-Driven Insights")
insight_placeholder = st.empty()

if total_sales > 100000:
    insight_placeholder.success("🚀 Sales performance is strong! Consider expanding product lines.")
elif total_sales < 50000:
    insight_placeholder.warning("⚠ Sales are lower than expected. Consider revising pricing strategies.")

if avg_order_value > 500:
    insight_placeholder.info("💡 High average order value detected. Consider loyalty programs.")
