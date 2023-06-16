import time
import pandas as pd
from google.cloud import monitoring_v3
from google.cloud import bigquery

from datetime import datetime, timedelta

client = monitoring_v3.MetricServiceClient()
project_name = "projects/hpa-masterthesis"

# Set up the BigQuery client
bq_client = bigquery.Client()

while True:
    
    # Get the current time in UTC
    now_utc = datetime.utcnow()

    # Subtract 5 minutes from the current time to get the rounded time
    rounded_time = now_utc + timedelta(minutes=5)

    # Format the rounded time as a string
    rounded_now = rounded_time.strftime("%Y-%m-%d %H:%M:00")

    # Fetch predicted rps from BigQuery using the rounded current time as the condition
    pusher_q = f"""
    SELECT yhat1 
    FROM `hpa-masterthesis.pusher_forecasts.pusher`
    WHERE ds = '{rounded_now} UTC'
    ORDER BY ds
    """
    query_job = bq_client.query(pusher_q)
    df_q = query_job.result().to_dataframe()
    yhat1_value = df_q['yhat1'].values[0]
    print(yhat1_value)

    # Create the time series data point
    timestamp = int(time.time())
    interval = monitoring_v3.TimeInterval(
        {"end_time": {"seconds": timestamp}}
    )
    point = monitoring_v3.Point({"interval": interval, "value": {"double_value": yhat1_value}})

    # Create the time series and send it to Google Cloud Monitoring
    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/predicted-rps-gke"
    series.resource.type = "gke_container"
    series.resource.labels["instance_id"] = "1234567890123456789"
    series.resource.labels["zone"] = "us-central1-c"

    series.resource.labels["cluster_name"] = "hpa-test"
    series.resource.labels["container_name"] = ""
    series.resource.labels["namespace_id"] = "default"
    series.resource.labels["pod_id"] = "frontend-79767b47b4-p9lqx"

    series.metric.labels["TestLabel"] = "My Label Data"
    series.points = [point]

    client.create_time_series(name=project_name, time_series=[series])

    # Wait for 5 minutes before creating the next time series point
    time.sleep(10)