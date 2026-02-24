# Walker Brain Portal

Streamlit dashboard for AI-powered legal intake call analysis. Visualizes 35+ structured fields extracted from 500-800 daily call transcripts.

## Pages

**Visible (8):**
1. Quote Bank - Searchable caller quotes with quality bands
2. Call Search - Full-text search with chat transcript view and badge pills
3. Transcript Search - RPC-backed transcript search with highlighted snippets
4. Today's Highlights - KPIs, trending quotes, case type distribution
5. Signals & Objections - Clickable tag buttons, objection frequencies
6. Testimonial Pipeline - Candidate review board and workflow visibility
7. Data Explorer - Grouped column browser with humanized headers
8. Pipeline Status - Pipeline status, cost tracking, drift alerts (admin gated)

**Hidden stubs (2):** Case Studies, Clusters

## Setup

```bash
# Clone
git clone https://github.com/alexbespwalker/walker-brain-portal.git
cd walker-brain-portal

# Create secrets
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with real values (see below)

# Install and run
pip install -r requirements.txt
streamlit run app.py
```

### Required secrets (`.streamlit/secrets.toml`)

```toml
[auth]
password = "portal-password-here"
admin_password = "admin-password-here"

[database]
url = "https://beviondsojrrdvknpdbh.supabase.co"
key = "ANON_KEY_HERE"
```

Get the anon key from: Supabase Dashboard > Project `beviondsojrrdvknpdbh` > Settings > API > `anon` `public` key.

## Deploy to Streamlit Cloud

See `context/layers/L4_FRONTEND.md` in the walker_brain project for the full deployment checklist.

## Tech Stack

- **Streamlit** - UI framework
- **Supabase** (PostgREST) - Database via anon key
- **Plotly** - Charts and visualizations
