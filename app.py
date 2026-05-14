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

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #f6f8f4 0%, #eef3ec 100%);
}

.hero {
    background: linear-gradient(135deg, #062e22 0%, #0f5a3d 60%, #c9a961 100%);
    padding: 34px;
    border-radius: 24px;
    color: white;
    box-shadow: 0px 8px 24px rgba(0,0,0,0.18);
    margin-bottom: 24px;
}

.hero-title {
    font-size: 46px;
    font-weight: 900;
    margin-bottom: 8px;
}

.hero-subtitle {
    font-size: 19px;
    opacity: 0.95;
    max-width: 950px;
}

.card {
    background-color: white;
    padding: 24px;
    border-radius: 20px;
    box-shadow: 0px 5px 18px rgba(0,0,0,0.08);
    border: 1px solid #e6e8e3;
    margin-bottom: 18px;
}

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border-left: 7px solid #c9a961;
    box-shadow: 0px 5px 16px rgba(0,0,0,0.08);
}

.metric-label {
    font-size: 13px;
    color: #68736d;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
}

.metric-value {
    font-size: 36px;
    color: #073b2b;
    font-weight: 900;
}

.section-title {
    color: #073b2b;
    font-size: 24px;
    font-weight: 850;
    margin-bottom: 6px;
}

.gold-text {
    color: #b4913f;
    font-weight: 800;
}

.footer {
    text-align: center;
    color: #6f7771;
    font-size: 13px;
    padding-top: 30px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-title">⛳ PGA Predictive Intelligence</div>
    <div class="hero-subtitle">
        A cloud-powered fantasy golf projection engine using Databricks, Delta Lake, MLflow,
        Model Serving, and Streamlit. Adjust player profile inputs and generate a live
        DraftKings fantasy point prediction from the deployed machine learning model.
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Player Input Controls")
    st.caption("Adjust the golfer profile and tournament context.")

    player_name = st.text_input("Golfer Name", value="Sample Player")

    st.divider()
    st.subheader("Tournament Context")
    purse = st.number_input("Tournament Purse", min_value=1000000, max_value=30000000, value=20000000, step=500000)
    no_cut = st.selectbox("No-Cut Event?", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")

    st.divider()
    st.subheader("Recent Fantasy Form")
    avg_total_dkp_last_5 = st.slider("Average DK Points Last 5", 0.0, 120.0, 65.0)

    st.divider()
    st.subheader("Strokes Gained Profile")
    avg_sg_total_last_5 = st.slider("SG Total", -5.0, 5.0, 1.2)
    avg_sg_t2g_last_5 = st.slider("SG Tee-to-Green", -5.0, 5.0, 0.8)
    avg_sg_app_last_5 = st.slider("SG Approach", -5.0, 5.0, 0.4)
    avg_sg_ott_last_5 = st.slider("SG Off-the-Tee", -5.0, 5.0, 0.3)
    avg_sg_putt_last_5 = st.slider("SG Putting", -5.0, 5.0, 0.1)

    st.divider()
    st.subheader("Reliability")
    avg_strokes_last_5 = st.slider("Average Strokes", 250.0, 320.0, 280.0)
    avg_finish_position_last_5 = st.slider("Average Finish Position", 1.0, 100.0, 28.0)
    cuts_made_last_5 = st.slider("Cuts Made Percentage", 0.0, 1.0, 0.8)
    starts_last_5 = st.slider("Starts Last 5", 1, 5, 5)

def projection_tier(prediction):
    if prediction >= 80:
        return "Elite Upside", "This profile projects as a premium fantasy option with strong scoring potential."
    elif prediction >= 65:
        return "Strong Play", "This profile projects as a strong fantasy option with solid recent performance."
    elif prediction >= 50:
        return "Playable", "This profile has usable fantasy value, but the upside is more moderate."
    else:
        return "High Risk", "This profile carries elevated fantasy risk based on the current inputs."

def build_payload():
    return {
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

left, right = st.columns([1.4, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Projection Center</div>', unsafe_allow_html=True)
    st.write(
        f"Current golfer profile: **{player_name}**. "
        "The app sends these inputs to a live Databricks Model Serving endpoint and returns a real-time fantasy projection."
    )
    predict = st.button("Run Live Prediction", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Input Snapshot</div>', unsafe_allow_html=True)
    st.metric("Recent DK Avg", f"{avg_total_dkp_last_5:.1f}")
    st.metric("SG Total", f"{avg_sg_total_last_5:+.2f}")
    st.metric("Cuts Made", f"{cuts_made_last_5:.0%}")
    st.markdown('</div>', unsafe_allow_html=True)

if predict:
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }

    with st.spinner("Calling Databricks Model Serving endpoint..."):
        response = requests.post(
            DATABRICKS_ENDPOINT_URL,
            headers=headers,
            json=build_payload(),
            timeout=60
        )

    if response.status_code != 200:
        st.error("Prediction failed.")
        st.code(response.text)
        st.stop()

    prediction = response.json()["predictions"][0]
    tier, interpretation = projection_tier(prediction)
    difference = prediction - avg_total_dkp_last_5

    st.success("Prediction complete.")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Projected DK Points</div>
            <div class="metric-value">{prediction:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Projection Tier</div>
            <div class="metric-value" style="font-size:28px;">{tier}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Vs Recent Avg</div>
            <div class="metric-value">{difference:+.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Cut Reliability</div>
            <div class="metric-value">{cuts_made_last_5:.0%}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Projection Strength")
    st.progress(min(prediction / 100, 1.0))

    chart_df = pd.DataFrame({
        "Metric": [
            "Projected DK Points",
            "Recent DK Average",
            "SG Total x10",
            "SG T2G x10",
            "SG Approach x10",
            "SG Putting x10",
            "Cuts Made %"
        ],
        "Value": [
            prediction,
            avg_total_dkp_last_5,
            avg_sg_total_last_5 * 10,
            avg_sg_t2g_last_5 * 10,
            avg_sg_app_last_5 * 10,
            avg_sg_putt_last_5 * 10,
            cuts_made_last_5 * 100
        ]
    })

    st.markdown("### Player Projection Profile")
    st.bar_chart(chart_df.set_index("Metric"))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Model Interpretation</div>', unsafe_allow_html=True)
    st.write(interpretation)

    if avg_sg_total_last_5 > 1:
        st.write("The golfer has a positive recent strokes-gained profile, which supports stronger projected fantasy performance.")
    elif avg_sg_total_last_5 < 0:
        st.write("The golfer has a negative recent strokes-gained profile, which may reduce fantasy upside.")

    if cuts_made_last_5 >= 0.8:
        st.write("Recent cut-making consistency is strong, which lowers downside risk.")
    elif cuts_made_last_5 <= 0.4:
        st.write("Recent cut-making consistency is weak, which increases risk.")

    if no_cut == 1:
        st.write("This is a no-cut event, so the player has more scoring opportunity across all rounds.")

    st.markdown('</div>', unsafe_allow_html=True)

with st.expander("Project Methodology"):
    st.write("""
    The system uses a Databricks Medallion Architecture. Raw PGA data was ingested into a Bronze Delta table,
    cleaned and standardized in Silver, and transformed into rolling player-performance features in Gold.
    The Gold table trained a regression model tracked in MLflow, registered in Unity Catalog, and deployed
    through Databricks Model Serving. This Streamlit app calls the live endpoint through a REST API.
    """)

with st.expander("Features Used by the Model"):
    feature_df = pd.DataFrame({
        "Feature": [
            "purse",
            "no_cut",
            "avg_total_dkp_last_5",
            "avg_sg_total_last_5",
            "avg_sg_t2g_last_5",
            "avg_sg_app_last_5",
            "avg_sg_ott_last_5",
            "avg_sg_putt_last_5",
            "avg_strokes_last_5",
            "avg_finish_position_last_5",
            "cuts_made_last_5",
            "starts_last_5"
        ],
        "Meaning": [
            "Tournament prize pool",
            "Whether the event has no cut",
            "Recent DraftKings scoring form",
            "Overall recent strokes gained",
            "Recent tee-to-green performance",
            "Recent approach performance",
            "Recent off-the-tee performance",
            "Recent putting performance",
            "Recent scoring profile",
            "Recent average finish position",
            "Recent cut-making consistency",
            "Number of recent starts"
        ]
    })

    st.dataframe(feature_df, use_container_width=True)

st.markdown("""
<div class="footer">
Built with Databricks, Spark, Delta Lake, MLflow, Databricks Model Serving, GitHub, and Streamlit Cloud.
</div>
""", unsafe_allow_html=True)