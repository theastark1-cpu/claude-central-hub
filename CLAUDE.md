# Instructions for Claude Code Agents

You are working in a shared repo used by two Claude Code agents: **Thea** and **Amber**.

## Before Starting Any Work
1. Run `git pull` to get the latest changes.
2. Check `shared/tasks/BOARD.md` to see what's in progress.
3. Check `shared/decisions/LOG.md` for recent decisions.

## While Working
- Log decisions in `shared/decisions/LOG.md`.
- Update `shared/tasks/BOARD.md` when you start or finish a task.
- Use your own `agents/<your-name>/` folder for scratch work.
- Don't modify the other agent's folder.

## When Done
1. Commit with a clear message: `[Thea] did X` or `[Amber] did Y`.
2. Push immediately so the other agent can see your changes.

## Conflict Resolution
- Resolve conservatively — don't delete the other agent's work.
- When in doubt, leave a note and flag it for the human.

---

## Fund Dashboard Project

### Overview
- **Fund**: Armada Prime LLP
- **Dashboard**: Single-file HTML dashboard at `index.html` in `claude-central-hub` repo
- **Live URL**: https://theastark1-cpu.github.io/claude-central-hub/
- **GitHub Repo**: https://github.com/theastark1-cpu/claude-central-hub
- **Password**: armada2026 (SHA256 hashed in the HTML)
- **Hosting**: GitHub Pages, deployed from `main` branch

### Data Structure (Monthly Return Spreadsheets)
Each month's .xlsx has these sheets:
- **High Level**: Monthly performance %, entity splits (TruQuant 18%, Fund 82%, GPs 30%, Investor 70%)
- **Contributions & Withdrawals**: Per-investor capital activity with starting units/balance
- **Monthly Roll**: Per-investor cascade performance, TruQuant/Fund/Investor cuts, ending balances
- **GP Distribution**: Per-investor GP amounts split across Fund Mgmt, Raj, Nairne, Phil, and consultant
- **Consultants**: Consultant-level aggregated earnings, expenses, net profit
- **Costs**: Fund operating expenses (Chris, TPA, Insurance, Charalece, etc.)
- **IDS**: Investor ID mapping (TPA ID, Position ID, Consultant assignment)
- **Capital Raised**: Capital raised by each consultant
- **Copy of Investor Capital Summary**: TPA-provided capital summary with NAV, shares, P&L

### Key Business Logic
- **Threshold**: 1.75% gross monthly return triggers waterfall (GP/TQ splits)
- **Below threshold**: Full return passes through to investors, no GP/TQ cuts
- **Waterfall**: Gross → 82% to Fund (Armada Prime Return) → 70% Investor / 30% GP
- **TruQuant**: 18% of gross return
- **GP Distribution**: Fund Mgmt (59.5%), Consultant (39%), Raj/Nairne/Phil (0.5% each)
- **Consultant commission rate**: 39% of their investors' GP allocation

### Consultants
- Alec Atkinson (largest book), Jake Gordon, AJ Affleck, Luke, Isaac, Nikki, Raj (Split)

### Q1 2026 Data (Current as of April 2026)
- **Jan**: 8.70% gross, 4.99% investor, $186,950 GP, $30K expenses, 45 investors, $9.55M AUM
- **Feb**: 1.00% gross (below threshold), 1.00% investor, $0 GP, $16.7K expenses, 50 investors, $10.56M AUM
- **Mar**: 4.20% gross, 2.41% investor, $121,816 GP, $16.7K expenses, 51 investors, $12.07M AUM
- **Q1 YTD**: 14.40% gross, 8.60% investor, $308,766 GP, $63.4K expenses
- **Armada Prime Return (82% of gross)**: Jan 7.13%, Feb 0.82%, Mar 3.44%, Q1 11.81%

### Dashboard Structure
- **Overview tab**: YTD KPIs, month-over-month comparison table, return trend chart, AUM growth chart, consultant capital chart, Q1 summary
- **Jan/Feb/Mar tabs**: Monthly KPIs, return structure split, GP distribution table, money flow bars, expenses
- **Investor Detail tab**: Sortable table with all investors, consultant tags, ending balances, returns, contributions

### Tech Stack
- Single HTML file with inline CSS/JS
- Chart.js for charts
- CryptoJS for password hashing
- DM Sans + JetBrains Mono + Playfair Display fonts
- Dark theme with CSS variables

---

## Accelerated Consulting — Capital Relations OS (`accelerated-os/`)

The operating system for converting Alec Atkinson's ~5K-name UHNW network into systematic capital relationships across Armada Prime LLP and adjacent products. Source: `AlecPlaybook` (April 2026, v1.0). Brand: **Accelerated Consulting** (renamed from "Cipher Strategies" in the source doc).

### Roles
- **Alec Atkinson** — principal. Holds the relationships, takes meetings, records voice memos, sends under his name.
- **Nairne** — operator (Amber-equivalent in the doc). Tiers the database, drafts every follow-up, runs the dinners, owns the system.

### Architecture
- **CRM source-of-truth**: GoHighLevel (already provisioned, ~5K contacts loaded). Wiring spec in `accelerated-os/GHL_CONFIG_SPEC.md`.
- **Intelligence layer**: this repo at `accelerated-os/`.
  - `voice_memo/` — Telegram bot → Whisper → Claude structuring → GHL writeback
  - `draft_engine/` — Claude generates drafts in Alec's voice using prompts in `prompts/` and samples in `samples/`
  - `approval_inbox/` — mobile HTML + FastAPI for swipe approve/edit/reject
  - `daily_brief/`, `lp_notes/`, `newsletter/`, `weekly_audit/` (Phase 2+)
  - `orchestrator/` — GHL API client, tier cadence math, travel-week meeting list builder
- **Scheduling**: GitHub Actions cron (`.github/workflows/accelerated-*.yml`).

### Key files
- `accelerated-os/README.md` — entry point + how a meeting flows through the system
- `accelerated-os/GHL_CONFIG_SPEC.md` — what to wire in GHL (custom fields, pipelines, sequences)
- `accelerated-os/tiering_worksheet.md` — weekend session rubric for tiering the 5K
- `accelerated-os/playbooks/milken.md`, `la_dinner.md`, `nyc_dinner.md`, `operating_cadence.md`
- `accelerated-os/draft_engine/prompts/*.md` — 14 templates from Layer 5 of the playbook
- `accelerated-os/draft_engine/voice_style_guide.md` — voice rules (skeleton; awaits Alec writing samples)
- `~/.claude/plans/users-nairne-downloads-alecplaybook-doc-joyful-gizmo.md` — full build plan, all phases

### Tiers (from playbook)
- **T1** Whales (~50, $5M+): monthly personal touch + quarterly in-person, Alec direct
- **T2** Active (~300, $500K–$5M): monthly cadence, Amber drafts, Alec sends
- **T3** Network (~1,500): quarterly newsletter + ad-hoc warm, Amber automated
- **T4** Archive (~3,150): quarterly newsletter only, fully automated

### Recurring cost
~$1,000–1,200/mo: GHL Agency Pro $497, Claude API $300–500, Whisper $20–30, LinkedIn Sales Nav $99, Notion $16, R2 $5, misc $50. Plus per-dinner $10K × 4–6/yr.

### Required GitHub Secrets (set before workflows run live)
`GHL_API_KEY`, `GHL_LOCATION_ID`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`, `SMTP_PORT`, `BRIEF_RECIPIENTS`, `AUDIT_RECIPIENTS`. All Python modules run in dry-run mode (logging intended actions to `accelerated-os/data/dry_run_ghl.log.jsonl`) when secrets are missing.

### Phase status (2026-04-30)
Phase 1 build is complete on the Claude side. Awaits manual GHL config + tiering session + Secrets to go live. First real stress test is the LA dinner late June 2026 (not Milken — see plan file for posture decision).

---

## Armada Innovations LLC — GP of Armada Capital Group LLP (`armada-innovations/`)

Second fund. **Armada Capital Group LLP** is a new RE/PE-style fund (distinct from Armada Prime LLP). Its General Partner is **Armada Innovations LLC**, owned:

- **Nairne** 60% — Managing Member
- **Alec** 39.5% — Capital Relations
- **Chris** 0.5% — Member (last name TBD)

### Files
- `armada-innovations/index.html` — GP dashboard: ITD distributions, member splits, monthly waterfall.
- `armada-innovations/acg-tpa.html` — ACG LLP TPA dashboard (parallels `tpa-dashboard.html` for Prime).
- `armada-innovations/data/acg_history.json` — single JSON source for both pages. Keys: `fund`, `gp_entity`, `members`, `months[]`.
- `armada-innovations/data/armada-innovations-2026.xlsx` — manual workbook (High Level, Member Distribution, Capital Roll, Fund Source, Source Trail).

### Access
Both pages share password **`innovations-2026`** and `ai_auth` session key. Different from Armada Prime's `armada-tpa-2026` / `ap_tpa_auth`.

### Current state (Mar 2026, first month)
- LP commitments: Bliss Investments LLC $500K (funded Feb), JJNA, LLC $8M (April 2026 close, $8M cash received in advance)
- ACG LLP total assets $528,499.10; investments at cost $8,528,608 (Innovations tranche $508,650 + Undeployed Capital $8,019,958)
- Bank fees expense $180.90 MTD / $207.90 YTD (Zions Bank)
- **Innovations GP distribution: $3,720** → Nairne $2,232.00 / Alec $1,469.40 / Chris $18.60

### Adding a new month
Manual: append to `acg_history.json` (copy Mar 2026 block as template, keep TPA sign conventions: revenue Cr / expense Dr) + append a row to the xlsx. Both pages auto-pick-up new month chips on reload.
