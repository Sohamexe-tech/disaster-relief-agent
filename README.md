<img width="1829" height="935" alt="Screenshot 2026-01-21 212546" src="https://github.com/user-attachments/assets/5c681340-9571-45f5-bac5-2ba43341e3ed" /># 🌍 Disaster Relief Resource Scout

> **From Chaos → AI → Action**  
> An agentic AI system that monitors disasters in real-time, eliminates duplicate reports, and surfaces verified, actionable emergency incidents using semantic clustering and multi-source cross-referencing.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Output Examples](#output-examples)
- [Dashboard](#dashboard)
- [Technologies](#technologies)
- [Authors](#authors)

---

## Overview

During disasters, social media and news feeds are flooded with thousands of duplicate, unverified, and chaotic reports. **Disaster Relief Resource Scout** cuts through the noise by:

1. **Ingesting** real-time reports from simulated social media feeds and Google News
2. **Extracting** structured needs (type, location, urgency) using an LLM
3. **Deduplicating** semantically similar reports using DBSCAN clustering
4. **Cross-referencing** incidents across multiple sources to calculate a confidence score
5. **Displaying** verified, prioritized incidents on an interactive web dashboard with a live map

---

## Features

| Feature | Description |
|---|---|
| 🔴 **Real-Time Simulation** | Stream realistic disaster posts at configurable rates |
| 🤖 **LLM Extraction** | Groq's Llama 3.3 70B converts raw text into structured JSON |
| 🔍 **Semantic Deduplication** | DBSCAN clustering on sentence embeddings groups duplicate reports |
| ✅ **Cross-Reference Scoring** | Confidence scoring based on report count, source diversity & urgency consensus |
| 📰 **Live News Integration** | Pulls real disaster headlines from Google News RSS |
| 🗺️ **Interactive Map** | Leaflet.js map with geocoded incident markers |
| 🔎 **News Fact-Checker** | Paste a news URL to get an AI TRUE/FALSE verdict |
| 💾 **JSON Export** | All verified incidents saved to structured output files |

---

## Architecture

```
Raw Reports (Social Media / News)
         │
         ▼
 ┌───────────────────┐
 │   Extract Agent   │  ← Groq LLM (Llama 3.3 70B) + keyword fallback
 │  (extract_agent)  │
 └────────┬──────────┘
          │  Structured Need objects
          ▼
 ┌───────────────────┐
 │ Deduplication     │  ← SentenceTransformer embeddings + DBSCAN
 │     Agent         │
 └────────┬──────────┘
          │  UniqueIncident clusters
          ▼
 ┌───────────────────┐
 │ Cross-Reference   │  ← Confidence scoring (report count + source diversity
 │     Agent         │     + urgency consensus)
 └────────┬──────────┘
          │  Verified & ranked incidents
          ▼
 ┌───────────────────┐
 │   Flask Dashboard │  ← Map, fact-check, incident cards
 └───────────────────┘
```

---

## Project Structure

```
disaster-relief-agent/
│
├── agents/
│   ├── extract_agent.py          # LLM-based need extraction (Groq)
│   └── dedupe_agent.py           # Deduplication + cross-reference scoring
│
├── data/
│   └── sample_posts.txt          # Input disaster reports (one per line)
│
├── data_collectors/
│   ├── __init__.py
│   └── realtime_simulator.py     # Simulates real-time disaster post streams
│
├── models/
│   └── schema.py                 # Pydantic data models (Need, UniqueIncident)
│
├── outputs/
│   └── verified_incidents.json   # Auto-generated results
│
├── templates/
│   └── index.html                # Flask web dashboard (Leaflet map + Bootstrap)
│
├── app.py                        # Flask web app entry point
├── main.py                       # CLI pipeline runner
├── real_news_disaster_search.py  # Google News + AI hybrid search
├── requirements.txt
└── README.md
```

---

## Installation

### Prerequisites

- Python 3.9+
- A free [Groq API key](https://console.groq.com/)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Sohamexe-tech/disaster-relief-agent.git
cd disaster-relief-agent

# 2. Install dependencies
pip install -r requirements.txt
```

### `requirements.txt`

```
sentence-transformers
scikit-learn
numpy
pydantic
groq
flask
requests
beautifulsoup4
geopy
python-dotenv
```

---

## Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> ⚠️ Never commit your API key. The `.env` file is loaded automatically via `python-dotenv`.

---

## Usage

### Option 1 — CLI Pipeline (batch processing)

```bash
# Step 1: Generate sample disaster posts
python data_collectors/realtime_simulator.py

# Step 2: Run the full deduplication pipeline
python main.py
```

Results are saved to `outputs/verified_incidents.json`.

### Option 2 — Web Dashboard

```bash
python app.py
```

Open your browser at **http://127.0.0.1:5000**

From the dashboard you can:
- Enter a **city name** to search real news + AI-enhanced reports
- Paste a **news URL** to fact-check it (TRUE / FALSE verdict)
- View verified incidents on an **interactive Leaflet map**

### Option 3 — Real-Time Stream Simulation

```bash
python data_collectors/realtime_simulator.py
```

This streams posts to `data/sample_posts.txt` over 30 seconds at 4 posts/minute, then exits. Run `python main.py` afterward to process them.

---

## How It Works

### 1. Data Ingestion
- The **RealtimeSimulator** generates realistic disaster posts using randomized templates with locations across Mumbai (Andheri, Bandra, Kurla, Worli, etc.)
- The **RealNewsDisasterSearch** module fetches live headlines from Google News RSS and optionally supplements them with AI-generated reports when real news is sparse

### 2. LLM Extraction
- Each raw post is sent to **Groq's Llama 3.3 70B** with a structured JSON prompt
- Output fields: `need_type` (food / medical / rescue / shelter / other), `location`, `urgency` (1–5), `summary`
- If the LLM call fails, a keyword-based fallback extracts these fields from the raw text

### 3. Semantic Deduplication
- All summaries are encoded using **`all-MiniLM-L6-v2`** (SentenceTransformers)
- **DBSCAN** clusters embeddings using cosine distance with `eps = 1 - similarity_threshold` (default 0.75)
- Reports within the same cluster are merged into a single **UniqueIncident** with a combined source list and max urgency

### 4. Cross-Reference Scoring

Confidence is calculated on a 0–1 scale:

| Factor | Weight | Logic |
|---|---|---|
| Report count | up to 0.5 | `min(count / 5, 0.5)` |
| Source diversity | up to 0.3 | `min(unique_sources / 3, 0.3)` |
| Urgency consensus | up to 0.2 | Low variance = high consensus |

### 5. Prioritization
- Incidents are sorted by confidence score (descending)
- Visual indicators: 🟢 High (>70%) · 🟡 Medium (40–70%) · 🔴 Low (<40%)

---

## Output Examples

### CLI Output

```
🚨 DISASTER RELIEF RESOURCE SCOUT
======================================================================
✅ Loaded 20 posts from data/sample_posts.txt
✅ Extracted 20 structured needs
✅ Identified 12 unique incidents
📊 Eliminated 8 duplicates (40.0%)

🟢 #1 [INC_B286560D]
   Type: MEDICAL
   Location: Bandra West
   Urgency: 🔴🔴🔴🔴🔴 (5/5)
   Summary: Elderly diabetic needs insulin
   📊 Corroboration: 3 reports from 3 sources
   🎯 Confidence: 100.0%
   📱 Sources: facebook, twitter, instagram
```

### JSON Output (`outputs/verified_incidents.json`)

```json
{
  "timestamp": "2026-01-21T21:13:47.002889",
  "total_reports": 20,
  "unique_incidents": 12,
  "deduplication_rate": "40.0%",
  "incidents": [
    {
      "id": "INC_B286560D",
      "type": "medical",
      "location": "Bandra West",
      "urgency": 5,
      "summary": "Elderly diabetic needs insulin",
      "confidence": "100.0%",
      "report_count": 3,
      "sources": ["facebook", "twitter", "instagram"]
    }
  ]
}
```

---

## Dashboard

The Flask web app provides a visual interface:

- **Search bar** — Enter a city name or paste a news article URL
- **News signals** — Real headlines from Google News
- **AI reports** — LLM-generated scenarios used to fill gaps
- **Incident cards** — Color-coded by urgency with confidence badges
- **Live map** — Geocoded incident pins via Leaflet + OpenStreetMap
- **Fact-checker** — Paste any URL; get a TRUE ✅ / FALSE ❌ / UNKNOWN ⚠️ verdict

---

## Technologies

| Layer | Technology |
|---|---|
| LLM | [Groq](https://groq.com/) — Llama 3.3 70B Versatile |
| Embeddings | [sentence-transformers](https://www.sbert.net/) — `all-MiniLM-L6-v2` |
| Clustering | [scikit-learn](https://scikit-learn.org/) — DBSCAN |
| Data Validation | [Pydantic](https://docs.pydantic.dev/) |
| Web Framework | [Flask](https://flask.palletsprojects.com/) |
| Maps | [Leaflet.js](https://leafletjs.com/) + OpenStreetMap |
| Geocoding | [Geopy](https://geopy.readthedocs.io/) — Nominatim |
| News | Google News RSS |
| UI Styling | [Bootstrap 5](https://getbootstrap.com/) |

---

## Screenshots

### 🌐 Disaster Monitoring Dashboard — City Search
> Enter any city name to pull real news signals, AI-generated reports, and verified incidents.

![Disaster Monitoring Dashboard](screenshots/dashboard_city_search.png)

---

### 📰 Real News Signals (Live)
> Real headlines fetched from Google News RSS — bomb threats, water disruptions, air quality emergencies, and more.

![Real News Signals](screenshots/real_news_signals.png)

---

### 🚨 Verified Actionable Incidents (Web UI)
> Incident cards color-coded by urgency with a full-width red bar indicating severity level (Urgency: 4/5, 5/5).

![Verified Incidents UI](screenshots/verified_incidents_ui.png)

---

### 🗺️ Interactive Map View
> Geocoded incident pins on a Leaflet + OpenStreetMap map. Click any marker to see incident type, summary, and urgency.

![Interactive Map](screenshots/map_view.png)

---

### 💻 CLI Terminal Output
> Full terminal pipeline: incident IDs, type, location, urgency visualization (🔴 dots), corroboration count, and confidence score.

![CLI Output](screenshots/cli_output.png)

---

> 💡 **To add screenshots to your repo**, create a `screenshots/` folder and rename/copy your images as shown above.

---

## Authors

Built for **Disaster Relief Hackathon 2026** 🏆

> *"Our system processes chaotic social media reports and converts them into verified, actionable intelligence through semantic deduplication and multi-source cross-referencing."*

---

## License

MIT License — feel free to use, modify, and distribute.
