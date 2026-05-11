import streamlit as st
import requests
import pandas as pd

DATABRICKS_ENDPOINT_URL = st.secrets["DATABRICKS_ENDPOINT_URL"]

DATABRICKS_TOKEN = st.secrets["DATABRICKS_TOKEN"]

st.set_page_config(
    page_title="PGA Predictive Intelligence",
    page_icon="⛳",
    layout="wide"
)

st.title("⛳ PGA Predictive Intelligence")

st.markdown("""
### Predict PGA DraftKings Fantasy Performance

This application uses a Databricks distributed pipeline,
Delta Lake feature engineering, MLflow tracking,
and Databricks Model Serving.
""")

st.divider()

col1, col2 = st.columns(2)

with col1:

    purse = st.number_input(
        "Tournament Purse",
        value=20000000
    )

    no_cut = st.selectbox(
        "No Cut Event?",
        [0, 1]
    )

    avg_total_dkp_last_5 = st.slider(
        "Average DK Points Last 5",
        0.0,
        120.0,
        65.0
    )

    avg_sg_total_last_5 = st.slider(
        "Average SG Total",
        -5.0,
        5.0,
        1.2
    )

    avg_sg_t2g_last_5 = st.slider(
        "Average SG Tee-to-Green",
        -5.0,
        5.0,
        0.8
    )

    avg_sg_app_last_5 = st.slider(
        "Average SG Approach",
        -5.0,
        5.0,
        0.4
    )

with col2:

    avg_sg_ott_last_5 = st.slider(
        "Average SG Off-the-Tee",
        -5.0,
        5.0,
        0.3
    )

    avg_sg_putt_last_5 = st.slider(
        "Average SG Putting",
        -5.0,
        5.0,
        0.1
    )

    avg_strokes_last_5 = st.slider(
        "Average Strokes",
        250.0,
        320.0,
        280.0
    )

    avg_finish_position_last_5 = st.slider(
        "Average Finish Position",
        1.0,
        100.0,
        28.0
    )

    cuts_made_last_5 = st.slider(
        "Cuts Made Percentage",
        0.0,
        1.0,
        0.8
    )

    starts_last_5 = st.slider(
        "Recent Starts",
        1,
        5,
        5
    )

st.divider()

if st.button("Predict Fantasy Points"):

    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "dataframe_records": [
            {
                "purse": purse,
                "no_cut": no_cut,
                "avg_total_dkp_last_5": avg_total_dkp_last_5,
                "avg_sg_total_last_5": avg_sg_total_last_5,
                "avg_sg_t2g_last_5": avg_sg_t2g_last_5,
                "avg_sg_app_last_5": avg_sg_app_last_5,
                "avg_sg_ott_last_5": avg_sg_ott_last_5,
                "avg_sg_putt_last_5": avg_sg_putt_last_5,
                "avg_strokes_last_5": avg_strokes_last_5,
                "avg_finish_position_last_5": avg_finish_position_last_5,
                "cuts_made_last_5": cuts_made_last_5,
                "starts_last_5": starts_last_5
            }
        ]
    }

    response = requests.post(
        DATABRICKS_ENDPOINT_URL,
        headers=headers,
        json=payload
    )

    if response.status_code == 200:

        prediction = response.json()["predictions"][0]

        st.success(
            f"Predicted DraftKings Points: {prediction:.2f}"
        )

        chart_df = pd.DataFrame({
            "Projected DK Points": [prediction]
        })

        st.bar_chart(chart_df)

    else:
        st.error(response.text)