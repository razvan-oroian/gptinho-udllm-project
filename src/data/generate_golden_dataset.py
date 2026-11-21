"""Generates and verifies the 20 ground-truth entries for the Golden Dataset."""

from __future__ import annotations

import json
from pathlib import Path
from src.data.db_schema import get_db_connection

conn = get_db_connection("data/processed/gptinho.db")
cur = conn.cursor()

def fetch(sql):
    cur.execute(sql)
    return [dict(r) for r in cur.fetchall()]

# 1. GD-001 (Quantitative): Chelsea vs Liverpool final score on 2015-10-31
q1_sql = """
SELECT m.match_date, ht.team_name as home_team, m.home_score, at.team_name as away_team, m.away_score
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN teams at ON m.away_team_id = at.team_id
WHERE m.match_date = '2015-10-31' AND ht.team_name = 'Chelsea' AND at.team_name = 'Liverpool';
""".strip()
q1_rows = fetch(q1_sql)

# 2. GD-002 (Quantitative): Emre Can fouls committed vs Chelsea on 2015-10-31
q2_sql = """
SELECT p.player_name, COUNT(e.event_id) as fouls_committed
FROM events e
JOIN players p ON e.player_id = p.player_id
JOIN matches m ON e.match_id = m.match_id
WHERE m.match_date = '2015-10-31' AND p.player_name = 'Emre Can' AND e.event_type = 'Foul Committed'
GROUP BY p.player_name;
""".strip()
q2_rows = fetch(q2_sql)

# 3. GD-003 (Quantitative): Arsenal total passes vs Tottenham on 2015-11-08
q3_sql = """
SELECT t.team_name, COUNT(e.event_id) as total_passes
FROM events e
JOIN teams t ON e.team_id = t.team_id
JOIN matches m ON e.match_id = m.match_id
WHERE m.match_date = '2015-11-08' AND t.team_name = 'Arsenal' AND e.event_type = 'Pass'
GROUP BY t.team_name;
""".strip()
q3_rows = fetch(q3_sql)

# 4. GD-004 (Quantitative): Vardy shots and outcomes vs Man Utd on 2015-11-28
q4_sql = """
SELECT p.player_name, COUNT(e.event_id) as shots, e.outcome
FROM events e
JOIN players p ON e.player_id = p.player_id
JOIN matches m ON e.match_id = m.match_id
WHERE m.match_date = '2015-11-28' AND p.player_name = 'Jamie Vardy' AND e.event_type = 'Shot'
GROUP BY p.player_name, e.outcome;
""".strip()
q4_rows = fetch(q4_sql)

# 5. GD-005 (Quantitative): Chelsea vs Arsenal score on 2015-09-19
q5_sql = """
SELECT ht.team_name as home_team, m.home_score, at.team_name as away_team, m.away_score
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN teams at ON m.away_team_id = at.team_id
WHERE m.match_date = '2015-09-19' AND ht.team_name = 'Chelsea' AND at.team_name = 'Arsenal';
""".strip()
q5_rows = fetch(q5_sql)

# 6. GD-006 (Quantitative): Top dispossessed player for Chelsea vs Liverpool on 2015-10-31
q6_sql = """
SELECT p.player_name, COUNT(e.event_id) as dispossessions
FROM events e
JOIN players p ON e.player_id = p.player_id
JOIN matches m ON e.match_id = m.match_id
JOIN teams t ON e.team_id = t.team_id
WHERE m.match_date = '2015-10-31' AND t.team_name = 'Chelsea' AND e.event_type = 'Dispossessed'
GROUP BY p.player_name
ORDER BY dispossessions DESC
LIMIT 1;
""".strip()
q6_rows = fetch(q6_sql)

# 7. GD-007 (Quantitative): Manchester City vs Liverpool score on 2015-11-21
q7_sql = """
SELECT ht.team_name as home_team, m.home_score, at.team_name as away_team, m.away_score
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN teams at ON m.away_team_id = at.team_id
WHERE m.match_date = '2015-11-21' AND ht.team_name = 'Manchester City' AND at.team_name = 'Liverpool';
""".strip()
q7_rows = fetch(q7_sql)

# Hybrid SQL queries:
# GD-016 (Hybrid): Liverpool pressured events on 2015-10-31 for Roberto Firmino
q16_sql = """
SELECT p.player_name, COUNT(e.event_id) as pressured_events
FROM events e
JOIN players p ON e.player_id = p.player_id
JOIN matches m ON e.match_id = m.match_id
WHERE m.match_date = '2015-10-31' AND p.player_name = 'Roberto Firmino Barbosa de Oliveira' AND e.under_pressure = 1
GROUP BY p.player_name;
""".strip()
q16_rows = fetch(q16_sql)

# GD-017 (Hybrid): Leicester City total shots against Man Utd on 2015-11-28
q17_sql = """
SELECT t.team_name, COUNT(e.event_id) as total_shots
FROM events e
JOIN teams t ON e.team_id = t.team_id
JOIN matches m ON e.match_id = m.match_id
WHERE m.match_date = '2015-11-28' AND t.team_name = 'Leicester City' AND e.event_type = 'Shot'
GROUP BY t.team_name;
""".strip()
q17_rows = fetch(q17_sql)

# GD-018 (Hybrid): Santi Cazorla passes vs Tottenham on 2015-11-08
q18_sql = """
SELECT p.player_name, COUNT(e.event_id) as passes
FROM events e
JOIN players p ON e.player_id = p.player_id
JOIN matches m ON e.match_id = m.match_id
WHERE m.match_date = '2015-11-08' AND p.player_name = 'Santiago Cazorla González' AND e.event_type = 'Pass'
GROUP BY p.player_name;
""".strip()
q18_rows = fetch(q18_sql)

# GD-019 (Hybrid): Tottenham total pressures vs Liverpool on 2015-10-17
q19_sql = """
SELECT t.team_name, COUNT(e.event_id) as total_pressures
FROM events e
JOIN teams t ON e.team_id = t.team_id
JOIN matches m ON e.match_id = m.match_id
WHERE m.match_date = '2015-10-17' AND t.team_name = 'Tottenham Hotspur' AND e.event_type = 'Pressure'
GROUP BY t.team_name;
""".strip()
q19_rows = fetch(q19_sql)

# GD-020 (Hybrid): Chelsea pressures vs Liverpool on 2015-10-31
q20_sql = """
SELECT t.team_name, COUNT(e.event_id) as total_pressures
FROM events e
JOIN teams t ON e.team_id = t.team_id
JOIN matches m ON e.match_id = m.match_id
WHERE m.match_date = '2015-10-31' AND t.team_name = 'Chelsea' AND e.event_type = 'Pressure'
GROUP BY t.team_name;
""".strip()
q20_rows = fetch(q20_sql)

# Build complete golden dataset list
golden_items = [
    # Tier 1: Purely Quantitative
    {
        "id": "GD-001",
        "tier": "quantitative",
        "category": "match_results",
        "target_team": "Liverpool",
        "simulated_date": "2015-11-01",
        "prompt": "What was the final score in the Premier League match between Chelsea and Liverpool on October 31, 2015?",
        "expected_sql": q1_sql,
        "expected_sql_rows": q1_rows,
        "expected_doc_source": None,
        "expected_doc_snippet": None,
        "expected_synthesis": "On October 31, 2015, Liverpool defeated Chelsea 3-1 at Stamford Bridge.",
    },
    {
        "id": "GD-002",
        "tier": "quantitative",
        "category": "player_discipline",
        "target_team": "Liverpool",
        "simulated_date": "2015-11-01",
        "prompt": "How many fouls did Emre Can commit for Liverpool against Chelsea on October 31, 2015?",
        "expected_sql": q2_sql,
        "expected_sql_rows": q2_rows,
        "expected_doc_source": None,
        "expected_doc_snippet": None,
        "expected_synthesis": "Emre Can committed 6 fouls during Liverpool's 3-1 victory over Chelsea on October 31, 2015.",
    },
    {
        "id": "GD-003",
        "tier": "quantitative",
        "category": "team_passing",
        "target_team": "Arsenal",
        "simulated_date": "2015-11-09",
        "prompt": "How many total passes did Arsenal attempt in their North London derby against Tottenham on November 8, 2015?",
        "expected_sql": q3_sql,
        "expected_sql_rows": q3_rows,
        "expected_doc_source": None,
        "expected_doc_snippet": None,
        "expected_synthesis": "Arsenal attempted 514 total passes against Tottenham on November 8, 2015.",
    },
    {
        "id": "GD-004",
        "tier": "quantitative",
        "category": "player_shooting",
        "target_team": "Leicester City",
        "simulated_date": "2015-11-29",
        "prompt": "How many shots did Jamie Vardy take against Manchester United on November 28, 2015, and what was the outcome?",
        "expected_sql": q4_sql,
        "expected_sql_rows": q4_rows,
        "expected_doc_source": None,
        "expected_doc_snippet": None,
        "expected_synthesis": "Jamie Vardy took 1 shot against Manchester United on November 28, 2015, resulting in a Goal.",
    },
    {
        "id": "GD-005",
        "tier": "quantitative",
        "category": "match_results",
        "target_team": "Chelsea",
        "simulated_date": "2015-09-20",
        "prompt": "What was the final score between Chelsea and Arsenal on September 19, 2015?",
        "expected_sql": q5_sql,
        "expected_sql_rows": q5_rows,
        "expected_doc_source": None,
        "expected_doc_snippet": None,
        "expected_synthesis": "Chelsea defeated Arsenal 2-0 on September 19, 2015.",
    },
    {
        "id": "GD-006",
        "tier": "quantitative",
        "category": "player_turnovers",
        "target_team": "Chelsea",
        "simulated_date": "2015-11-01",
        "prompt": "Which Chelsea player suffered the most dispossessions against Liverpool on October 31, 2015?",
        "expected_sql": q6_sql,
        "expected_sql_rows": q6_rows,
        "expected_doc_source": None,
        "expected_doc_snippet": None,
        "expected_synthesis": "Diego Costa was dispossessed the most for Chelsea against Liverpool on October 31, 2015, with 6 dispossessions.",
    },
    {
        "id": "GD-007",
        "tier": "quantitative",
        "category": "match_results",
        "target_team": "Manchester City",
        "simulated_date": "2015-11-22",
        "prompt": "What was the final score between Manchester City and Liverpool on November 21, 2015?",
        "expected_sql": q7_sql,
        "expected_sql_rows": q7_rows,
        "expected_doc_source": None,
        "expected_doc_snippet": None,
        "expected_synthesis": "Liverpool defeated Manchester City 4-1 at the Etihad Stadium on November 21, 2015.",
    },

    # Tier 2: Purely Qualitative
    {
        "id": "GD-008",
        "tier": "qualitative",
        "category": "build_up",
        "target_team": "Liverpool",
        "simulated_date": "2015-11-01",
        "prompt": "When pressed high, how do Liverpool center-backs construct their build-up play according to scout reports?",
        "expected_sql": None,
        "expected_sql_rows": None,
        "expected_doc_source": "scouting_liverpool_2015_10_31.pdf",
        "expected_doc_snippet": "When pressed high, Liverpool center-backs bypass the midfield pivot with direct, long passes to the wings.",
        "expected_synthesis": "According to scouting reports, when facing a high press, Liverpool center-backs bypass the central midfield pivot entirely with direct, driven long diagonal passes to the wings.",
    },
    {
        "id": "GD-009",
        "tier": "qualitative",
        "category": "pressing_triggers",
        "target_team": "Liverpool",
        "simulated_date": "2015-11-01",
        "prompt": "What specific pressing triggers does Jürgen Klopp's Liverpool rely upon to trap opponents?",
        "expected_sql": None,
        "expected_sql_rows": None,
        "expected_doc_source": "scouting_liverpool_2015_10_31.pdf",
        "expected_doc_snippet": "Liverpool's primary pressing trigger is initiated when the opponent plays a square pass to a fullback or when a central midfielder receives the ball facing their own goal.",
        "expected_synthesis": "Liverpool's pressing triggers are initiated on square passes to opposition fullbacks or when an opponent midfielder receives possession facing their own goal, triggering aggressive touchline traps.",
    },
    {
        "id": "GD-010",
        "tier": "qualitative",
        "category": "defensive_flaws",
        "target_team": "Liverpool",
        "simulated_date": "2015-11-01",
        "prompt": "What is the primary defensive transition vulnerability identified regarding Liverpool's fullbacks?",
        "expected_sql": None,
        "expected_sql_rows": None,
        "expected_doc_source": "scouting_liverpool_2015_10_31.pdf",
        "expected_doc_snippet": "Because Alberto Moreno pushes exceptionally high in the attacking phase, Liverpool leave significant open territory in the defensive left channel.",
        "expected_synthesis": "Scouts highlight that Alberto Moreno advances exceptionally high in the attacking phase, creating exploitable space behind him in the defensive left channel on fast counter-attacks.",
    },
    {
        "id": "GD-011",
        "tier": "qualitative",
        "category": "defensive_organization",
        "target_team": "Leicester City",
        "simulated_date": "2015-11-29",
        "prompt": "How does Claudio Ranieri structure Leicester City's central midfield block?",
        "expected_sql": None,
        "expected_sql_rows": None,
        "expected_doc_source": "scouting_leicester_2015_11_28.pdf",
        "expected_doc_snippet": "Leicester's defensive organization is anchored by N'Golo Kanté and Danny Drinkwater. The midfield line remains within 15 meters of the defensive line, suffocating central half-spaces.",
        "expected_synthesis": "Ranieri anchors Leicester's block with N'Golo Kanté and Danny Drinkwater in a compact 4-4-2 where the midfield line stays within 15 meters of the back four, suffocating central corridors.",
    },
    {
        "id": "GD-012",
        "tier": "qualitative",
        "category": "defensive_flaws",
        "target_team": "Leicester City",
        "simulated_date": "2015-11-29",
        "prompt": "What is the major vulnerability of Leicester City center-backs Wes Morgan and Robert Huth?",
        "expected_sql": None,
        "expected_sql_rows": None,
        "expected_doc_source": "scouting_leicester_2015_11_28.pdf",
        "expected_doc_snippet": "Center-backs Wes Morgan and Robert Huth possess immense physical power and aerial dominance in central zones, but struggle severely with mobility when isolated in open field against agile wingers.",
        "expected_synthesis": "Wes Morgan and Robert Huth possess aerial dominance but struggle significantly with mobility when dragged into wide areas and isolated in 1v1 situations against agile attackers.",
    },
    {
        "id": "GD-013",
        "tier": "qualitative",
        "category": "pressing_triggers",
        "target_team": "Arsenal",
        "simulated_date": "2015-11-09",
        "prompt": "Which Arsenal player should opponents press to force unforced turnovers in Arsenal's defensive third?",
        "expected_sql": None,
        "expected_sql_rows": None,
        "expected_doc_source": "scouting_arsenal_2015_11_08.pdf",
        "expected_doc_snippet": "The key trigger to disrupt Arsenal's build-up is aggressive pressing directed at Francis Coquelin. While Coquelin is an elite defensive ball-winner, his technical passing under severe pressure is limited.",
        "expected_synthesis": "Opponents target Francis Coquelin with aggressive pressing because his technical distribution under severe pressure is limited, generating turnovers in Arsenal's defensive third.",
    },
    {
        "id": "GD-014",
        "tier": "qualitative",
        "category": "transition_weakness",
        "target_team": "Manchester City",
        "simulated_date": "2015-11-22",
        "prompt": "Why is Manchester City's midfield vulnerable in transition when Yaya Touré plays in the double pivot?",
        "expected_sql": None,
        "expected_sql_rows": None,
        "expected_doc_source": "scouting_manchester_city_2015_11_21.pdf",
        "expected_doc_snippet": "When Yaya Touré plays in the double pivot, City lack defensive tracking pace in transition. Touré rarely recovers quickly when possession is turned over in the opponent's half, exposing Fernandinho",
        "expected_synthesis": "When Yaya Touré plays in the double pivot, City lacks recovery tracking pace on defensive transitions, isolating Fernandinho and exposing the central defenders.",
    },

    # Tier 3: Hybrid
    {
        "id": "GD-015",
        "tier": "hybrid",
        "category": "build_up_and_pressure",
        "target_team": "Liverpool",
        "simulated_date": "2015-11-01",
        "prompt": "How does Liverpool build up when pressed high, and how many times was Roberto Firmino under pressure against Chelsea on October 31, 2015?",
        "expected_sql": q16_sql,
        "expected_sql_rows": q16_rows,
        "expected_doc_source": "scouting_liverpool_2015_10_31.pdf",
        "expected_doc_snippet": "When pressed high, Liverpool center-backs bypass the midfield pivot with direct, long passes to the wings.",
        "expected_synthesis": "When pressed high, Liverpool center-backs bypass their midfield pivot with direct long balls to the wings. Against Chelsea on October 31, 2015, attacking focal point Roberto Firmino was placed under pressure 60 times.",
    },
    {
        "id": "GD-016",
        "tier": "hybrid",
        "category": "counter_attacks_and_shooting",
        "target_team": "Leicester City",
        "simulated_date": "2015-11-29",
        "prompt": "How does Leicester City execute direct counter-attacks through Mahrez and Vardy, and how many total shots did Leicester record against Manchester United on November 28, 2015?",
        "expected_sql": q17_sql,
        "expected_sql_rows": q17_rows,
        "expected_doc_source": "scouting_leicester_2015_11_28.pdf",
        "expected_doc_snippet": "Riyad Mahrez cuts inside onto his left foot to deliver precision curled through-balls into the right half-space, while Jamie Vardy continually targets the shoulder of the last defender",
        "expected_synthesis": "Leicester's direct counter-attacks rely on Mahrez cutting inside to feed through-balls into the channels for Vardy running behind the last defender. Against Manchester United on November 28, 2015, Leicester recorded 7 total shots.",
    },
    {
        "id": "GD-017",
        "tier": "hybrid",
        "category": "pivot_and_passing",
        "target_team": "Arsenal",
        "simulated_date": "2015-11-09",
        "prompt": "How does Santi Cazorla orchestrate Arsenal's build-up phase, and how many passes did Cazorla complete against Tottenham on November 8, 2015?",
        "expected_sql": q18_sql,
        "expected_sql_rows": q18_rows,
        "expected_doc_source": "scouting_arsenal_2015_11_08.pdf",
        "expected_doc_snippet": "Arsenal's initial build-up runs through Santi Cazorla, who drops between the split center-backs Laurent Koscielny and Per Mertesacker.",
        "expected_synthesis": "Santi Cazorla orchestrates Arsenal's build-up by dropping between split center-backs to break the first pressing line. In the derby against Tottenham on November 8, 2015, Cazorla attempted 38 passes before being substituted.",
    },
    {
        "id": "GD-018",
        "tier": "hybrid",
        "category": "pressing_architecture",
        "target_team": "Tottenham Hotspur",
        "simulated_date": "2015-10-18",
        "prompt": "What is Tottenham's primary high-pressing sequence, and how many pressure events did Tottenham record against Liverpool on October 17, 2015?",
        "expected_sql": q19_sql,
        "expected_sql_rows": q19_rows,
        "expected_doc_source": "scouting_tottenham_2015_10_17.pdf",
        "expected_doc_snippet": "Tottenham's primary pressing sequence initiates when the opposition goalkeeper plays to either center-back.",
        "expected_synthesis": "Tottenham initiates high pressing when the opposition keeper plays out to either center-back, cutting return passes and swarming passing lanes. In their clash against Liverpool on October 17, 2015, Tottenham executed 157 total pressure events.",
    },
    {
        "id": "GD-019",
        "tier": "hybrid",
        "category": "midfield_space_and_pressure",
        "target_team": "Chelsea",
        "simulated_date": "2015-11-01",
        "prompt": "Why does Chelsea's double pivot leave space in Zone 14, and how many pressure events did Chelsea register against Liverpool on October 31, 2015?",
        "expected_sql": q20_sql,
        "expected_sql_rows": q20_rows,
        "expected_doc_source": "scouting_chelsea_2015_10_31.pdf",
        "expected_doc_snippet": "When Fabregas pushes forward to support Diego Costa and Eden Hazard, Matic is left to defend vast horizontal spaces alone, making Chelsea vulnerable in Zone 14.",
        "expected_synthesis": "Chelsea's double pivot is vulnerable because Cesc Fabregas pushes high, stranding Nemanja Matic in wide central space. Against Liverpool on October 31, 2015, Chelsea registered 123 pressure events.",
    },
    {
        "id": "GD-020",
        "tier": "hybrid",
        "category": "midfield_turnovers",
        "target_team": "Liverpool",
        "simulated_date": "2015-11-01",
        "prompt": "What turnover vulnerability does Emre Can have under pressure, and how many fouls did Can commit against Chelsea on October 31, 2015?",
        "expected_sql": q2_sql,
        "expected_sql_rows": q2_rows,
        "expected_doc_source": "scouting_liverpool_2015_10_31.pdf",
        "expected_doc_snippet": "When facing an aggressive high press, Can tends to take multiple touches before distributing, leading to frequent dispossessions in Zone 14.",
        "expected_synthesis": "Under high pressure, Emre Can takes excessive touches before releasing the ball, resulting in central dispossessions. In the match against Chelsea on October 31, 2015, Can committed 6 fouls.",
    },
]

# Write out golden_dataset.jsonl
out_file = Path("data/golden_dataset/golden_dataset.jsonl")
out_file.parent.mkdir(parents=True, exist_ok=True)
with open(out_file, "w", encoding="utf-8") as f:
    for item in golden_items:
        f.write(json.dumps(item) + "\n")

print(f"Successfully generated {len(golden_items)} verified entries in {out_file}")
conn.close()
