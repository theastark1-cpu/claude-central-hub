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
