# GPTinho - AI Tactical Football Assistant

GPTinho is an AI-powered tactical assistant tailored for football coaching staff and analysts. It unifies quantitative match event data with qualitative scouting intelligence using a local SLM reasoning agent and Model Context Protocol (MCP).

---

## Architecture Overview

```
                      +-------------------+
                      | Football Manager  |
                      +---------+---------+
                                |
                                v
                      +-------------------+
                      |   Frontend UI     |
                      | (Matchday Context)|
                      +---------+---------+
                                |
                                v
                      +-------------------+
                      |    MCP Server     |
                      +---+-----------+---+
                          |           |
            +-------------+           +-------------+
            |                                       |
            v                                       v
+-----------------------+               +-----------------------+
|  Text-to-SQL Engine   |               |   Vector RAG Engine   |
| (StatsBomb SQLite DB) |               | (ChromaDB + Scouting) |
+-----------------------+               +-----------------------+
```

---

## Phase 1: Data & Infrastructure (Complete)

### 1. Relational SQL Database (`data/processed/gptinho.db`)
- Anchored to the **2015/2016 English Premier League** open dataset from StatsBomb.
- Fully normalized and indexed SQLite schema:
  - `teams`: 20 clubs
  - `matches`: 380 matches (100% season coverage)
  - `players`: 549 players
  - `events`: 1,313,773 granular tactical events (passes, pressures, dispossessions, shots, recoveries)
- Specialized indices for Text-to-SQL performance: `idx_events_match`, `idx_events_team_type`, `idx_events_player_pressure`, `idx_matches_date`.

### 2. Tactical Scouting Reports & Vector Store (`data/chromadb`)
- Realistic tactical scouting dossiers compiled as PDFs in `data/raw/scouting_reports/`:
  - **Liverpool FC** (Klopp's build-up mechanics, wing progression, Can's midfield vulnerabilities)
  - **Leicester City** (Ranieri's compact 4-4-2, Vardy-Mahrez transitions, Huth/Morgan mobility)
  - **Arsenal FC** (Cazorla pivot, Coquelin pressing trigger, Bellerin transition space)
  - **Tottenham Hotspur** (Pochettino high press triggers, Dembélé press resistance)
  - **Chelsea FC** (Mourinho midfield spacing, Matic/Fabregas pivot disconnect)
  - **Manchester City** (Pellegrini 2-4-4, Touré tracking transition vulnerabilities)
- Recursive character text chunking (~1000 characters with natural paragraph breaks).
- Ingested into local ChromaDB collection `tactical_scouting_reports` with strict metadata pre-filtering (`team`, `opponent`, `match_date`, `scout`).

### 3. Golden Dataset (`data/golden_dataset/golden_dataset.jsonl`)
- 20 verified ground-truth entries across three tiers:
  - **Purely Quantitative**: Text-to-SQL queries with 100% verified row matches against `gptinho.db`.
  - **Purely Qualitative**: Scout intelligence queries verified via ChromaDB semantic retrieval.
  - **Hybrid**: Dual retrieval queries verifying both SQL row outputs and qualitative scouting paragraphs.
- Automated validation suite: `src/data/validate_golden_dataset.py`.

---

## Getting Started

### Installation
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
python -m pytest tests/ -v
```

### Validate Golden Dataset
```bash
python src/data/validate_golden_dataset.py
```

### Re-generate Scouting PDFs and Re-index Vector DB
```bash
python src/data/scouting_generator.py
python -c "from src.rag import load_all_scouting_pdfs, chunk_all_reports, ScoutingVectorStore; vs = ScoutingVectorStore(); vs.reset(); vs.add_chunks(chunk_all_reports(load_all_scouting_pdfs()))"
```
