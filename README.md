 README.md
# AI-Powered Knowledge Engine for Smart Support Ticket Resolution

### Project Overview
The **AI-Powered Knowledge Engine** is a real-time automation system that classifies incoming support tickets, recommends relevant knowledge base (KB) articles, and identifies missing or underperforming content.  

This project helps customer support teams resolve tickets faster, maintain KB quality, and get proactive alerts when content performance drops.



## Key Features
- **AI-Based Ticket Classification:** Automatically tags tickets using an LLM model (LLaMA / Groq).
- **Semantic Article Recommendations:** Uses FAISS and SentenceTransformer embeddings for top-k article retrieval.
- **Gap Analysis Reports:** Computes CTR, impressions, and click metrics to identify weak KB articles.
- **Slack Alert Integration:** Automatically sends alerts for low-performing articles.
- **Google Sheet Integration:** Loads and syncs ticket data via the Sheets API.
- **Streamlit Dashboard:** Simple visual interface for monitoring, running analysis, and viewing results.


## System Architecture

```
Google Sheets / CSV
        │
        ▼
Preprocessing Layer  ──►  Classification Layer (LLM)
        │
        ▼
Embedding & Indexing (FAISS + SentenceTransformer)
        │
        ▼
Recommendation API (FastAPI)
        │
        ▼
Analytics & Alerting (Gap Analysis + Slack Alerts)
        │
        ▼
Streamlit Dashboard (Visualization)
```



## Project Modules Overview

| Module | Description |
|--------|--------------|
| `preprocessing2.py` | Cleans and standardizes raw text data from support tickets. |
| `classification_tagging.py` | Classifies tickets using a language model (LLaMA/Groq) with confidence scores. |
| `build_index.py` | Builds FAISS semantic index from KB article embeddings. |
| `recommend_api.py` | FastAPI service that returns top-k recommended KB articles for a given ticket. |
| `gap_analysis.py` | Calculates impressions, clicks, and CTR for KB articles. |
| `slack_alerts.py` | Sends Slack alerts for articles with low CTR using a daily scheduler. |
| `gsheet_loader.py` | Loads ticket data from Google Sheets via service account credentials. |
| `app.py` | Streamlit dashboard to visualize reports and trigger processes. |



## Tech Stack
- **Programming Language:** Python 3.10+
- **Frameworks & Libraries:**
  - FastAPI, Streamlit
  - FAISS, SentenceTransformers
  - Pandas, NumPy
  - APScheduler, Requests, GSpread
- **Integrations:** Google Sheets API, Slack Webhooks
- **Deployment Ready:** Can be hosted locally or on cloud (Render / AWS / GCP).



## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/AI-Knowledge-Engine.git
cd AI-Knowledge-Engine
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Create a `.env` file in the project root:
```bash
SLACK_WEBHOOK_URL=<your_slack_webhook_url>
```

### 4. Add Google Sheet Credentials
Save your Google service account JSON in:
```
credentials/service_account.json
```



## Running the Project

### Run the FastAPI Recommendation API
```bash
uvicorn recommend_api:app --reload
```
Then visit: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Run the Streamlit Dashboard
```bash
streamlit run app.py
```
Use the dashboard to:
- Load tickets from Google Sheets
- Preprocess & classify
- Run recommendations
- Execute gap analysis
- Send Slack alerts



## Sample Output Files
| File | Description |
|------|--------------|
| `data/processed/preprocessed_tickets.csv` | Cleaned & tokenized ticket data. |
| `logs/coverage_report5.csv` | Engagement metrics & CTR report. |
| `logs/alerts5.log` | Daily Slack alert logs. |



## Results & Evaluation
- Ticket classification accuracy: **~85%**
- Semantic recommendation latency: **<1 second/query**
- Auto-detection of KB gaps (CTR < 0.5)
- Automated Slack alerts for low-performing articles



## Future Enhancements
- Add multilingual model support.
- Implement agent feedback learning for re-ranking.
- Add interactive analytics dashboards.
- Deploy on cloud (GCP or Render) with continuous monitoring.



## 🧑‍💻 Contributors
- **Emmadi Srikar** — Project Lead & Developer



## License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.



## Acknowledgements
- **SentenceTransformers** for embeddings  
- **FAISS** for fast similarity search  
- **FastAPI** & **Streamlit** for modern web interfaces  
- **Slack API** for notifications  
- **Google Sheets API** for live data integration  



### Feedback
If you find this project useful, give it a ⭐ on GitHub and share your feedback!
