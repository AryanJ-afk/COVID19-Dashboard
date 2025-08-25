import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="COVID-19 Global Dashboard", layout="wide")

@st.cache_data
def load_data():
    country = pd.read_csv("data/processed/country_daily.csv", parse_dates=["date"])
    global_df = pd.read_csv("data/processed/global_daily.csv", parse_dates=["date"])
    # Clean country names inconsistencies (minimal)
    country["country"] = country["country"].str.replace(r"\*", "", regex=True).str.strip()
    return country, global_df

def overview_tab(country, global_df):
    st.subheader("Global Overview")
    c1, c2, c3, c4 = st.columns(4)
    last = global_df.sort_values("date").iloc[-1]
    c1.metric("Total Confirmed", f"{int(last['confirmed']):,}")
    c2.metric("Total Deaths", f"{int(last['deaths']):,}")
    if "new_confirmed_7dma" in global_df.columns:
        c3.metric("New Cases (7-day MA)", f"{int(round(last['new_confirmed_7dma'])):,}")
    if "cfr" in global_df.columns:
        c4.metric("Global CFR", f"{last['cfr']*100:.2f}%")

    st.markdown("### Global Trend")
    fig = px.line(global_df, x="date", y=["new_confirmed_7dma","new_deaths_7dma"] if "new_deaths_7dma" in global_df.columns else ["new_confirmed_7dma"],
                  labels={"value":"Count","variable":"Metric"},
                  title="Global New Cases / Deaths (7-day MA)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Map: Cumulative Confirmed by Country (latest date)")
    latest_date = country["date"].max()
    latest = country[country["date"] == latest_date]
    fig_map = px.choropleth(
        latest,
        locations="country",
        locationmode="country names",
        color="confirmed",
        hover_name="country",
        color_continuous_scale="Reds",
        title=f"Confirmed Cases by Country — {latest_date.date()}",
    )
    st.plotly_chart(fig_map, use_container_width=True)

def country_analysis_tab(country):
    st.subheader("Country Analysis")
    countries = sorted(country["country"].unique().tolist())
    default = "India" if "India" in countries else countries[0]
    picked = st.selectbox("Select country", countries, index=countries.index(default))
    dfc = country[country["country"] == picked].sort_values("date")

    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.line(dfc, x="date", y=["confirmed","deaths"], title=f"Cumulative — {picked}")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        y_cols = []
        if "new_confirmed_7dma" in dfc.columns: y_cols.append("new_confirmed_7dma")
        if "new_deaths_7dma" in dfc.columns: y_cols.append("new_deaths_7dma")
        if not y_cols: y_cols = [c for c in ["new_confirmed","new_deaths"] if c in dfc.columns]
        fig2 = px.line(dfc, x="date", y=y_cols, title=f"Daily (7-day MA) — {picked}")
        st.plotly_chart(fig2, use_container_width=True)

    if "cfr" in dfc.columns:
        st.markdown("**Case Fatality Rate (CFR)**")
        fig3 = px.line(dfc, x="date", y="cfr", labels={"cfr":"CFR"}, title=f"CFR — {picked}")
        st.plotly_chart(fig3, use_container_width=True)

def comparison_tab(country):
    st.subheader("Country Comparison")
    countries = sorted(country["country"].unique().tolist())
    picks = st.multiselect("Select countries to compare", countries, default=["India","United States"] if {"India","United States"}.issubset(countries) else countries[:2])
    metric_options = [c for c in ["new_confirmed_7dma","new_deaths_7dma","confirmed","deaths"] if c in country.columns]
    metric = st.selectbox("Metric", metric_options, index=0)

    dfp = country[country["country"].isin(picks)].sort_values(["country","date"])
    fig = px.line(dfp, x="date", y=metric, color="country", title=f"{metric.replace('_',' ').title()} — Comparison")
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("COVID-19 Global Dashboard")
    st.caption("Data: Johns Hopkins CSSE. This is an educational portfolio project.")

    # Safety: ensure processed files exist
    if not Path("data/processed/country_daily.csv").exists():
        st.warning("Processed data files not found. Run `python data_fetch.py` first.")
        st.stop()

    country, global_df = load_data()
    tabs = st.tabs(["Overview", "Country Analysis", "Comparison"])
    with tabs[0]: overview_tab(country, global_df)
    with tabs[1]: country_analysis_tab(country)
    with tabs[2]: comparison_tab(country)

if __name__ == "__main__":
    main()
