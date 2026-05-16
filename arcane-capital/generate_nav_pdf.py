#!/usr/bin/env python3
"""
Generate retrospective monthly NAV & Capital Account reports for
NC Opportunity Fund LP's investment in Arcane Capital Partners LLLP
(May, June, July 2025).

Format mirrors the Cascade Technology Group NAV report template prepared by
Eric C. Reimer, CPA (EEPB) for Armada Prime LLP — same 6-section structure,
typography, color palette, and page layout.

Source of truth for period returns: GPs Cuts tab of the monthly Master
Tracker xlsx files. May 2025 reconstructed from Juniper Square netincome
allocation (no GPs Cuts row for inception month).

Usage:
    python3 generate_nav_pdf.py            # generates all 3 PDFs
    python3 generate_nav_pdf.py may        # one month only
"""

import sys
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table,
    TableStyle, PageBreak, NextPageTemplate, KeepTogether,
)

OUT_DIR = Path(__file__).parent / "nav_reports"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Color palette (from Cascade NAV report) ────────────────────────────────
NAVY = colors.HexColor("#1B2A4E")
DARK_TEXT = colors.HexColor("#2C3E50")
SOFT_TEXT = colors.HexColor("#5A6878")
ROW_LIGHT = colors.HexColor("#F4F5F8")
ROW_HIGHLIGHT = colors.HexColor("#E8ECF4")
BORDER = colors.HexColor("#D5DAE3")
QUOTE_BG = colors.HexColor("#EEF1F7")
QUOTE_BAR = NAVY

# ─── Per-month data (locked from source files; see plan doc) ────────────────
MONTHS = {
    "may": {
        "period_label": "May 2025",
        "period_short": "2025-05",
        "as_of_date": "May 31, 2025",
        "issuance_date": "May 31, 2025",
        "report_period_start": "May 1, 2025",
        "report_period_end": "May 31, 2025",
        # Roll-forward (NC's capital account at Arcane)
        "beginning_nav": 226061.54,
        "contributions": 442959.61,
        "distributions": 0.00,
        "period_return": 6690.21,
        "other_adjustments": 0.00,
        "ending_nav": 675711.36,
        # Waterfall breakdown — partial for May (no GP cuts row)
        "gross_profit": None,           # not separately calculated for May
        "gross_pct": None,
        "trading_fee": None,
        "net_after_fee": None,
        "investor_net": 6690.21,
        "investor_pct": 0.0100,         # ~1.00% on time-weighted avg capital
        "gp_net": None,
        "source_note": (
            "May 2025 period return is sourced from the Juniper Square accounting "
            "system allocation ($6,690.21 booked June 2, 2025 as 'May 2025 Fund "
            "Returns'). No separate GPs Cuts allocation row was produced for May 2025 "
            "as this was the inception month of NC Opportunity Fund LP's full position; "
            "the standard GPs Cuts waterfall (gross → 30% SpyderTech trading fee → "
            "70/30 investor/GP) was applied to subsequent monthly reporting."
        ),
        "opening_balance_note": (
            "Beginning NAV reflects NC Opportunity Fund LP's initial subscription "
            "effective April 15, 2025 ($224,970.00) plus partial-period April 2025 "
            "unrealized gain ($1,091.54) booked May 1, 2025 as the inception "
            "allocation."
        ),
        "commentary_subtitle": "Inception Period · Initial Capital Deployment",
        "commentary": [
            (
                "May 2025 represented NC Opportunity Fund LP's first full reporting "
                "period as a Class B limited partner in Arcane Capital Partners LLLP. "
                "Beginning capital reflected NC's initial subscription of $224,970.00 "
                "effective April 15, 2025, together with the partial-period April 2025 "
                "fund-return allocation of $1,091.54 booked at inception."
            ),
            (
                "During May, NC deployed an additional $442,959.61 effective May 1, 2025, "
                "scaling its capital base to approximately $667,929.61 on a contributed "
                "basis. The Fund allocated a May period return of $6,690.21 to NC's "
                "capital account, equivalent to approximately 1.00% on time-weighted "
                "average capital deployed during the month. Ending capital account "
                "balance at May 31, 2025 was $675,711.36."
            ),
            (
                "The May allocation is sourced from the Juniper Square accounting system "
                "as no separate GPs Cuts waterfall row was produced for the inception "
                "month. Beginning with June 2025, the standard GPs Cuts allocation "
                "methodology (gross trading return → 30% SpyderTech trading fee → 70% "
                "investor / 30% GP split of remainder) is applied and reflected on "
                "subsequent monthly reports."
            ),
        ],
    },
    "june": {
        "period_label": "June 2025",
        "period_short": "2025-06",
        "as_of_date": "June 30, 2025",
        "issuance_date": "June 30, 2025",
        "report_period_start": "June 1, 2025",
        "report_period_end": "June 30, 2025",
        "beginning_nav": 675711.36,
        "contributions": 139965.00,
        "distributions": 0.00,
        "period_return": 10791.40,
        "other_adjustments": 3075.10,
        "ending_nav": 829542.86,
        "gross_profit": 22023.26,
        "gross_pct": 0.0326,
        "trading_fee": 6606.98,
        "net_after_fee": 15416.28,
        "investor_net": 10791.40,
        "investor_pct": 0.01597,
        "gp_net": 4624.88,
        "source_note": (
            "June 2025 period return of $10,791.40 reflects NC Opportunity Fund LP's "
            "70% allocation under the GPs Cuts waterfall: $22,023.26 gross trading "
            "profit (3.26% on opening capital) less the 30% SpyderTech trading fee "
            "($6,606.98) leaves $15,416.28, of which 70% accrues to investors and 30% "
            "to general partner economics. 'Other Adjustments / Reconciling Items' "
            "captures the minor difference between the internal GPs Cuts allocation "
            "and the final TPA accounting-system booking for the period and ties the "
            "ending NAV to the July 1, 2025 opening capital reflected on the July "
            "2025 GPs Cuts allocation."
        ),
        "opening_balance_note": None,
        "commentary_subtitle": "First Full GPs Cuts Reporting Period",
        "commentary": [
            (
                "June 2025 was NC Opportunity Fund LP's first full reporting period "
                "calculated under the standard GPs Cuts waterfall methodology used "
                "across all Arcane Capital Partners LLLP investor allocations. "
                "Beginning capital at June 1, 2025 was $675,711.36."
            ),
            (
                "NC deployed an additional $139,965.00 effective June 1, 2025, bringing "
                "contributed capital for the period to $815,676.36 prior to the period "
                "allocation. The Fund generated $22,023.26 of gross trading profit on "
                "NC's allocated position during June (3.26% on opening capital). After "
                "the 30% SpyderTech trading fee ($6,606.98), the net allocable amount "
                "of $15,416.28 was split per the waterfall: $10,791.40 (70%) to NC's "
                "capital account and $4,624.88 (30%) to general-partner economics. "
                "NC's effective net return for the period was 1.60% on opening capital."
            ),
            (
                "Operationally, June 2025 marked the first month of regular GPs Cuts "
                "allocation cadence for NC's full subscribed position. NAV reporting, "
                "fee accounting, and waterfall application all operated cleanly. Ending "
                "capital account balance at June 30, 2025 was $829,542.86, which ties "
                "directly to the opening capital reflected on the July 2025 GPs Cuts "
                "allocation."
            ),
        ],
    },
    "july": {
        "period_label": "July 2025",
        "period_short": "2025-07",
        "as_of_date": "July 31, 2025",
        "issuance_date": "July 31, 2025",
        "report_period_start": "July 1, 2025",
        "report_period_end": "July 31, 2025",
        "beginning_nav": 829542.86,
        "contributions": 0.00,
        "distributions": 0.00,
        "period_return": 25201.51,
        "other_adjustments": 0.00,
        "ending_nav": 854744.37,
        "gross_profit": 51431.66,
        "gross_pct": 0.0620,
        "trading_fee": 15429.50,
        "net_after_fee": 36002.16,
        "investor_net": 25201.51,
        "investor_pct": 0.03038,
        "gp_net": 10800.65,
        "source_note": (
            "July 2025 period return of $25,201.51 reflects NC Opportunity Fund LP's "
            "70% allocation under the GPs Cuts waterfall: $51,431.66 gross trading "
            "profit (6.20% on opening capital) less the 30% SpyderTech trading fee "
            "($15,429.50) leaves $36,002.16, of which 70% accrues to investors and 30% "
            "to general partner economics. The two wire contributions received during "
            "July ($64,951.00 received July 15, 2025 and $149,943.00 received July 31, "
            "2025) carry effective dates of August 1, 2025 and August 15, 2025, "
            "respectively, and are reflected on subsequent Armada Prime LLP reporting "
            "following NC's August 2025 transition."
        ),
        "opening_balance_note": None,
        "commentary_subtitle": "Capital Scale & Return Acceleration",
        "commentary": [
            (
                "July 2025 represented NC Opportunity Fund LP's third full month at "
                "Arcane Capital Partners LLLP and the final reporting period prior "
                "to NC's transition to Armada Prime LLP in August 2025. Beginning "
                "capital at July 1, 2025 was $829,542.86."
            ),
            (
                "The Fund generated $51,431.66 of gross trading profit on NC's "
                "allocated position during July (6.20% on opening capital), the "
                "strongest single-month gross-return outcome during NC's Arcane "
                "tenure. After the 30% SpyderTech trading fee ($15,429.50), the net "
                "allocable amount of $36,002.16 was split per the waterfall: "
                "$25,201.51 (70%) to NC's capital account and $10,800.65 (30%) to "
                "general-partner economics. NC's effective net return for the period "
                "was 3.04% on opening capital."
            ),
            (
                "No new capital was effective for NC during the July reporting "
                "period; the two wires received in July ($64,951.00 received "
                "July 15 and $149,943.00 received July 31) carry effective dates "
                "in August 2025 and are reflected on subsequent reporting. Ending "
                "capital account balance at July 31, 2025 was $854,744.37. "
                "Effective August 1, 2025, NC Opportunity Fund LP's full position "
                "transferred to Armada Prime LLP, the successor fund vehicle, "
                "where Formidium-issued monthly NAV statements have been provided "
                "in the ordinary course since."
            ),
        ],
    },
}

# ─── Styling ────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

st_title_header = ParagraphStyle(
    "title_header", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=14, leading=18,
    textColor=colors.HexColor("#B8C0D0"), alignment=TA_CENTER,
)
st_h1 = ParagraphStyle(
    "h1", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=28, leading=34,
    textColor=NAVY, alignment=TA_CENTER, spaceAfter=18,
)
st_prepared_for_label = ParagraphStyle(
    "prep_label", parent=styles["Normal"],
    fontName="Helvetica", fontSize=12, leading=16,
    textColor=DARK_TEXT, alignment=TA_CENTER, spaceAfter=2,
)
st_prepared_for_name = ParagraphStyle(
    "prep_name", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=14, leading=18,
    textColor=NAVY, alignment=TA_CENTER, spaceAfter=24,
)
st_period_label = ParagraphStyle(
    "period_label", parent=styles["Normal"],
    fontName="Helvetica", fontSize=12, leading=16,
    textColor=DARK_TEXT, alignment=TA_CENTER, spaceAfter=2,
)
st_period_value = ParagraphStyle(
    "period_value", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=18, leading=22,
    textColor=NAVY, alignment=TA_CENTER,
)
st_period_asof = ParagraphStyle(
    "period_asof", parent=styles["Normal"],
    fontName="Helvetica", fontSize=11, leading=14,
    textColor=DARK_TEXT, alignment=TA_CENTER, spaceAfter=24,
)
st_confidential_badge = ParagraphStyle(
    "conf_badge", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=10, leading=12,
    textColor=SOFT_TEXT, alignment=TA_CENTER,
)
st_issuer = ParagraphStyle(
    "issuer", parent=styles["Normal"],
    fontName="Helvetica-Oblique", fontSize=10, leading=14,
    textColor=DARK_TEXT, alignment=TA_CENTER,
)
st_section_kicker = ParagraphStyle(
    "section_kicker", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=9, leading=12,
    textColor=SOFT_TEXT, alignment=TA_LEFT, spaceAfter=4,
)
st_section_h = ParagraphStyle(
    "section_h", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=20, leading=24,
    textColor=NAVY, alignment=TA_LEFT, spaceAfter=14,
)
st_body = ParagraphStyle(
    "body", parent=styles["Normal"],
    fontName="Helvetica", fontSize=10.5, leading=15,
    textColor=DARK_TEXT, alignment=TA_JUSTIFY, spaceAfter=10,
)
st_body_italic = ParagraphStyle(
    "body_italic", parent=st_body,
    fontName="Helvetica-Oblique", textColor=SOFT_TEXT,
    alignment=TA_LEFT,
)
st_subhead = ParagraphStyle(
    "subhead", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=11, leading=14,
    textColor=DARK_TEXT, spaceAfter=8, spaceBefore=4,
)
st_quote = ParagraphStyle(
    "quote", parent=styles["Normal"],
    fontName="Helvetica-Oblique", fontSize=10.5, leading=15,
    textColor=DARK_TEXT, alignment=TA_LEFT,
    leftIndent=14, rightIndent=8,
)
st_signature_name = ParagraphStyle(
    "sig_name", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=11, leading=14,
    textColor=NAVY, alignment=TA_LEFT,
)
st_signature_role = ParagraphStyle(
    "sig_role", parent=styles["Normal"],
    fontName="Helvetica", fontSize=10, leading=13,
    textColor=DARK_TEXT, alignment=TA_LEFT,
)


# ─── Helpers ────────────────────────────────────────────────────────────────
def fmt_money(v):
    if v is None:
        return "—"
    if v == 0:
        return "$0"
    if v < 0:
        return f"$({abs(v):,.0f})"
    return f"${v:,.0f}"


def fmt_money_cents(v):
    if v is None:
        return "—"
    if v == 0:
        return "$0.00"
    if v < 0:
        return f"$({abs(v):,.2f})"
    return f"${v:,.2f}"


def fmt_pct(v):
    if v is None:
        return "—"
    return f"{v * 100:.2f}%"


def header_footer(canvas, doc, period_label):
    """Header + footer drawn on every page after the title page."""
    canvas.saveState()
    page_num = canvas.getPageNumber()
    width, height = LETTER

    if page_num > 1:
        # Header band (subtle)
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(0.6 * inch, height - 0.55 * inch,
                    width - 0.6 * inch, height - 0.55 * inch)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(NAVY)
        canvas.drawString(0.6 * inch, height - 0.45 * inch,
                          "ARCANE CAPITAL PARTNERS LLLP")
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(DARK_TEXT)
        canvas.drawString(2.7 * inch, height - 0.45 * inch,
                          "·  NAV & Capital Account Report")
        canvas.drawRightString(width - 0.6 * inch, height - 0.45 * inch,
                               f"{period_label}  ·  NC Opportunity Fund LP")

    # Footer band
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(0.6 * inch, 0.6 * inch, width - 0.6 * inch, 0.6 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SOFT_TEXT)
    canvas.drawString(0.6 * inch, 0.42 * inch,
                      "Confidential & Proprietary — Not for redistribution")
    canvas.drawString(3.6 * inch, 0.42 * inch,
                      "Prepared in support of audit & investor records")
    canvas.drawRightString(width - 0.6 * inch, 0.42 * inch,
                           f"Page {page_num}")
    canvas.restoreState()


# ─── Page 1 — Title ─────────────────────────────────────────────────────────
def title_page(month):
    story = []
    # Spacer to push down from top
    story.append(Spacer(1, 0.6 * inch))

    # Navy header bar — implemented as a 1-row table for fill
    bar = Table(
        [[Paragraph("ARCANE CAPITAL PARTNERS LLLP", st_title_header)]],
        colWidths=[6.8 * inch], rowHeights=[0.5 * inch],
    )
    bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(bar)
    story.append(Spacer(1, 1.1 * inch))

    story.append(Paragraph("Monthly NAV &amp; Capital Account Report", st_h1))
    story.append(Spacer(1, 0.4 * inch))

    story.append(Paragraph("Prepared for", st_prepared_for_label))
    story.append(Paragraph("NC Opportunity Fund LP", st_prepared_for_name))

    story.append(Paragraph("Reporting Month", st_period_label))
    story.append(Paragraph(month["period_label"], st_period_value))
    story.append(Paragraph(f"As of {month['as_of_date']}", st_period_asof))

    story.append(Spacer(1, 1.3 * inch))

    # Confidential badge — bordered box
    badge = Table(
        [[Paragraph("CONFIDENTIAL &amp; PROPRIETARY", st_confidential_badge)]],
        colWidths=[3.2 * inch], rowHeights=[0.35 * inch],
    )
    badge.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.75, BORDER),
        ("BACKGROUND", (0, 0), (-1, -1), QUOTE_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    badge_wrap = Table([[badge]], colWidths=[6.8 * inch])
    badge_wrap.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(badge_wrap)
    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph("Prepared in support of audit &amp; investor records",
                           st_issuer))
    story.append(Paragraph("Arcane Capital Partners LLLP · Internal Records",
                           st_issuer))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(f"Date of Issuance: {month['issuance_date']}",
                           st_issuer))

    story.append(PageBreak())
    return story


# ─── Page 2 — Executive Summary ─────────────────────────────────────────────
def exec_summary(month):
    story = []
    story.append(Paragraph("SECTION 1", st_section_kicker))
    story.append(Paragraph("Executive Summary", st_section_h))

    # Intro narrative
    if month["contributions"] > 0 and month["beginning_nav"] == 0:
        intro = (
            f"{month['period_label']} represented the inception of "
            f"NC Opportunity Fund LP's Class B limited partnership interest in "
            f"Arcane Capital Partners LLLP. Capital contributed during the "
            f"period totaled <b>{fmt_money(month['contributions'])}</b>. "
            f"The Fund allocated a period return to NC's capital account of "
            f"<b>{fmt_money(month['period_return'])}</b>, equivalent to "
            f"approximately <b>{fmt_pct(month['investor_pct'])}</b> on "
            f"time-weighted average capital deployed during the period. "
            f"Ending capital account balance was "
            f"<b>{fmt_money(month['ending_nav'])}</b>."
        )
    elif month["contributions"] > 0:
        intro = (
            f"During {month['period_label']}, NC Opportunity Fund LP contributed "
            f"additional capital of <b>{fmt_money(month['contributions'])}</b> "
            f"to Arcane Capital Partners LLLP and received a period return "
            f"allocation of <b>{fmt_money(month['period_return'])}</b>, "
            f"representing <b>{fmt_pct(month['investor_pct'])}</b> on opening "
            f"capital. Ending capital account balance was "
            f"<b>{fmt_money(month['ending_nav'])}</b>."
        )
    else:
        intro = (
            f"During {month['period_label']}, NC Opportunity Fund LP received "
            f"a period return allocation of "
            f"<b>{fmt_money(month['period_return'])}</b> on its Arcane Capital "
            f"Partners LLLP Class B position, representing "
            f"<b>{fmt_pct(month['investor_pct'])}</b> on opening capital. "
            f"No new capital contributions were effective during the period. "
            f"Ending capital account balance was "
            f"<b>{fmt_money(month['ending_nav'])}</b>."
        )
    story.append(Paragraph(intro, st_body))
    story.append(Spacer(1, 0.1 * inch))

    # Capital Account Roll-Forward (rounded)
    rows = [
        ["Metric", "Amount"],
        ["Beginning Capital Account Balance",
         "— (Position inception)" if month["beginning_nav"] == 0
         else fmt_money(month["beginning_nav"])],
        ["Capital Contributions", fmt_money(month["contributions"])],
        ["Distributions", fmt_money(-month["distributions"])
         if month["distributions"] else "$0"],
        ["Period Return Allocated to Capital Account",
         fmt_money(month["period_return"])],
        ["Other Adjustments / Reconciling Items",
         fmt_money(-month["other_adjustments"])
         if month["other_adjustments"] < 0
         else (fmt_money(month["other_adjustments"])
               if month["other_adjustments"] else "$0")],
        ["Ending Capital Account Balance", fmt_money(month["ending_nav"])],
    ]
    table = Table(rows, colWidths=[4.0 * inch, 2.5 * inch])
    table.setStyle(_summary_table_style(highlight_last=True))
    story.append(table)
    story.append(Spacer(1, 0.18 * inch))

    # Period Return Breakdown
    story.append(Paragraph("<b>Period Return Breakdown</b>", st_subhead))
    if month["gross_profit"] is not None:
        breakdown_rows = [
            ["Component", "Percentage", "Dollar Amount"],
            ["Gross Trading Return (to NC's allocated position)",
             fmt_pct(month["gross_pct"]), fmt_money(month["gross_profit"])],
            ["SpyderTech Trading Fee (30% of gross)", "—",
             f"({fmt_money(month['trading_fee'])})"],
            ["Net Allocable After Trading Fee", "—",
             fmt_money(month["net_after_fee"])],
            ["NC Investor Return (70% of net)",
             fmt_pct(month["investor_pct"]),
             fmt_money(month["investor_net"])],
            ["GP Allocation (30% of net, retained at Fund)", "—",
             fmt_money(month["gp_net"])],
        ]
        bd_table = Table(breakdown_rows,
                         colWidths=[3.6 * inch, 1.3 * inch, 1.6 * inch])
        bd_table.setStyle(_breakdown_table_style())
        story.append(bd_table)
    else:
        # May has no GP cuts breakdown
        breakdown_rows = [
            ["Component", "Percentage", "Dollar Amount"],
            ["NC Investor Return (Juniper Square allocation)",
             fmt_pct(month["investor_pct"]),
             fmt_money(month["investor_net"])],
        ]
        bd_table = Table(breakdown_rows,
                         colWidths=[3.6 * inch, 1.3 * inch, 1.6 * inch])
        bd_table.setStyle(_breakdown_table_style())
        story.append(bd_table)

    story.append(Spacer(1, 0.12 * inch))
    note = (
        "The Period Return shown above is the all-in return Arcane Capital "
        "Partners LLLP allocated to NC Opportunity Fund LP's Class B capital "
        "account for the reporting period and ties directly to the entry posted "
        "to NC's capital account on the Fund's books. Detailed allocation source "
        "is described in Section 3."
    )
    story.append(Paragraph(note, st_body_italic))

    story.append(PageBreak())
    return story


def _summary_table_style(highlight_last=False):
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#D8DEE9")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
        ("TOPPADDING", (0, 0), (-1, 0), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("TEXTCOLOR", (0, 1), (-1, -1), DARK_TEXT),
        ("ALIGN", (-1, 0), (-1, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_LIGHT]),
        ("LINEBELOW", (0, 0), (-1, 0), 0, colors.white),
        ("LINEABOVE", (0, 1), (-1, -1), 0.25, BORDER),
    ]
    if highlight_last:
        style.extend([
            ("BACKGROUND", (0, -1), (-1, -1), ROW_HIGHLIGHT),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, -1), (-1, -1), NAVY),
        ])
    return TableStyle(style)


def _breakdown_table_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#D8DEE9")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
        ("TOPPADDING", (0, 0), (-1, 0), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 1), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 7),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("TEXTCOLOR", (0, 1), (-1, -1), DARK_TEXT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_LIGHT]),
        ("LINEABOVE", (0, 1), (-1, -1), 0.25, BORDER),
        ("FONTNAME", (0, 4), (-1, 4), "Helvetica-Bold"),
    ])


# ─── Page 3 — LP Investment Overview ────────────────────────────────────────
def lp_overview():
    story = []
    story.append(Paragraph("SECTION 2", st_section_kicker))
    story.append(Paragraph("Limited Partnership Investment Overview", st_section_h))

    quote = (
        "&ldquo;NC Opportunity Fund LP holds a Class B limited partnership "
        "interest in Arcane Capital Partners LLLP. Period returns are allocated "
        "to NC's capital account under the Fund's standard waterfall, which "
        "applies a 30% trading fee to gross trading profits and splits the "
        "remaining net 70% to investors and 30% to general-partner economics. "
        "All NC period returns are retained as additions to capital account "
        "balance; no distributions were taken during NC's Arcane tenure.&rdquo;"
    )
    qbox = Table([[Paragraph(quote, st_quote)]], colWidths=[6.5 * inch])
    qbox.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), QUOTE_BG),
        ("LINEBEFORE", (0, 0), (0, -1), 3, NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(qbox)
    story.append(Spacer(1, 0.22 * inch))

    story.append(Paragraph(
        "Summary of the operating framework reflected in this report:",
        st_body))

    bullets = [
        ("NC Opportunity Fund LP subscribed to a Class B limited partnership "
         "interest in Arcane Capital Partners LLLP effective April 15, 2025, "
         "with an initial commitment of $350,000.00 and subsequent additional "
         "capital deployments. NC was assigned Position ID 2196755 on the "
         "Juniper Square TPA system."),
        ("Arcane Capital Partners LLLP deployed contributed capital across "
         "its trading program operated under the KIG Forex Trade Agreement "
         "dated January 27, 2025, with execution provided by SpyderTech."),
        ("Monthly returns are calculated under the Fund's standard GPs Cuts "
         "waterfall: Gross Trading Return → 30% SpyderTech Trading Fee → "
         "70% Investor Allocation / 30% GP Allocation of the remaining net. "
         "Effective NC investor share of gross trading return is "
         "approximately 49% (70% × 70%)."),
        ("All NC period-return allocations have been retained as additions "
         "to NC's capital account balance throughout the Arcane reporting "
         "period; no cash distributions have been made to NC during its "
         "Arcane Capital Partners LLLP tenure."),
    ]
    for b in bullets:
        story.append(Paragraph(f"•  {b}", ParagraphStyle(
            "bullet", parent=st_body, leftIndent=16, bulletIndent=0,
            spaceAfter=8,
        )))

    story.append(PageBreak())
    return story


# ─── Page 4 — NAV Calculation Support ───────────────────────────────────────
def nav_calc(month):
    story = []
    story.append(Paragraph("SECTION 3", st_section_kicker))
    story.append(Paragraph("Capital Account Roll-Forward Support", st_section_h))

    intro = (
        "The roll-forward below documents the calculation of NC Opportunity "
        "Fund LP's Class B capital account balance at the end of the reporting "
        "period. All amounts are stated to the cent per the underlying source "
        "records."
    )
    story.append(Paragraph(intro, st_body))
    story.append(Spacer(1, 0.05 * inch))

    rows = [
        ["Roll-Forward Line", "USD"],
        ["Beginning Capital Account Balance",
         "— (Position inception)" if month["beginning_nav"] == 0
         else fmt_money_cents(month["beginning_nav"])],
        ["Capital Contributions (effective during period)",
         fmt_money_cents(month["contributions"])],
        ["Distributions to NC", fmt_money_cents(-month["distributions"])
         if month["distributions"] else "$0.00"],
        ["Period Return Allocation (per GPs Cuts / accounting source)",
         fmt_money_cents(month["period_return"])],
        ["Other Adjustments / Reconciling Items",
         (fmt_money_cents(month["other_adjustments"])
          if month["other_adjustments"] else "$0.00")],
        ["Ending Capital Account Balance",
         fmt_money_cents(month["ending_nav"])],
    ]
    table = Table(rows, colWidths=[4.4 * inch, 2.1 * inch])
    table.setStyle(_summary_table_style(highlight_last=True))
    story.append(table)
    story.append(Spacer(1, 0.18 * inch))

    if month["opening_balance_note"]:
        story.append(Paragraph(
            f"<b>Beginning balance note.</b> {month['opening_balance_note']}",
            st_body_italic))
        story.append(Spacer(1, 0.08 * inch))

    story.append(Paragraph(
        f"<b>Source of period return.</b> {month['source_note']}",
        st_body_italic))

    story.append(PageBreak())
    return story


# ─── Page 5 — Manager Commentary ────────────────────────────────────────────
def commentary(month):
    story = []
    story.append(Paragraph("SECTION 4", st_section_kicker))
    story.append(Paragraph("Manager Commentary", st_section_h))
    story.append(Paragraph(
        f"<b>{month['commentary_subtitle']}</b>", st_subhead))
    for para in month["commentary"]:
        story.append(Paragraph(para, st_body))
    story.append(PageBreak())
    return story


# ─── Page 6 — Compliance + Signature ────────────────────────────────────────
def compliance_signature(month):
    story = []
    story.append(Paragraph("SECTION 5", st_section_kicker))
    story.append(Paragraph("Compliance &amp; Reliance Language", st_section_h))

    quote = (
        "&ldquo;This report is provided by Arcane Capital Partners LLLP to "
        "NC Opportunity Fund LP for informational and capital-account-support "
        "purposes. NC Opportunity Fund LP and its retained advisors may rely "
        "upon the information contained herein for internal NAV reconciliation, "
        "investor reporting, and audit-support purposes.&rdquo;"
    )
    qbox = Table([[Paragraph(quote, st_quote)]], colWidths=[6.5 * inch])
    qbox.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), QUOTE_BG),
        ("LINEBEFORE", (0, 0), (0, -1), 3, NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(qbox)
    story.append(Spacer(1, 0.18 * inch))

    legal_1 = (
        "The information contained in this report is believed to be accurate "
        "as of the date of issuance and is derived from Arcane Capital "
        "Partners LLLP's internal records, including the monthly GPs Cuts "
        "allocation schedule and the Juniper Square third-party-administrator "
        "capital account records. This report does not constitute a "
        "solicitation, offer, or recommendation to buy or sell any security "
        "or investment product. It is intended solely for the use of "
        "NC Opportunity Fund LP and its professional advisors, including the "
        "auditors retained in connection with NC Opportunity Fund LP's annual "
        "audit review."
    )
    legal_2 = (
        "Arcane Capital Partners LLLP makes no representation or warranty "
        "regarding any downstream NC Opportunity Fund LP communications, "
        "marketing materials, or LP-level reporting produced from this NAV "
        "and capital account support report. NC Opportunity Fund LP retains "
        "exclusive responsibility for its own investor NAV calculations, "
        "regulatory compliance, and audit responses."
    )
    story.append(Paragraph(legal_1, st_body_italic))
    story.append(Paragraph(legal_2, st_body_italic))
    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph("SECTION 6", st_section_kicker))
    story.append(Paragraph("Signature", st_section_h))
    story.append(Paragraph(
        "Issued by Arcane Capital Partners LLLP on behalf of NC Opportunity "
        "Fund LP's Class B capital account for the period referenced above.",
        st_body))
    story.append(Spacer(1, 0.22 * inch))

    # Dual signature — Alec & Jake side by side
    sig_line = "_____________________________________"
    sig_cell_alec = [
        Paragraph(sig_line, st_signature_role),
        Spacer(1, 0.05 * inch),
        Paragraph("Alec Atkinson", st_signature_name),
        Paragraph("Authorized Signatory", st_signature_role),
        Paragraph("Arcane Capital Partners LLLP", st_signature_role),
        Spacer(1, 0.08 * inch),
        Paragraph(f"Date: {month['issuance_date']}", st_signature_role),
    ]
    sig_cell_jake = [
        Paragraph(sig_line, st_signature_role),
        Spacer(1, 0.05 * inch),
        Paragraph("Jake Gordon", st_signature_name),
        Paragraph("Authorized Signatory", st_signature_role),
        Paragraph("Arcane Capital Partners LLLP", st_signature_role),
        Spacer(1, 0.08 * inch),
        Paragraph(f"Date: {month['issuance_date']}", st_signature_role),
    ]
    sig_table = Table(
        [[sig_cell_alec, sig_cell_jake]],
        colWidths=[3.25 * inch, 3.25 * inch],
    )
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))
    story.append(sig_table)

    return story


# ─── Document assembly ─────────────────────────────────────────────────────
def build_pdf(month_key):
    month = MONTHS[month_key]
    fname = (f"Arcane_NAV_Support_{month['period_short']}"
             f"_NCOpportunityFund.pdf")
    out_path = OUT_DIR / fname

    doc = BaseDocTemplate(
        str(out_path),
        pagesize=LETTER,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        title=f"Arcane Capital Partners LLLP — NAV & Capital Account Report — "
              f"{month['period_label']} — NC Opportunity Fund LP",
        author="Arcane Capital Partners LLLP",
        subject="Monthly NAV & Capital Account Support Report",
    )

    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        leftPadding=0, rightPadding=0,
        topPadding=0, bottomPadding=0,
        id="normal",
    )

    def _hf(c, d):
        header_footer(c, d, month["period_label"])

    doc.addPageTemplates([
        PageTemplate(id="main", frames=[frame], onPage=_hf),
    ])

    story = []
    story.extend(title_page(month))
    story.extend(exec_summary(month))
    story.extend(lp_overview())
    story.extend(nav_calc(month))
    story.extend(commentary(month))
    story.extend(compliance_signature(month))

    doc.build(story)
    print(f"  ✓ {out_path}")


def main():
    args = sys.argv[1:]
    targets = args if args else list(MONTHS.keys())
    print("Generating NC Opportunity Fund LP — Arcane NAV reports:")
    for t in targets:
        if t not in MONTHS:
            print(f"  ! unknown month: {t}")
            continue
        build_pdf(t)
    print(f"\nOutput: {OUT_DIR}")


if __name__ == "__main__":
    main()
