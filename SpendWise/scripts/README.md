# SpendWise Scripts

**Production scripts for running SpendWise services.**

These are executable scripts that run as services or scheduled tasks.

## bank_sync.py

Continuous synchronization script that syncs transactions from MockBank to SpendWise database.

### Usage

```bash
cd SpendWise
uv run scripts/bank_sync.py
```

### What it does

1. Connects to MockBank API every 5 seconds
2. Fetches new transactions
3. Uses Import Agent to categorize and save to database
4. Uses Insights Agent to detect suspicious transactions and send SMS alerts
5. Removes transactions that were deleted from MockBank

### Requirements

- MockBank running on localhost:8080
- SpendWise database initialized
- OpenAI API key in .env
- Twilio keys in .env (optional, for SMS alerts)

---

## weekly_check.py (deprecated - functionality integrated into bank_sync.py)

Woechentlicher Budget-Check mit automatischen SMS-Alerts.

### Usage

```bash
# Standard (nutzt NOTIFICATION_PHONE aus .env)
uv run scripts/weekly_check.py

# Mit custom Telefonnummer
uv run scripts/weekly_check.py --phone +41791234567

# Dry-Run (keine SMS, nur anzeigen)
uv run scripts/weekly_check.py --dry-run
```

### Cron Setup (Woechentlich)

```bash
# Crontab oeffnen
crontab -e

# Jeden Sonntag um 18:00 Uhr ausfuehren
0 18 * * 0 cd /Users/robin/Datenbank/University-HSG/SpendWise/SpendWise && /path/to/.venv/bin/python scripts/weekly_check.py >> /tmp/spendwise_weekly.log 2>&1
```

### Was es macht

1. Verbindet zu SQLite (readonly) und SMS MCP Server (Docker)
2. Agent analysiert alle aktiven Budgets
3. Fuer Budgets mit 80%+ Usage:
   - Generiert lustigen, hilfreichen Tipp
   - Sendet SMS-Alert via Twilio
4. Gibt Zusammenfassung aus

### Beispiel Output

```
============================================================
  WEEKLY BUDGET CHECK - 06.12.2024 18:00
============================================================

Database: /path/to/spendwise.db
Phone: +41791234567

Agent analysiert Budgets...
------------------------------------------------------------

Budget-Analyse Woche 49:

- Food: CHF 89/100 (89%) - WARNING
  -> SMS gesendet: "Dein Magen will Steak... Tipp: Meal-Prep!"

- Transport: CHF 45/100 (45%) - OK

- Entertainment: CHF 110/100 (110%) - OVER BUDGET
  -> SMS gesendet: "Streaming-Jungle! Tipp: Ein Abo pausieren."

Zusammenfassung:
- 1 OK
- 1 Warning  
- 1 Over Budget
- 2 SMS gesendet

============================================================
Weekly Check abgeschlossen!
============================================================
```

### Environment Variables

Erforderlich in `.env`:

```env
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890
NOTIFICATION_PHONE=+41791234567
```

