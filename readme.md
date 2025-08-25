# 📊 COVID-19 Global Dashboard

An interactive dashboard to explore the spread of COVID-19 worldwide, built with **Streamlit** and **Plotly**.
The project uses data from the [Johns Hopkins University CSSE COVID-19 dataset](https://github.com/CSSEGISandData/COVID-19) and demonstrates an end-to-end data science workflow:
➡️ Data ingestion → cleaning & wrangling → feature engineering → visualization → interactive dashboard → deployment.

---

## 🚀 Problem Statement

*"How did COVID-19 spread across regions over time, and what patterns can we observe in different countries?"*

Understanding pandemic trends is useful for governments, healthcare systems, and the public. This project provides a clear, interactive way to explore case numbers, deaths, and fatality rates by country and over time.

---

## 🔧 Tech Stack

* **Python** (pandas, numpy) – data wrangling & processing
* **Plotly** – interactive charts & choropleth maps
* **Streamlit** – web app framework
* **Requests** – fetching raw CSVs directly from GitHub
* **Jupyter Notebook** – initial exploratory data analysis

---

## 📂 Project Structure

```
covid19-dashboard/
│── data/
│   └── raw/         # Raw downloaded CSVs
│   └── processed/   # Cleaned datasets (country_daily.csv, global_daily.csv)
│── notebooks/
│   └── eda.ipynb    # Exploratory data analysis
│── app.py           # Streamlit dashboard
│── data_fetch.py    # Script to download + preprocess data
│── requirements.txt # Dependencies
│── README.md
```

---

## 📈 Dashboard Features

* **Global Overview**

  * Total confirmed cases, deaths, CFR
  * Global trend of new cases & deaths (7-day average)
  * Interactive world map (cases by country)

* **Country Analysis**

  * Select a country and view cumulative & daily trends
  * Case Fatality Rate over time

* **Comparisons**

  * Compare multiple countries on cases, deaths, or trends

---

## 🧮 Engineered Parameters in the Processed Dataset

To make trends more meaningful, we derived the following new columns:

* **`new_confirmed_7dma`** → *7-day moving average of new confirmed cases*

  * Smooths out noisy daily reporting (weekend/holiday effects).
  * Shows the real trend of infections.

* **`new_deaths_7dma`** → *7-day moving average of new deaths*

  * Same smoothing for death counts.
  * Helps visualize mortality trends.

* **`cfr` (Case Fatality Rate)** → *Deaths ÷ Confirmed cases*

  * Proxy for severity of the outbreak and healthcare response.
  * Decreasing CFR often reflects better testing, treatments, or vaccination.

