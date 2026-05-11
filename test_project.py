"""
Test Script for PGA Predictive Intelligence

Sends one sample prediction request to the Databricks Model Serving endpoint.

Requirements:
pip install requests

Usage:
python test_project.py
"""

import os
import sys
import requests

URL = os.getenv(
    "DATABRICKS_ENDPOINT_URL",
    "https://dbc-54edc556-f10f.cloud.databricks.com/serving-endpoints/pga-dkp-predictor/invocations"
)

TOKEN = os.getenv("DATABRICKS_TOKEN")

if not TOKEN:
    print("FAIL: Missing DATABRICKS_TOKEN environment variable.")
    print("Set it before running this script.")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "dataframe_records": [
        {
            "purse": 20000000,
            "no_cut": 0,
            "avg_total_dkp_last_5": 65,
            "avg_sg_total_last_5": 1.2,
            "avg_sg_t2g_last_5": 0.8,
            "avg_sg_app_last_5": 0.4,
            "avg_sg_ott_last_5": 0.3,
            "avg_sg_putt_last_5": 0.1,
            "avg_strokes_last_5": 280,
            "avg_finish_position_last_5": 28,
            "cuts_made_last_5": 0.8,
            "starts_last_5": 5
        }
    ]
}

try:
    response = requests.post(URL, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        print(f"FAIL: status code {response.status_code}")
        print(response.text)
        sys.exit(1)

    result = response.json()
    print("Prediction response:")
    print(result)
    print("PASS")
    sys.exit(0)

except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)