"""Generates authentic tactical scouting PDF reports for the 2015/2016 Premier League season."""

from __future__ import annotations

import logging
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOUTING_REPORTS_DATA = [
    {
        "filename": "scouting_liverpool_2015_10_31.pdf",
        "team": "Liverpool",
        "opponent": "Chelsea",
        "match_date": "2015-10-31",
        "scout": "Ian Graham (Tactical Intelligence Unit)",
        "fixture": "Chelsea vs Liverpool - Premier League Matchday 11",
        "sections": [
            (
                "Executive Summary & Structural Setup",
                "Under Jürgen Klopp's 4-3-2-1 / 4-2-3-1 framework, Liverpool exhibit extreme spatial compression without the ball, prioritizing immediate verticality upon ball recovery. In sustained possession, they alternate between short central interplay and sudden direct switches to advancing wingbacks Alberto Moreno and Nathaniel Clyne."
            ),
            (
                "Build-up Mechanics & Pressing Resistance",
                "When pressed high, Liverpool center-backs bypass the midfield pivot with direct, long passes to the wings. Rather than circulating slowly through Lucas Leiva or Emre Can, Mamadou Sakho and Martin Skrtel are instructed to bypass the first two pressing lines with driven diagonal balls into the channels for Roberto Firmino and Philippe Coutinho to contest the second ball."
            ),
            (
                "Midfield Turnover Vulnerabilities",
                "Emre Can serves as the physical anchor in midfield transitions, but demonstrates consistent vulnerability when pressed from his blindside. When facing an aggressive high press, Can tends to take multiple touches before distributing, leading to frequent dispossessions in Zone 14. Opponents should target Can immediately upon receipt when his back is turned to the attacking goal."
            ),
            (
                "Pressing Triggers & Gegenpressing",
                "Liverpool's primary pressing trigger is initiated when the opponent plays a square pass to a fullback or when a central midfielder receives the ball facing their own goal. Adam Lallana and James Milner immediately swarm the receiver from blind angles, creating a touchline trap designed to force hasty clearances or direct turnovers."
            ),
            (
                "Defensive Transition Vulnerabilities",
                "Because Alberto Moreno pushes exceptionally high in the attacking phase, Liverpool leave significant open territory in the defensive left channel. Rapid vertical counter-attacks targeted into the space behind Moreno before Sakho can rotate across represent their most exploitable defensive flaw."
            ),
        ]
    },
    {
        "filename": "scouting_leicester_2015_11_28.pdf",
        "team": "Leicester City",
        "opponent": "Manchester United",
        "match_date": "2015-11-28",
        "scout": "Steve Walsh (Head of Recruitment)",
        "fixture": "Leicester City vs Manchester United - Premier League Matchday 14",
        "sections": [
            (
                "Executive Summary & Structural Setup",
                "Claudio Ranieri has organized Leicester City into a rigid, compact 4-4-2 mid/low block that intentionally surrenders possession in favor of explosive transition corridors. They operate with an exceptionally narrow back four and rely on rapid vertical feeds."
            ),
            (
                "Defensive Shape & Central Trap",
                "Leicester's defensive organization is anchored by N'Golo Kanté and Danny Drinkwater. The midfield line remains within 15 meters of the defensive line, suffocating central half-spaces. Kanté acts as a free-roaming ball-winner, stepping up to intercept penetrating passes while Drinkwater covers the second line."
            ),
            (
                "Direct Counter-Attacking Mechanics",
                "Upon winning possession, Leicester require an average of fewer than 4 passes to register an effort on goal. Riyad Mahrez cuts inside onto his left foot to deliver precision curled through-balls into the right half-space, while Jamie Vardy continually targets the shoulder of the last defender with blindside sprint runs."
            ),
            (
                "Pressing Resistance & Build-up Limitations",
                "Leicester do not engage in elaborate short build-up play from Kasper Schmeichel. Facing a high press, Schmeichel will reliably bypass pressure with direct drop-kicks targeted towards Shinji Okazaki or Leonardo Ulloa to contest aerial duels."
            ),
            (
                "Defensive Vulnerabilities",
                "Center-backs Wes Morgan and Robert Huth possess immense physical power and aerial dominance in central zones, but struggle severely with mobility when isolated in open field against agile wingers. Isolating Morgan in 1v1 situations in wide channels produces high-percentage attacking chances."
            ),
        ]
    },
    {
        "filename": "scouting_arsenal_2015_11_08.pdf",
        "team": "Arsenal",
        "opponent": "Tottenham Hotspur",
        "match_date": "2015-11-08",
        "scout": "Gilles Grimandi (Chief European Scout)",
        "fixture": "Arsenal vs Tottenham Hotspur - Premier League Matchday 12",
        "sections": [
            (
                "Executive Summary & Tactical Philosophy",
                "Arsène Wenger's Arsenal deploy a fluid 4-2-3-1 focused on possession dominance, positional interchanges in the half-spaces, and patient breakdown of opposition defensive blocks through quick one-touch combinations."
            ),
            (
                "Build-up Phase & Midfield Pivot",
                "Arsenal's initial build-up runs through Santi Cazorla, who drops between the split center-backs Laurent Koscielny and Per Mertesacker. Cazorla's ambipedal passing enables Arsenal to break central presses with ease, connecting directly into Mesut Özil drifting between defensive lines."
            ),
            (
                "Pressing Triggers & Exploitable Weaknesses",
                "The key trigger to disrupt Arsenal's build-up is aggressive pressing directed at Francis Coquelin. While Coquelin is an elite defensive ball-winner, his technical passing under severe pressure is limited. Forcing Cazorla to pass to Coquelin while cutting off Cazorla's return passing lane creates regular unforced turnovers in Arsenal's defensive third."
            ),
            (
                "Defensive Transition Gaps",
                "With Hector Bellerin instructed to overlap aggressively into the final third, Arsenal's right defensive flank is frequently left unprotected. Mertesacker's lack of lateral recovery pace makes Arsenal vulnerable to direct counter-attacking balls played into the channel behind Bellerin."
            ),
        ]
    },
    {
        "filename": "scouting_tottenham_2015_10_17.pdf",
        "team": "Tottenham Hotspur",
        "opponent": "Liverpool",
        "match_date": "2015-10-17",
        "scout": "Paul Mitchell (Head of Recruitment & Analysis)",
        "fixture": "Tottenham Hotspur vs Liverpool - Premier League Matchday 9",
        "sections": [
            (
                "Executive Summary & Pressing Architecture",
                "Mauricio Pochettino has implemented an aggressive high-tempo 4-2-3-1 characterized by synchronized front-foot pressing, relentless physical dueling, and rapid vertical progression through Christian Eriksen and Dele Alli."
            ),
            (
                "High-Pressing Triggers",
                "Tottenham's primary pressing sequence initiates when the opposition goalkeeper plays to either center-back. Harry Kane cuts off the return pass to the keeper, while Son Heung-min and Erik Lamela pinch inward to compress the passing lanes to the fullbacks. Eric Dier and Mousa Dembélé step aggressively up to midfield duels."
            ),
            (
                "Build-up & Midfield Resistance",
                "Mousa Dembélé is Tottenham's primary pressure release valve, capable of shielding the ball and dribbling out of tight central pressure. Attempts to press Dembélé directly rarely succeed; teams must instead press his passing targets."
            ),
            (
                "Defensive Vulnerabilities",
                "Tottenham maintain an aggressive high defensive line. When the front press is bypassed via third-man combinations, Jan Vertonghen and Toby Alderweireld can be caught on the turn by pace-based attackers running from deep positions."
            ),
        ]
    },
    {
        "filename": "scouting_chelsea_2015_10_31.pdf",
        "team": "Chelsea",
        "opponent": "Liverpool",
        "match_date": "2015-10-31",
        "scout": "Piet de Visser (Technical Advisor)",
        "fixture": "Chelsea vs Liverpool - Premier League Matchday 11",
        "sections": [
            (
                "Executive Summary & Tactical Crisis",
                "José Mourinho's side operates in a 4-2-3-1 that has shown severe defensive instability throughout early 2015/2016. The team struggles to coordinate defensive transitions, leading to dangerous disconnects between the back four and midfield double pivot."
            ),
            (
                "Midfield Defensive Gaps",
                "The double pivot of Nemanja Matic and Cesc Fabregas lacks the defensive coverage of previous campaigns. When Fabregas pushes forward to support Diego Costa and Eden Hazard, Matic is left to defend vast horizontal spaces alone, making Chelsea vulnerable in Zone 14."
            ),
            (
                "Attacking Threats & Over-Reliance on Willian",
                "Willian has been Chelsea's most reliable attacking outlet, driving through transition phases and posing lethal set-piece delivery. Eden Hazard frequently drifts inside from the left wing, searching for isolation dribbles against opposing right-backs."
            ),
            (
                "Defensive Fragility Against High Intensity",
                "Branislav Ivanovic and Gary Cahill have struggled against high-intensity pressing teams. When pressured into hasty back-passes, Asmir Begovic is forced to kick long, resulting in low ball retention rates."
            ),
        ]
    },
    {
        "filename": "scouting_manchester_city_2015_11_21.pdf",
        "team": "Manchester City",
        "opponent": "Liverpool",
        "match_date": "2015-11-21",
        "scout": "Txiki Begiristain (Director of Football)",
        "fixture": "Manchester City vs Liverpool - Premier League Matchday 13",
        "sections": [
            (
                "Executive Summary & Structural Profile",
                "Manuel Pellegrini's Manchester City utilize an expansive 4-2-3-1 that shifts into a 2-4-4 in possession. Kevin De Bruyne, David Silva, and Raheem Sterling offer supreme creative combination play in the final third behind Sergio Agüero."
            ),
            (
                "Build-up Phase Mechanics",
                "City build patiently from the back with Vincent Kompany or Martin Demichelis connecting through Fernandinho. De Bruyne and Silva roam dynamically across both half-spaces, pulling opponent defensive markers out of shape to create shooting lanes."
            ),
            (
                "Transition Weakness in Midfield",
                "When Yaya Touré plays in the double pivot, City lack defensive tracking pace in transition. Touré rarely recovers quickly when possession is turned over in the opponent's half, exposing Fernandinho and forcing the center-backs into 2v2 counter-attacking duels."
            ),
            (
                "Exploitable Flank Space",
                "Bacary Sagna and Aleksandar Kolarov commit high into the final third. Fast counter-attacks initiated into the wide areas directly behind City's fullbacks create immediate 2v1 overloads against their retreating central defenders."
            ),
        ]
    }
]


def generate_scouting_pdf(report: dict, output_path: Path) -> Path:
    """Generate a clean, structured PDF scouting report document."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        "ReportMeta",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#4A5568"),
    )
    section_head_style = ParagraphStyle(
        "SectionHead",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=8,
    )

    story = []
    # Title & Header
    story.append(Paragraph(f"Tactical Scouting Dossier: {report['team']}", title_style))
    story.append(Paragraph(f"<b>Fixture:</b> {report['fixture']}", meta_style))
    story.append(Paragraph(f"<b>Match Date:</b> {report['match_date']} | <b>Opposition:</b> {report['opponent']}", meta_style))
    story.append(Paragraph(f"<b>Lead Analyst:</b> {report['scout']} | <b>Classification:</b> CLUB CONFIDENTIAL", meta_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#CBD5E0"), spaceAfter=10))

    # Sections
    for heading, text in report["sections"]:
        story.append(Paragraph(heading, section_head_style))
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    logger.info("Generated PDF report: %s", output_path)
    return output_path


def generate_all_reports(output_dir: Path | str = "data/raw/scouting_reports") -> list[Path]:
    """Generate all standard tactical scouting PDF reports."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    generated = []
    for rep in SCOUTING_REPORTS_DATA:
        file_path = out / rep["filename"]
        generate_scouting_pdf(rep, file_path)
        generated.append(file_path)
    logger.info("Generated %d tactical scouting PDF reports in %s", len(generated), out)
    return generated


if __name__ == "__main__":
    generate_all_reports()
