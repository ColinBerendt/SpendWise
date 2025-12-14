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

Weekly budget check with automatic SMS alerts.

### Usage

```bash
# Standard (uses NOTIFICATION_PHONE from .env)
uv run scripts/weekly_check.py

# With custom phone number
uv run scripts/weekly_check.py --phone +41791234567

# Dry-Run (no SMS, only display)
uv run scripts/weekly_check.py --dry-run
```

### Cron Setup (Weekly)

```bash
# Open crontab
crontab -e

# Run every Sunday at 18:00
0 18 * * 0 cd /Users/robin/Datenbank/University-HSG/SpendWise/SpendWise && /path/to/.venv/bin/python scripts/weekly_check.py >> /tmp/spendwise_weekly.log 2>&1
```

### What It Does

1. Connects to SQLite (readonly) and SMS MCP Server (Docker)
2. Agent analyzes all active budgets
3. For budgets with 80%+ usage:
   - Generates a fun, helpful tip
   - Sends SMS alert via Twilio
4. Outputs summary

### Beispiel Output

```
============================================================
  WEEKLY BUDGET CHECK - 06.12.2024 18:00
============================================================

Database: /path/to/spendwise.db
Phone: +41791234567

Agent analyzing budgets...
------------------------------------------------------------

Budget Analysis Week 49:

- Food: CHF 89/100 (89%) - WARNING
  -> SMS sent: "Your stomach wants steak... Tip: Meal prep!"

- Transport: CHF 45/100 (45%) - OK

- Entertainment: CHF 110/100 (110%) - OVER BUDGET
  -> SMS sent: "Streaming jungle! Tip: Pause one subscription."

Summary:
- 1 OK
- 1 Warning  
- 1 Over Budget
- 2 SMS sent

============================================================
Weekly Check completed!
============================================================
```

### Environment Variables

Required in `.env`:

```env
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890
NOTIFICATION_PHONE=+41791234567
```

