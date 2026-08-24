from __future__ import annotations

import io
import os
import tempfile

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schemas.models import (
    AllTimeResponse,
    LeagueInfo,
    MatchupsResponse,
    PlayoffsResponse,
    SagarinResponse,
    StandingsResponse,
    TeamRatingsResponse,
    TeamsResponse,
    WeeklyLeadersResponse,
)

HEADER_BG = colors.HexColor("#2b2d42")
GRID = colors.HexColor("#cbd3e1")
BAND_COLORS = {
    "leader": colors.yellow,
    "playoff": colors.HexColor("#e7f3ff"),
    "bubble": colors.HexColor("#f5f0e6"),
    "out": colors.HexColor("#ffe6ea"),
}


def _doc() -> tuple[io.BytesIO, SimpleDocTemplate, list, object]:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )
    return buffer, doc, [], getSampleStyleSheet()


def _table(elements, styles, heading, headers, rows, col_widths=None, highlights=None):
    elements.append(Paragraph(heading, styles["Heading2"]))
    data = [headers] + rows
    table = Table(data, colWidths=col_widths)
    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8f9fb"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.25, GRID),
    ]
    if highlights:
        for row_idx, color in highlights.items():
            ts.append(("BACKGROUND", (0, row_idx), (-1, row_idx), color))
    table.setStyle(TableStyle(ts))
    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))


def weekly_pdf(
    league: LeagueInfo,
    standings: StandingsResponse,
    matchups: MatchupsResponse,
    teams: TeamsResponse,
    leaders: WeeklyLeadersResponse,
    season_ratings: TeamRatingsResponse,
) -> bytes:
    buffer, doc, elements, styles = _doc()
    elements.append(Paragraph(f"{league.name} — Weekly Report ({league.year})", styles["Title"]))
    elements.append(Paragraph(league.scoring_summary, styles["BodyText"]))
    elements.append(Spacer(1, 0.15 * inch))

    highlights = {row.seed: BAND_COLORS[row.band] for row in standings.rows}
    _table(
        elements,
        styles,
        "League Standings",
        ["Seed", "Team", "Div", "Record", "H2H", "Top6", "Total", "PF", "PA", "Streak"],
        [
            [
                r.seed,
                r.team_name,
                r.division,
                r.record,
                r.h2h_points,
                r.top6_points,
                r.total_points,
                f"{r.points_for:.1f}",
                f"{r.points_against:.1f}",
                r.streak,
            ]
            for r in standings.rows
        ],
        highlights=highlights,
    )

    _table(
        elements,
        styles,
        f"Matchups (Week {matchups.week})",
        ["Home", "Score", "", "Score", "Away"],
        [
            [
                f"{m.home.team_name}{' ★' if m.home.top_n else ''}",
                "" if m.home.score is None else f"{m.home.score:.1f}",
                "vs",
                "" if not m.away or m.away.score is None else f"{m.away.score:.1f}",
                "" if not m.away else f"{m.away.team_name}{' ★' if m.away.top_n else ''}",
            ]
            for m in matchups.matchups
        ],
    )
    elements.append(Paragraph("★ = Top-6 score this week (bonus point)", styles["BodyText"]))
    elements.append(Spacer(1, 0.15 * inch))

    _table(
        elements,
        styles,
        "Team Statistics",
        ["Team", "Avg", "High", "Low"],
        [
            [t.team_name, f"{t.avg_points:.1f}", f"{t.highest_score:.1f}", f"{t.lowest_score:.1f}"]
            for t in teams.teams
        ],
    )
    _table(
        elements,
        styles,
        "Weekly Scoring Leaders",
        ["Week", "Team", "Score"],
        [[l.week, l.team_name, f"{l.score:.1f}"] for l in leaders.leaders],
    )
    _table(
        elements,
        styles,
        "Current Season Ratings (100 = average)",
        ["Team", "Overall+", "PPG+", "Win%+", "PPG", "Record"],
        [
            [
                r.name,
                f"{r.overall_rating:.1f}",
                f"{r.ppg_rating:.1f}",
                f"{r.win_pct_rating:.1f}",
                f"{r.ppg:.1f}",
                f"{r.wins}-{r.losses}",
            ]
            for r in season_ratings.rows
        ],
    )
    doc.build(elements)
    return buffer.getvalue()


def alltime_pdf(history: AllTimeResponse, ratings: TeamRatingsResponse) -> bytes:
    buffer, doc, elements, styles = _doc()
    elements.append(
        Paragraph(f"All-Time Records ({history.start_year}-{history.end_year})", styles["Title"])
    )
    _table(
        elements,
        styles,
        "By owner",
        ["Owner", "Seasons", "W", "L", "Win%", "PF", "PA", "Avg PF", "Avg PA"],
        [
            [
                r.owner_name,
                r.seasons,
                r.wins,
                r.losses,
                f"{r.win_pct:.3f}",
                f"{r.points_for:.1f}",
                f"{r.points_against:.1f}",
                f"{r.avg_pf:.1f}",
                f"{r.avg_pa:.1f}",
            ]
            for r in history.rows
        ],
    )
    _table(
        elements,
        styles,
        "All-time ratings (100 = average)",
        ["Owner", "Overall+", "PPG+", "Win%+", "PPG", "Win%", "Record", "Seasons"],
        [
            [
                r.name,
                f"{r.overall_rating:.1f}",
                f"{r.ppg_rating:.1f}",
                f"{r.win_pct_rating:.1f}",
                f"{r.ppg:.1f}",
                f"{r.win_pct:.3f}",
                f"{r.wins}-{r.losses}",
                r.seasons or "",
            ]
            for r in ratings.rows
        ],
    )
    doc.build(elements)
    return buffer.getvalue()


def sagarin_pdf(league: LeagueInfo, sagarin: SagarinResponse) -> bytes:
    buffer, doc, elements, styles = _doc()
    elements.append(Paragraph(f"{league.name} — Sagarin Ratings ({league.year})", styles["Title"]))
    elements.append(
        Paragraph(
            "Hypothetical every-team-plays-every-team weekly records, scaled so 100 is average. "
            "SOS is the average Sagarin rating of opponents faced.",
            styles["BodyText"],
        )
    )
    highlights = {1: colors.yellow, 2: colors.HexColor("#e7f3ff"), 3: colors.HexColor("#e7f3ff")}
    _table(
        elements,
        styles,
        "Sagarin power ratings",
        ["Rank", "Team", "Rating", "H2H-all", "Avg", "Max", "Min", "SOS"],
        [
            [
                r.rank,
                r.team_name,
                f"{r.sagarin_rating:.1f}",
                r.hypothetical_record,
                f"{r.avg_score:.1f}",
                f"{r.max_score:.1f}",
                f"{r.min_score:.1f}",
                f"{r.strength_of_schedule:.1f}",
            ]
            for r in sagarin.rows
        ],
        highlights=highlights,
    )

    chart = _heatmap_image(sagarin)
    if chart:
        elements.append(Paragraph("Weekly rank heatmap (1 = best)", styles["Heading2"]))
        elements.append(Image(chart, width=7.4 * inch, height=4.4 * inch))
        elements.append(Spacer(1, 0.15 * inch))

    _table(
        elements,
        styles,
        "Sagarin vs traditional ranks",
        ["Team", "Sagarin", "PF", "Win%", "Avg"],
        [[r.team_name, r.rank, r.pf_rank, r.win_pct_rank, r.avg_score_rank] for r in sagarin.rows],
    )
    doc.build(elements)
    if chart and os.path.exists(chart):
        try:
            os.remove(chart)
        except OSError:
            pass
    return buffer.getvalue()


def _heatmap_image(sagarin: SagarinResponse) -> str | None:
    if not sagarin.heatmap or not sagarin.weeks:
        return None
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except Exception:
        return None

    n_teams = len(sagarin.heatmap)
    matrix = []
    names = []
    for row in sagarin.heatmap:
        names.append(row.team_name)
        matrix.append([cell.rank or 0 for cell in row.cells])
    array = np.array(matrix)
    fig, ax = plt.subplots(figsize=(12, max(4, n_teams * 0.45)))
    im = ax.imshow(array, cmap="RdYlGn_r", aspect="auto", vmin=1, vmax=max(n_teams, 1))
    ax.set_xticks(range(len(sagarin.weeks)))
    ax.set_xticklabels([f"W{w}" for w in sagarin.weeks], fontsize=8)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8)
    for i, row in enumerate(sagarin.heatmap):
        for j, cell in enumerate(row.cells):
            if cell.rank:
                ax.text(j, i, str(cell.rank), ha="center", va="center", fontsize=7, fontweight="bold")
    ax.set_title("Weekly performance rank")
    plt.colorbar(im, ax=ax, label="Rank")
    plt.tight_layout()
    handle, path = tempfile.mkstemp(suffix=".png")
    os.close(handle)
    plt.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    return path


def playoffs_pdf(league: LeagueInfo, playoffs: PlayoffsResponse) -> bytes:
    buffer, doc, elements, styles = _doc()
    elements.append(Paragraph(f"{league.name} — Playoff Report ({league.year})", styles["Title"]))
    elements.append(Paragraph(f"Current week: {playoffs.current_week}. If playoffs started today:", styles["BodyText"]))
    _table(
        elements,
        styles,
        "Wild card",
        ["Match", "Teams"],
        [
            [m.label, f"{m.seed1}) {m.team1}" + (f" vs {m.seed2}) {m.team2}" if m.team2 else "")]
            for m in playoffs.wild_card
        ],
    )
    _table(
        elements,
        styles,
        "Semifinals",
        ["Match", "Detail"],
        [[m.label, f"{m.seed1}) {m.team1} {m.note or ''}"] for m in playoffs.semifinals],
    )
    _table(
        elements,
        styles,
        "Championship",
        ["Matchup"],
        [[f"{playoffs.championship.team1} vs {playoffs.championship.team2}"]],
    )
    _table(
        elements,
        styles,
        "Playoff team comparison",
        ["Seed", "Team", "Record", "PF", "PA", "Avg", "Max", "Min", "Win%"],
        [
            [
                p.seed,
                p.team_name,
                p.record,
                f"{p.points_for:.1f}",
                f"{p.points_against:.1f}",
                f"{p.avg_score:.1f}",
                f"{p.max_score:.1f}",
                f"{p.min_score:.1f}",
                f"{p.win_pct:.3f}",
            ]
            for p in playoffs.profiles
        ],
    )
    if playoffs.head_to_head:
        _table(
            elements,
            styles,
            "Head-to-head (playoff teams)",
            ["Team 1", "Team 2", "Record"],
            [[h.team1, h.team2, f"{h.wins}-{h.losses}"] for h in playoffs.head_to_head],
        )
    doc.build(elements)
    return buffer.getvalue()
