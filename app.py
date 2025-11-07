import os
import json
import uvicorn
import requests
import pandas as pd
import threading
import streamlit as st
from integrations.gsheet_loader import GoogleSheetLoader 
from src.preprocessing2 import TicketProcessor
from src.classification_tagging import TicketClassifier
from src.test_request3 import RecommendationClient
from src.gap_analysis import RecommendationAnalyzer
from integrations.slack_alerts import DailyAlertScheduler


# CONFIG
API_URL = "http://127.0.0.1:8000/recommend"
LOG_PATH = "logs/recommendation_results_tickets5.csv"
OUTPUT_DIR = "logs/"

st.set_page_config(page_title="Smart Support AI Dashboard", layout="wide")
st.title("Smart Support AI Dashboard")

# SESSION STATE INIT

if "gsheet_data" not in st.session_state:
    st.session_state.gsheet_data = None

if "df" not in st.session_state:
    st.session_state.df = None

if "ticket_classify_result" not in st.session_state:
    st.session_state.ticket_classify_result = None

if "batch_classify_result" not in st.session_state:
    st.session_state.batch_classify_result = None

if "recommendation_result" not in st.session_state:
    st.session_state.recommendation_result = None

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None



# Session State Initialization
if "alert_scheduler" not in st.session_state:
    st.session_state.alert_scheduler = None


# VERTICAL TABS (Sidebar Navigation)
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to Section:",
    [
        "📥 Load Tickets from Google Sheet", 
        "🧹 Ticket Preprocessing",
        "🎫 Ticket Classification and Tagging", 
        "📄 Ticket Recommendations", 
        "📊 Gap Analysis", 
        "🔔 Slack Alerts"
    ]
)


# TAB 1: Load Tickets from Google Sheet
if page == "📥 Load Tickets from Google Sheet":
    st.header("📥 Load Tickets from Google Sheet")
    
    # Moved the Google Sheets settings to the main page
    st.subheader("Google Sheet Settings")
    sheet_name = st.text_input("Google Sheet Name", "tickets1")
    worksheet_name = st.text_input("Worksheet Name", "Sheet1")
    creds_path = st.text_input("Credentials File Path", "credentials/service_account.json")
    
    submit_button = st.button("Load Data")
    
    if submit_button:
        try:
            google_sheet_loader = GoogleSheetLoader(sheet_name, worksheet_name, creds_path)
            st.session_state.gsheet_data = google_sheet_loader.load_data()
            st.success("Tickets Loaded Successfully!")

            if not st.session_state.gsheet_data.empty:
                st.write("### Loaded Tickets Preview")
                st.dataframe(st.session_state.gsheet_data)

                # Save the loaded data as tickets6.csv in data/raw folder
                raw_data_dir = "data/raw"
                os.makedirs(raw_data_dir, exist_ok=True)  # Ensure the folder exists
                tickets_file_path = os.path.join(raw_data_dir, "tickets6.csv")
                
                # Save DataFrame to CSV
                st.session_state.gsheet_data.to_csv(tickets_file_path, index=False)
                st.success(f"✅ Tickets saved as {tickets_file_path}")

                csv_data = st.session_state.gsheet_data.to_csv(index=False)
                st.download_button(
                    label="📥 Download Loaded Tickets as CSV",
                    data=csv_data,
                    file_name="loaded_tickets.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data found in the Google Sheet.")
        except Exception as e:
            st.error(f"❌ Error loading data from Google Sheets: {e}")




# TAB 2: Ticket Preprocessing
if page == "🧹 Ticket Preprocessing":
    st.header("🧹 Ticket Preprocessing")
    
    # File upload or path input for raw ticket CSV
    file_option = st.radio("Input Option:", ["CSV Upload", "Use Default File"])

    if file_option == "CSV Upload":
        uploaded_file = st.file_uploader("Upload Raw Tickets CSV", type=["csv"])
        
        if uploaded_file:
            uploaded_filename = uploaded_file.name
            base_filename = uploaded_filename.split('.')[0]
            preprocessed_filename = f"preprocessed_{base_filename}.csv"

            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())  # Show sample data
            st.session_state.df = df  # Store the dataframe in session state

            if st.button("Preprocess and Save", key="preprocess"):
                with st.spinner("Preprocessing tickets..."):
                    processor = TicketProcessor(df = df, output_file=f"data/processed/{preprocessed_filename}")
                    processor.process_and_save()
                    st.success(f"Preprocessing completed! Saved to data/processed/{preprocessed_filename}")

                # Optionally, show and provide a download for the processed CSV
                processed_df = pd.read_csv(f"data/processed/{preprocessed_filename}")
                st.dataframe(processed_df.head())
                st.download_button("Download Processed CSV", processed_df.to_csv(index=False), "processed_tickets.csv", "text/csv")

    else:  # Use default file (hardcoded path)
        st.subheader("Using Default Tickets File")
        processor = TicketProcessor("data/raw/tickets6.csv", "data/processed/preprocessed_tickets6.csv")
        
        if st.button("Preprocess and Save Default File"):
            with st.spinner("Preprocessing default tickets..."):
                processor.process_and_save()
                st.success(f"Preprocessing completed! Processed file saved in data/processed/preprocessed_tickets6.csv")

            # Show and download the processed data
            processed_df = pd.read_csv("data/processed/preprocessed_tickets6.csv")
            st.dataframe(processed_df.head())
            st.download_button(
                label="📥 Download Processed Tickets",
                data=processed_df.to_csv(index=False),
                file_name="preprocessed_tickets6.csv",
                mime="text/csv"
            )


# TAB 2: Ticket Classification
if page == "🎫 Ticket Classification and Tagging":
    st.header("🎫 Ticket Classification and Tagging")
    classifier = TicketClassifier()

    classify_option = st.radio("Input Type:", ["Single Ticket", "CSV Upload"])

    if classify_option == "Single Ticket":
        text_input = st.text_area("Enter a support ticket:", "I was charged twice for my order.")
        ticket_id = st.text_input("Ticket ID", "T001")

        if st.button("Classify Ticket", key="single_ticket"):
            with st.spinner("Classifying..."):
                st.session_state.ticket_classify_result = classifier.classify_ticket(ticket_id, text_input)

        if st.session_state.ticket_classify_result:
            st.subheader("✅ Classification Result")
            st.json(st.session_state.ticket_classify_result)

    else:  # CSV Upload
        uploaded_file = st.file_uploader("Upload CSV with 'clean_text' column", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)

            if "ticket_id" not in df.columns or "clean_text" not in df.columns:
                st.error("CSV must contain 'ticket_id' and 'clean_text' columns.")

            else:
                if st.button("Classify All Tickets", key="batch_ticket"):
                    with st.spinner("Classifying all tickets..."):
                        ticket_id = df["ticket_id"].tolist()
                        tickets = df["clean_text"].tolist()
                        classifier.classify_all(ticket_id, tickets)

                        # Convert the results to a DataFrame
                        classified_df = pd.DataFrame(classifier.results)
                        st.session_state.batch_classify_result = classified_df

                        # Save the classified tickets as a CSV file
                        classified_data_dir = "data/processed"
                        os.makedirs(classified_data_dir, exist_ok=True)
                        tickets_file_path = os.path.join(classified_data_dir, "classified_tickets5.csv")

                        classified_df.to_csv(tickets_file_path, index=False)
                        st.success(f"✅ Classified tickets saved to {tickets_file_path}")

                if st.session_state.batch_classify_result is not None:
                    st.subheader("✅ Tickets Classification Results")
                    st.dataframe(st.session_state.batch_classify_result.head())
                    st.download_button(
                        "📥 Download Results CSV",
                        st.session_state.batch_classify_result.to_csv(index=False),
                        "classified_tickets.csv",
                        "text/csv"
                    )


# TAB 3: Recommendations
if page == "📄 Ticket Recommendations":
    st.header("📄 Single Ticket Recommendation")

    with st.form("recommend_form"):
        ticket_id = st.text_input("Ticket ID", "T001")
        ticket_text = st.text_area("Ticket Text", "I was charged twice for my order.")
        submitted = st.form_submit_button("Get Recommendations ⚡")

    if submitted:
        try:
            payload = {"ticket_id": ticket_id, "ticket_text": ticket_text}
            response = requests.post(API_URL, json=payload)

            if response.status_code == 200:
                st.session_state.recommendation_result = response.json()
                st.success("✅ Recommendations received successfully!")

            else:
                st.error(f"❌ API Error {response.status_code}: {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("⚠️ Could not connect to FastAPI server.")
            st.code("uvicorn src.recommend_api:app --reload")

    if st.session_state.recommendation_result:
        st.subheader("Recommended Articles")
        recs = pd.DataFrame(st.session_state.recommendation_result["recommendations"])
        st.dataframe(recs)

    st.markdown("---")

    st.header("📄 Multiple Tickets Recommendation")

    api_url = os.getenv("RECOMMENDATION_API_URL", "http://127.0.0.1:8000/recommend")
    client = RecommendationClient(api_url=api_url)

    uploaded_file = st.file_uploader(
        "Upload a CSV file containing tickets", type=["csv"], key="ticket_upload"
    )

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write(f"✅ Loaded **{len(df)}** tickets.")
        st.dataframe(df.head())

        
        if st.button("Get Recommendations ⚡", key="recommend_button"):
            with st.spinner("Generating Recommendations..."):
                tickets = df.to_dict(orient="records")
                results = [client.send_ticket(ticket) for ticket in tickets]
                results_df = pd.DataFrame(results)
                
                os.makedirs("logs", exist_ok=True)
                results_df.to_csv(f"logs/recommendation_results_tickets5.csv", index=False)
                st.success(f"✅ Recommendations generated and saved to logs/recommendation_results_tickets5.csv")
                
                results_df["results"] = results_df["recommendations"]  # map your data here
                
                # Flatten and format recommendations for display (top 3 only)
                def format_recommendations(recs):
                    if isinstance(recs, list):
                        return ", ".join([r.get("title", str(r)) for r in recs[:3]])
                    return str(recs)

                if "recommendations" in results_df.columns:
                    results_df["top_3_recommendations"] = results_df["recommendations"].apply(format_recommendations)

            st.success("Recommended Articles")
            st.dataframe(results_df[["ticket_id", "ticket_text", "top_3_recommendations"]])

            st.download_button(
                label="📥 Download Results (CSV)",
                data=results_df.to_csv(index=False).encode("utf-8"),
                file_name="recommendation_results.csv",
                mime="text/csv",
                key="download_csv"
            )

    else:
        st.info("Please upload a ticket CSV file to get started.")




# TAB 4: Gap Analysis
if page == "📊 Gap Analysis":
    st.header("📊 Analyze Recommendation Logs")

    if os.path.exists(LOG_PATH):
        if st.button("Run Coverage & Engagement Analysis", key="run_analysis"):
            analyzer = RecommendationAnalyzer(log_path=LOG_PATH, output_dir=OUTPUT_DIR)
            with st.spinner("Analyzing logs..."):
                st.session_state.analysis_result = analyzer.run_full_analysis()

        if st.session_state.analysis_result:
            results = st.session_state.analysis_result

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Articles", len(results["summary"]))
            col2.metric("Low CTR Articles", len(results["low_ctr"]))
            col3.metric("Unused Articles", len(results["unused"]))

            st.subheader("📋 Full Summary")
            st.dataframe(results["summary"])

            st.subheader("🔻 Low CTR Articles (< 0.6 CTR)")
            st.dataframe(results["low_ctr"][["article", "CTR", "impressions", "avg_score"]])

            st.subheader("Unused Articles (0 Impressions)")
            st.dataframe(results["unused"][["article", "impressions"]])

            # Download report
            with open(results["report_path"], "rb") as f:
                st.download_button(
                    label="📥 Download Coverage Report CSV",
                    data=f,
                    file_name=os.path.basename(results["report_path"]),
                    mime="text/csv"
                )
    else:
        st.info("📄 No logs found yet. Submit tickets first via the Recommendations tab.")




# TAB 5: Slack Alerts 

# CONFIG
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

from apscheduler.schedulers.background import BackgroundScheduler
from integrations.slack_alerts import DailyAlertScheduler  # Import your class
import dotenv

if page == "🔔 Slack Alerts":
    st.header("🔔 Slack Alerts - Daily Gap Analysis")
    st.markdown("Monitor article CTRs and automatically send alerts to Slack channels.")

    if not SLACK_WEBHOOK_URL:
        st.error("❌ `SLACK_WEBHOOK_URL` is not set in your `.env` file. Please configure it before using this page.")
        st.stop()

    # Initialize Scheduler 
    alert_scheduler = DailyAlertScheduler(
        slack_webhook_url=SLACK_WEBHOOK_URL,
        coverage_report_path="logs/coverage_report5.csv",
        alert_log_path="logs/alerts5.log"
    )

    # Use BackgroundScheduler so Streamlit doesn’t freeze
    alert_scheduler.scheduler = BackgroundScheduler()
    alert_scheduler.scheduler.add_job(alert_scheduler.daily_alert, "interval", hours=24)

    # UI Controls
    st.subheader("Alert Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📤 Send Alert Now"):
            st.info("Running daily alert check...")
            alert_scheduler.daily_alert()
            st.success("✅ Alert sent successfully.")

    with col2:
        if st.button("▶️ Start Scheduler"):
            if not alert_scheduler.scheduler.running:
                alert_scheduler.scheduler.start()
                st.success("🚀 Scheduler started — will run every 24 hours.")
            else:
                st.warning("⚠️ Scheduler is already running.")

    with col3:
        if st.button("⏹ Stop Scheduler"):
            if alert_scheduler.scheduler.running:
                alert_scheduler.scheduler.shutdown()
                st.warning("🛑 Scheduler stopped.")
            else:
                st.info("Scheduler is not currently running.")


    # --- Alert Logs ---
    st.markdown("### 🧾 Alert Log History")
    if os.path.exists(alert_scheduler.alert_log_path):
        with open(alert_scheduler.alert_log_path, "r") as f:
            logs = f.read()
        st.text_area("Alert Log", logs, height=250)
    else:
        st.info("No alerts logged yet. Use **Send Alert Now** to trigger one.")

    # --- Preview Current Coverage Report ---
    if os.path.exists(alert_scheduler.coverage_report_path):
        st.markdown("### 📊 Current Coverage Report Preview")
        df = pd.read_csv(alert_scheduler.coverage_report_path)
        st.dataframe(df.head())
    else:
        st.info("No coverage report found. Please upload one above.")
        st.stop()