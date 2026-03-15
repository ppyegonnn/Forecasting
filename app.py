import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Inventory Dashboard", layout="wide")

base = os.path.dirname(__file__)
reorder_df = pd.read_csv(os.path.join(base, "reorder_report.csv"))
forecast_df = pd.read_csv(os.path.join(base, "forecasts.csv"), parse_dates=["ds"])
demand_df = pd.read_csv(os.path.join(base, "weekly_demand.csv"), parse_dates=["Week"])

st.sidebar.title("Inventory Planner")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", ["Stock Overview", "Demand Forecast", "Reorder Alerts"])

if page == "Stock Overview":
    st.title("Stock Overview")
    st.markdown("Summary of current inventory health across all 8 products.")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", len(reorder_df))
    col2.metric("Critical", len(reorder_df[reorder_df["Status"] == "CRITICAL"]))
    col3.metric("Reorder Now", len(reorder_df[reorder_df["Status"] == "REORDER NOW"]))
    col4.metric("OK", len(reorder_df[reorder_df["Status"] == "OK"]))
    st.markdown("---")
    st.subheader("Current Stock vs Reorder Point")
    fig = go.Figure()
    fig.add_bar(x=reorder_df["Product"], y=reorder_df["Current Stock (simulated)"], name="Current Stock", marker_color="#378ADD")
    fig.add_bar(x=reorder_df["Product"], y=reorder_df["Reorder Point"], name="Reorder Point", marker_color="#E24B4A", opacity=0.6)
    fig.update_layout(barmode="group", xaxis_tickangle=-30, height=420, legend=dict(orientation="h", y=1.1), margin=dict(t=20, b=120))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    st.subheader("Avg Weekly Demand by Product")
    fig2 = go.Figure(go.Bar(x=reorder_df["Product"], y=reorder_df["Avg Weekly Demand"], marker_color="#1D9E75"))
    fig2.update_layout(xaxis_tickangle=-30, height=380, margin=dict(t=20, b=120))
    st.plotly_chart(fig2, use_container_width=True)

elif page == "Demand Forecast":
    st.title("Demand Forecast")
    st.markdown("4-week rolling average forecast vs actual weekly demand.")
    products = forecast_df["Description"].unique().tolist()
    selected = st.selectbox("Select a product", products)
    product_fc = forecast_df[forecast_df["Description"] == selected].copy()
    actual_only = product_fc[product_fc["actual"].notna()].copy()
    acc_row = reorder_df[reorder_df["Product"] == selected]
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Weekly Demand", f"{acc_row['Avg Weekly Demand'].values[0]:,.0f} units")
    col2.metric("Safety Stock", f"{acc_row['Safety Stock'].values[0]:,.0f} units")
    col3.metric("Forecast Next 4 Weeks", f"{acc_row['Forecast Next 4 Weeks'].values[0]:,.0f} units")
    st.markdown("---")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=actual_only["ds"], y=actual_only["actual"], name="Actual demand", line=dict(color="#378ADD", width=2)))
    fig.add_trace(go.Scatter(x=product_fc["ds"], y=product_fc["yhat"], name="Forecast", line=dict(color="#1D9E75", width=2, dash="dash")))
    cutoff = actual_only["ds"].max()
    fig.add_shape(type="line", x0=cutoff, x1=cutoff, y0=0, y1=1, xref="x", yref="paper", line=dict(color="#E24B4A", dash="dot", width=1.5))
    fig.add_annotation(x=cutoff, y=1, xref="x", yref="paper", text="Forecast starts", showarrow=False, yanchor="bottom", font=dict(color="#E24B4A", size=11))
    fig.update_layout(height=420, xaxis_title="Week", yaxis_title="Units", legend=dict(orientation="h", y=1.1), margin=dict(t=20, b=40))
    st.plotly_chart(fig, use_container_width=True)

elif page == "Reorder Alerts":
    st.title("Reorder Alerts")
    st.markdown("Stock status for all products. Red = critical, amber = reorder, green = OK.")
    def color_status(val):
        colors = {
            "CRITICAL": "background-color: #FCEBEB; color: #A32D2D; font-weight: bold",
            "REORDER NOW": "background-color: #FAEEDA; color: #633806; font-weight: bold",
            "OK": "background-color: #E1F5EE; color: #085041; font-weight: bold"
        }
        return colors.get(val, "")
    display_cols = ["Product", "Avg Weekly Demand", "Safety Stock", "Reorder Point", "Current Stock (simulated)", "Forecast Next 4 Weeks", "Recommended Order Qty", "Status"]
    styled = reorder_df[display_cols].style.applymap(color_status, subset=["Status"])
    st.dataframe(styled, use_container_width=True, height=350)
    st.markdown("---")
    st.subheader("Safety Stock vs Current Stock")
    fig = go.Figure()
    fig.add_bar(x=reorder_df["Product"], y=reorder_df["Current Stock (simulated)"], name="Current Stock", marker_color="#378ADD")
    fig.add_bar(x=reorder_df["Product"], y=reorder_df["Safety Stock"], name="Safety Stock", marker_color="#E24B4A", opacity=0.7)
    fig.update_layout(barmode="group", xaxis_tickangle=-30, height=400, legend=dict(orientation="h", y=1.1), margin=dict(t=20, b=120))
    st.plotly_chart(fig, use_container_width=True)
