# MockBank Testing & Demo Scripts

This directory contains testing and demo scripts for development purposes.

## Scripts

### `seed_data.py`
Populates MockBank databases with test data including:
- Sample transactions (various categories, merchants, amounts)
- Stock portfolio holdings
- Recurring transaction definitions

**Usage:**
```bash
cd MockBank/testing
uv run python seed_data.py
```

### `test_api.py`
Tests all MockBank API endpoints to verify they work correctly.

**Usage:**
```bash
cd MockBank/testing
uv run python test_api.py
```

**Prerequisites:**
Make sure the MockBank server is running:
```bash
cd MockBank
uv run uvicorn server:app --reload --port 8080
```

## Purpose

These scripts are intended for:
- **Development**: Setting up test data during development
- **Testing**: Verifying API functionality
- **Demo**: Populating sample data for demonstrations

