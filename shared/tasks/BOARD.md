# Task Board

## To Do
- [AC] Phase 2: collect 15–20 Alec writing samples → drop in `accelerated-os/draft_engine/samples/` → fill out `voice_style_guide.md`
- [AC] Phase 2: build `lp_notes/generate.py` (per-LP performance note from `data/tpa_history.json`)
- [AC] Phase 2: build `weekly_audit/generate.py` (Friday surfacing of stalled contacts)
- [AC] Phase 2: build metrics dashboard at `accelerated-os/dashboard/index.html` (reuse pattern from `index.html`)
- [AC] Phase 2: replace `WORKFLOW_IDS` placeholders in `accelerated-os/voice_memo/ghl_writeback.py` with real GHL workflow IDs after sequences are wired
- [AC] Manual (Nairne, this weekend): tier the 5K per `accelerated-os/tiering_worksheet.md`
- [AC] Manual (Nairne, this week): wire GHL custom fields, pipelines, sequences per `accelerated-os/GHL_CONFIG_SPEC.md`
- [AC] Manual (Alec/Nairne): set GitHub Secrets — `GHL_API_KEY`, `GHL_LOCATION_ID`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, SMTP_*
- [AC] Manual (Alec/Nairne): create Telegram bot via @BotFather, set webhook OR run polling locally for dev

## In Progress
- [AC] Phase 1 build complete on Claude side (2026-04-30); awaiting GHL config + API keys to go live

## Done
- [Nairne + Claude] Arcane Capital Partners LLLP — retrospective NAV reports for NC Opportunity Fund LP (May, Jun, Jul 2025). 6-section PDFs mirroring Cascade Technology Group NAV format. Source of truth: GPs Cuts tab (June + July) + Juniper Square netincome CSV (May inception). Dual signature: Alec Atkinson + Jake Gordon. Folder: `arcane-capital/` (no auth, plain HTML index + `nav_reports/*.pdf` + `generate_nav_pdf.py`). All 3 reports reconcile end-to-end to Jul 31 ending NAV $854,744.37; cumulative Unrealized G/L $46,849.76 ties to capital account CSV. (2026-05-15)
- [Nairne + Claude] Armada Prime Tech LLC — 2025 year-end reconciliation for 1099s + K-1s. Aggregator (`tools/build_2025_year_end.py`), workbook (`2025-armada-prime-tech-1099-k1.xlsx` with 8 tabs), markdown summary (`2025-armada-prime-tech-summary.md`). Period covered: Aug-Dec 2025 (entity formed at Armada Prime relaunch). Gross income $153,023.03; contractor 1099s $54,491.59; op expenses $91,225 (subject to reclass); Partnership net income +$7,306.44. K-1 partners: Nairne 60% (Fund Mgmt 59.5% + direct 0.5%) + Raj 0.5%. TruQuant excluded entirely per Nairne. (2026-04-30)
- [AC] Phase 1: `accelerated-os/` scaffolded — README, GHL config spec, tiering worksheet, 14 Layer 5 prompt templates, 4 playbooks (milken, la_dinner, nyc_dinner, operating_cadence), voice style guide skeleton, voice memo pipeline (telegram→whisper→claude→GHL), draft engine, approval inbox UI+API, daily brief generator, GH Actions workflows. (2026-04-30)
- [Nairne + Claude] Consultant Splits — TPA-sourced GP pool attribution. Regenerator (`tools/build_consultant_splits.py`), dynamic Excel (`Armada_Consultant_Splits.xlsx`), dashboard (`consultant-splits.html`), data (`data/consultant_splits.json`). Seeded with Mar 2026. Password: `armada2026`. (2026-04-27)
- [Nairne + Claude] Build TPA Reporting Package dashboard — parser (`tools/parse_tpa_report.py`), seeded history (`data/tpa_history.json`), dashboard (`tpa-dashboard.html`). Seeded with Aug 2025. (2026-04-16)
- [Nairne + Claude] Consultant Splits — TPA-sourced GP pool attribution. Regenerator (`tools/build_consultant_splits.py`), dynamic Excel (`Armada_Consultant_Splits.xlsx`), dashboard (`consultant-splits.html`), data (`data/consultant_splits.json`). Seeded with Mar 2026. Password: `armada2026`. (2026-04-27)
- [Nairne + Claude] Build TPA Reporting Package dashboard — parser (`tools/parse_tpa_report.py`), seeded history (`data/tpa_history.json`), dashboard (`tpa-dashboard.html`). Seeded with Aug 2025. (2026-04-16)
