#!/usr/bin/env python3
"""
Seed Sample Data - Populates MockBank databases with test data

Usage:
    cd MockBank/testing
    uv run python seed_data.py
"""

import sqlite3
from pathlib import Path

# Data directory is in parent directory (MockBank/data/)
DATA_DIR = Path(__file__).parent.parent / "data"

# ═══════════════════════════════════════════════════════════════════════════════
# FULL YEAR 2025 TRANSACTIONS (January 1 - December 7)
# Hardcoded list with realistic spending patterns
# ═══════════════════════════════════════════════════════════════════════════════

# Format: (date, description, amount, reference)
TRANSACTIONS_2025 = [
    # ══════════════════════════════════════════════════════════════
    # DECEMBER 2025 (until 7th)
    # ══════════════════════════════════════════════════════════════
    ("2025-12-07", "MIGROS ZURICH", -52.30, "TXN-00001"),
    ("2025-12-07", "SBB", -25.00, "TXN-00002"),
    ("2025-12-06", "COOP BERN", -67.80, "TXN-00003"),
    ("2025-12-06", "STARBUCKS GENEVA", -8.50, "TXN-00004"),
    ("2025-12-05", "AMAZON", -89.90, "TXN-00005"),
    ("2025-12-05", "UBER", -22.40, "TXN-00006"),
    ("2025-12-04", "DENNER BASEL", -34.20, "TXN-00007"),
    ("2025-12-04", "MCDONALD'S LAUSANNE", -15.80, "TXN-00008"),
    ("2025-12-03", "ZVV", -8.80, "TXN-00009"),
    ("2025-12-03", "ZALANDO", -129.00, "TXN-00010"),
    ("2025-12-02", "SHELL WINTERTHUR", -78.50, "TXN-00011"),
    ("2025-12-02", "DIGITEC", -249.00, "TXN-00012"),
    ("2025-12-01", "RENT", -1500.00, "TXN-00013"),
    ("2025-12-01", "NETFLIX", -12.90, "TXN-00014"),
    ("2025-12-01", "SPOTIFY", -9.90, "TXN-00015"),
    ("2025-12-01", "SWISSCOM", -65.00, "TXN-00016"),
    ("2025-12-01", "EWZ ELECTRICITY", -118.00, "TXN-00017"),
    ("2025-12-01", "CSS INSURANCE", -385.00, "TXN-00018"),
    
    # ══════════════════════════════════════════════════════════════
    # NOVEMBER 2025
    # ══════════════════════════════════════════════════════════════
    ("2025-11-30", "MIGROS WINTERTHUR", -88.40, "TXN-00019"),
    ("2025-11-29", "RESTAURANT KRONENHALLE", -145.00, "TXN-00020"),
    ("2025-11-28", "SBB", -45.00, "TXN-00021"),
    ("2025-11-27", "COOP ZURICH", -72.30, "TXN-00022"),
    ("2025-11-26", "H&M ZURICH", -65.00, "TXN-00023"),
    ("2025-11-25", "SALARY", 6000.00, "TXN-00024"),
    ("2025-11-24", "PARKING ZURICH", -18.00, "TXN-00025"),
    ("2025-11-23", "IKEA SPREITENBACH", -234.00, "TXN-00026"),
    ("2025-11-22", "KEBAB ST. GALLEN", -16.50, "TXN-00027"),
    ("2025-11-21", "AMAVITA PHARMACY", -42.80, "TXN-00028"),
    ("2025-11-20", "UBER", -28.60, "TXN-00029"),
    ("2025-11-19", "MIGROS BERN", -56.20, "TXN-00030"),
    ("2025-11-18", "ETH TUITION", -450.00, "TXN-00031"),
    ("2025-11-17", "STEAM", -49.90, "TXN-00032"),
    ("2025-11-16", "COOP BASEL", -44.90, "TXN-00033"),
    ("2025-11-15", "CINEMA ZURICH", -24.00, "TXN-00034"),
    ("2025-11-14", "PIZZA HUT GENEVA", -32.50, "TXN-00035"),
    ("2025-11-13", "ZVV", -8.80, "TXN-00036"),
    ("2025-11-12", "DENNER LAUSANNE", -28.40, "TXN-00037"),
    ("2025-11-11", "MANOR BERN", -89.00, "TXN-00038"),
    ("2025-11-10", "MIGROS FITNESS", -79.00, "TXN-00039"),
    ("2025-11-09", "BP ZURICH", -95.00, "TXN-00040"),
    ("2025-11-08", "STARBUCKS BERN", -12.40, "TXN-00041"),
    ("2025-11-07", "AMAZON", -67.00, "TXN-00042"),
    ("2025-11-06", "SBB", -32.00, "TXN-00043"),
    ("2025-11-05", "COOP WINTERTHUR", -58.70, "TXN-00044"),
    ("2025-11-04", "MEDIAMARKT DIETLIKON", -399.00, "TXN-00045"),
    ("2025-11-03", "BOOKSTORE ORELL FUESSLI", -45.00, "TXN-00046"),
    ("2025-11-02", "UBER", -19.80, "TXN-00047"),
    ("2025-11-01", "RENT", -1500.00, "TXN-00048"),
    ("2025-11-01", "NETFLIX", -12.90, "TXN-00049"),
    ("2025-11-01", "SPOTIFY", -9.90, "TXN-00050"),
    ("2025-11-01", "SWISSCOM", -65.00, "TXN-00051"),
    ("2025-11-01", "EWZ ELECTRICITY", -124.00, "TXN-00052"),
    ("2025-11-01", "CSS INSURANCE", -385.00, "TXN-00053"),
    
    # ══════════════════════════════════════════════════════════════
    # OCTOBER 2025
    # ══════════════════════════════════════════════════════════════
    ("2025-10-31", "MIGROS ZURICH", -62.10, "TXN-00054"),
    ("2025-10-30", "HALLOWEEN COSTUME SHOP", -75.00, "TXN-00055"),
    ("2025-10-29", "COOP BERN", -48.90, "TXN-00056"),
    ("2025-10-28", "SBB", -55.00, "TXN-00057"),
    ("2025-10-27", "DENTIST BERN", -380.00, "TXN-00058"),
    ("2025-10-26", "ZALANDO", -156.00, "TXN-00059"),
    ("2025-10-25", "SALARY", 6000.00, "TXN-00060"),
    ("2025-10-24", "RESTAURANT ASIA", -68.00, "TXN-00061"),
    ("2025-10-23", "UBER", -34.20, "TXN-00062"),
    ("2025-10-22", "MIGROS BASEL", -71.40, "TXN-00063"),
    ("2025-10-21", "UDEMY", -29.90, "TXN-00064"),
    ("2025-10-20", "PARKING BERN", -12.00, "TXN-00065"),
    ("2025-10-19", "COOP GENEVA", -55.60, "TXN-00066"),
    ("2025-10-18", "CONCERT HALLENSTADION", -125.00, "TXN-00067"),
    ("2025-10-17", "DENNER ZURICH", -38.90, "TXN-00068"),
    ("2025-10-16", "ZVV", -8.80, "TXN-00069"),
    ("2025-10-15", "STARBUCKS LAUSANNE", -9.80, "TXN-00070"),
    ("2025-10-14", "AMAZON", -112.00, "TXN-00071"),
    ("2025-10-13", "MCDONALD'S BERN", -18.40, "TXN-00072"),
    ("2025-10-12", "SHELL BASEL", -82.00, "TXN-00073"),
    ("2025-10-11", "DIGITEC", -189.00, "TXN-00074"),
    ("2025-10-10", "MIGROS WINTERTHUR", -49.30, "TXN-00075"),
    ("2025-10-09", "SBB", -28.00, "TXN-00076"),
    ("2025-10-08", "COOP ZURICH", -63.20, "TXN-00077"),
    ("2025-10-07", "PHARMACY BASEL", -24.50, "TXN-00078"),
    ("2025-10-06", "H&M BERN", -78.00, "TXN-00079"),
    ("2025-10-05", "UBER", -26.40, "TXN-00080"),
    ("2025-10-04", "KEBAB ZURICH", -14.50, "TXN-00081"),
    ("2025-10-03", "MIGROS LAUSANNE", -58.80, "TXN-00082"),
    ("2025-10-02", "COURSERA", -49.00, "TXN-00083"),
    ("2025-10-01", "RENT", -1500.00, "TXN-00084"),
    ("2025-10-01", "NETFLIX", -12.90, "TXN-00085"),
    ("2025-10-01", "SPOTIFY", -9.90, "TXN-00086"),
    ("2025-10-01", "SWISSCOM", -65.00, "TXN-00087"),
    ("2025-10-01", "SERAFE", -28.00, "TXN-00088"),
    ("2025-10-01", "EWZ ELECTRICITY", -95.00, "TXN-00089"),
    ("2025-10-01", "CSS INSURANCE", -385.00, "TXN-00090"),
    
    # ══════════════════════════════════════════════════════════════
    # SEPTEMBER 2025
    # ══════════════════════════════════════════════════════════════
    ("2025-09-30", "COOP ZURICH", -78.40, "TXN-00091"),
    ("2025-09-29", "MIGROS BERN", -52.30, "TXN-00092"),
    ("2025-09-28", "SBB", -68.00, "TXN-00093"),
    ("2025-09-27", "RESTAURANT ITALIANO", -92.00, "TXN-00094"),
    ("2025-09-26", "AMAZON", -45.00, "TXN-00095"),
    ("2025-09-25", "SALARY", 6000.00, "TXN-00096"),
    ("2025-09-25", "BONUS", 500.00, "TXN-00097"),
    ("2025-09-24", "UBER", -31.80, "TXN-00098"),
    ("2025-09-23", "ZALANDO", -199.00, "TXN-00099"),
    ("2025-09-22", "MIGROS GENEVA", -67.90, "TXN-00100"),
    ("2025-09-21", "STEAM", -34.90, "TXN-00101"),
    ("2025-09-20", "COOP BASEL", -42.10, "TXN-00102"),
    ("2025-09-19", "ETH BOOKS", -185.00, "TXN-00103"),
    ("2025-09-18", "DENNER WINTERTHUR", -31.40, "TXN-00104"),
    ("2025-09-17", "ZVV", -8.80, "TXN-00105"),
    ("2025-09-16", "STARBUCKS ZURICH", -7.90, "TXN-00106"),
    ("2025-09-15", "DR. MUELLER ZURICH", -150.00, "TXN-00107"),
    ("2025-09-14", "IKEA SPREITENBACH", -312.00, "TXN-00108"),
    ("2025-09-13", "MCDONALD'S GENEVA", -16.20, "TXN-00109"),
    ("2025-09-12", "PARKING ZURICH", -22.00, "TXN-00110"),
    ("2025-09-11", "MIGROS LAUSANNE", -59.70, "TXN-00111"),
    ("2025-09-10", "SBB", -42.00, "TXN-00112"),
    ("2025-09-09", "COOP BERN", -71.30, "TXN-00113"),
    ("2025-09-08", "MANOR ZURICH", -134.00, "TXN-00114"),
    ("2025-09-07", "BP BERN", -88.00, "TXN-00115"),
    ("2025-09-06", "PIZZA HUT BASEL", -28.50, "TXN-00116"),
    ("2025-09-05", "UBER", -18.90, "TXN-00117"),
    ("2025-09-04", "MIGROS ZURICH", -48.20, "TXN-00118"),
    ("2025-09-03", "AMAVITA PHARMACY", -56.00, "TXN-00119"),
    ("2025-09-02", "DIGITEC", -79.00, "TXN-00120"),
    ("2025-09-01", "RENT", -1500.00, "TXN-00121"),
    ("2025-09-01", "NETFLIX", -12.90, "TXN-00122"),
    ("2025-09-01", "SPOTIFY", -9.90, "TXN-00123"),
    ("2025-09-01", "SWISSCOM", -65.00, "TXN-00124"),
    ("2025-09-01", "EWZ ELECTRICITY", -98.00, "TXN-00125"),
    ("2025-09-01", "CSS INSURANCE", -385.00, "TXN-00126"),
    
    # ══════════════════════════════════════════════════════════════
    # AUGUST 2025
    # ══════════════════════════════════════════════════════════════
    ("2025-08-31", "MIGROS ZURICH", -72.40, "TXN-00127"),
    ("2025-08-30", "COOP BERN", -58.90, "TXN-00128"),
    ("2025-08-29", "SBB", -125.00, "TXN-00129"),
    ("2025-08-28", "HOTEL LUZERN", -280.00, "TXN-00130"),
    ("2025-08-27", "RESTAURANT LUZERN", -95.00, "TXN-00131"),
    ("2025-08-26", "UBER", -45.00, "TXN-00132"),
    ("2025-08-25", "SALARY", 6000.00, "TXN-00133"),
    ("2025-08-24", "ZALANDO", -87.00, "TXN-00134"),
    ("2025-08-23", "MIGROS BASEL", -44.30, "TXN-00135"),
    ("2025-08-22", "AMAZON", -156.00, "TXN-00136"),
    ("2025-08-21", "COOP GENEVA", -62.70, "TXN-00137"),
    ("2025-08-20", "CINEMA ZURICH", -28.00, "TXN-00138"),
    ("2025-08-19", "DENNER LAUSANNE", -35.80, "TXN-00139"),
    ("2025-08-18", "ZVV", -8.80, "TXN-00140"),
    ("2025-08-17", "STARBUCKS WINTERTHUR", -11.20, "TXN-00141"),
    ("2025-08-16", "MIGROS FITNESS", -79.00, "TXN-00142"),
    ("2025-08-15", "H&M GENEVA", -92.00, "TXN-00143"),
    ("2025-08-14", "SHELL ZURICH", -76.00, "TXN-00144"),
    ("2025-08-13", "MCDONALD'S BASEL", -14.60, "TXN-00145"),
    ("2025-08-12", "COOP ZURICH", -55.40, "TXN-00146"),
    ("2025-08-11", "PARKING BASEL", -15.00, "TXN-00147"),
    ("2025-08-10", "MIGROS BERN", -68.90, "TXN-00148"),
    ("2025-08-09", "KEBAB GENEVA", -17.50, "TXN-00149"),
    ("2025-08-08", "SBB", -38.00, "TXN-00150"),
    ("2025-08-07", "UBER", -23.40, "TXN-00151"),
    ("2025-08-06", "PHARMACY ZURICH", -32.00, "TXN-00152"),
    ("2025-08-05", "DIGITEC", -449.00, "TXN-00153"),
    ("2025-08-04", "COOP WINTERTHUR", -47.20, "TXN-00154"),
    ("2025-08-03", "MEDIAMARKT ZURICH", -299.00, "TXN-00155"),
    ("2025-08-02", "MIGROS GENEVA", -53.10, "TXN-00156"),
    ("2025-08-01", "RENT", -1500.00, "TXN-00157"),
    ("2025-08-01", "NETFLIX", -12.90, "TXN-00158"),
    ("2025-08-01", "SPOTIFY", -9.90, "TXN-00159"),
    ("2025-08-01", "SWISSCOM", -65.00, "TXN-00160"),
    ("2025-08-01", "EWZ ELECTRICITY", -78.00, "TXN-00161"),
    ("2025-08-01", "CSS INSURANCE", -385.00, "TXN-00162"),
    
    # ══════════════════════════════════════════════════════════════
    # JULY 2025
    # ══════════════════════════════════════════════════════════════
    ("2025-07-31", "COOP ZURICH", -82.30, "TXN-00163"),
    ("2025-07-30", "MIGROS BERN", -64.70, "TXN-00164"),
    ("2025-07-29", "SBB", -95.00, "TXN-00165"),
    ("2025-07-28", "BEACH CLUB BARCELONA", -180.00, "TXN-00166"),
    ("2025-07-27", "HOTEL BARCELONA", -450.00, "TXN-00167"),
    ("2025-07-26", "FLIGHT SWISS", -320.00, "TXN-00168"),
    ("2025-07-25", "SALARY", 6000.00, "TXN-00169"),
    ("2025-07-24", "UBER", -28.90, "TXN-00170"),
    ("2025-07-23", "ZALANDO", -145.00, "TXN-00171"),
    ("2025-07-22", "MIGROS BASEL", -48.60, "TXN-00172"),
    ("2025-07-21", "AMAZON", -78.00, "TXN-00173"),
    ("2025-07-20", "COOP GENEVA", -71.20, "TXN-00174"),
    ("2025-07-19", "DENNER ZURICH", -29.40, "TXN-00175"),
    ("2025-07-18", "STEAM", -24.90, "TXN-00176"),
    ("2025-07-17", "ZVV", -8.80, "TXN-00177"),
    ("2025-07-16", "STARBUCKS BERN", -9.40, "TXN-00178"),
    ("2025-07-15", "MIGROS LAUSANNE", -56.80, "TXN-00179"),
    ("2025-07-14", "DR. MUELLER ZURICH", -120.00, "TXN-00180"),
    ("2025-07-13", "PIZZA HUT WINTERTHUR", -35.00, "TXN-00181"),
    ("2025-07-12", "COOP BASEL", -49.30, "TXN-00182"),
    ("2025-07-11", "BP GENEVA", -92.00, "TXN-00183"),
    ("2025-07-10", "MCDONALD'S ZURICH", -12.80, "TXN-00184"),
    ("2025-07-09", "MIGROS ZURICH", -61.40, "TXN-00185"),
    ("2025-07-08", "SBB", -52.00, "TXN-00186"),
    ("2025-07-07", "PARKING GENEVA", -28.00, "TXN-00187"),
    ("2025-07-06", "UBER", -19.60, "TXN-00188"),
    ("2025-07-05", "COOP BERN", -67.80, "TXN-00189"),
    ("2025-07-04", "H&M BASEL", -55.00, "TXN-00190"),
    ("2025-07-03", "MIGROS WINTERTHUR", -42.90, "TXN-00191"),
    ("2025-07-02", "AMAVITA PHARMACY", -38.50, "TXN-00192"),
    ("2025-07-01", "RENT", -1500.00, "TXN-00193"),
    ("2025-07-01", "NETFLIX", -12.90, "TXN-00194"),
    ("2025-07-01", "SPOTIFY", -9.90, "TXN-00195"),
    ("2025-07-01", "SWISSCOM", -65.00, "TXN-00196"),
    ("2025-07-01", "SERAFE", -28.00, "TXN-00197"),
    ("2025-07-01", "EWZ ELECTRICITY", -85.00, "TXN-00198"),
    ("2025-07-01", "CSS INSURANCE", -385.00, "TXN-00199"),
    
    # ══════════════════════════════════════════════════════════════
    # JUNE 2025
    # ══════════════════════════════════════════════════════════════
    ("2025-06-30", "MIGROS ZURICH", -58.20, "TXN-00200"),
    ("2025-06-29", "COOP BERN", -73.40, "TXN-00201"),
    ("2025-06-28", "SBB", -48.00, "TXN-00202"),
    ("2025-06-27", "RESTAURANT FRENCH", -125.00, "TXN-00203"),
    ("2025-06-26", "UBER", -35.80, "TXN-00204"),
    ("2025-06-25", "SALARY", 6000.00, "TXN-00205"),
    ("2025-06-25", "BONUS", 1000.00, "TXN-00206"),
    ("2025-06-24", "ZALANDO", -178.00, "TXN-00207"),
    ("2025-06-23", "MIGROS BASEL", -51.90, "TXN-00208"),
    ("2025-06-22", "AMAZON", -234.00, "TXN-00209"),
    ("2025-06-21", "COOP GENEVA", -64.30, "TXN-00210"),
    ("2025-06-20", "CONCERT OPENAIR", -185.00, "TXN-00211"),
    ("2025-06-19", "DENNER LAUSANNE", -27.60, "TXN-00212"),
    ("2025-06-18", "ZVV", -8.80, "TXN-00213"),
    ("2025-06-17", "STARBUCKS ZURICH", -8.70, "TXN-00214"),
    ("2025-06-16", "MIGROS WINTERTHUR", -69.40, "TXN-00215"),
    ("2025-06-15", "IKEA SPREITENBACH", -567.00, "TXN-00216"),
    ("2025-06-14", "KEBAB BERN", -15.80, "TXN-00217"),
    ("2025-06-13", "COOP ZURICH", -58.20, "TXN-00218"),
    ("2025-06-12", "SHELL LAUSANNE", -84.00, "TXN-00219"),
    ("2025-06-11", "MCDONALD'S GENEVA", -17.40, "TXN-00220"),
    ("2025-06-10", "MIGROS BERN", -47.60, "TXN-00221"),
    ("2025-06-09", "SBB", -62.00, "TXN-00222"),
    ("2025-06-08", "PARKING ZURICH", -20.00, "TXN-00223"),
    ("2025-06-07", "UBER", -22.30, "TXN-00224"),
    ("2025-06-06", "COOP BASEL", -72.10, "TXN-00225"),
    ("2025-06-05", "DIGITEC", -159.00, "TXN-00226"),
    ("2025-06-04", "MIGROS GENEVA", -54.80, "TXN-00227"),
    ("2025-06-03", "DENTIST ZURICH", -290.00, "TXN-00228"),
    ("2025-06-02", "BOOKSTORE ORELL FUESSLI", -62.00, "TXN-00229"),
    ("2025-06-01", "RENT", -1500.00, "TXN-00230"),
    ("2025-06-01", "NETFLIX", -12.90, "TXN-00231"),
    ("2025-06-01", "SPOTIFY", -9.90, "TXN-00232"),
    ("2025-06-01", "SWISSCOM", -65.00, "TXN-00233"),
    ("2025-06-01", "EWZ ELECTRICITY", -72.00, "TXN-00234"),
    ("2025-06-01", "CSS INSURANCE", -385.00, "TXN-00235"),
    
    # ══════════════════════════════════════════════════════════════
    # MAY 2025
    # ══════════════════════════════════════════════════════════════
    ("2025-05-31", "COOP ZURICH", -66.70, "TXN-00236"),
    ("2025-05-30", "MIGROS BERN", -59.30, "TXN-00237"),
    ("2025-05-29", "SBB", -72.00, "TXN-00238"),
    ("2025-05-28", "AMAZON", -89.00, "TXN-00239"),
    ("2025-05-27", "UBER", -27.40, "TXN-00240"),
    ("2025-05-26", "RESTAURANT THAI", -78.00, "TXN-00241"),
    ("2025-05-25", "SALARY", 6000.00, "TXN-00242"),
    ("2025-05-24", "ZALANDO", -112.00, "TXN-00243"),
    ("2025-05-23", "MIGROS BASEL", -48.20, "TXN-00244"),
    ("2025-05-22", "COOP GENEVA", -71.60, "TXN-00245"),
    ("2025-05-21", "STEAM", -59.90, "TXN-00246"),
    ("2025-05-20", "DENNER ZURICH", -33.40, "TXN-00247"),
    ("2025-05-19", "ZVV", -8.80, "TXN-00248"),
    ("2025-05-18", "STARBUCKS LAUSANNE", -10.20, "TXN-00249"),
    ("2025-05-17", "MIGROS WINTERTHUR", -62.80, "TXN-00250"),
    ("2025-05-16", "CINEMA BERN", -26.00, "TXN-00251"),
    ("2025-05-15", "COOP BERN", -54.90, "TXN-00252"),
    ("2025-05-14", "BP BASEL", -79.00, "TXN-00253"),
    ("2025-05-13", "MCDONALD'S WINTERTHUR", -15.20, "TXN-00254"),
    ("2025-05-12", "MIGROS LAUSANNE", -51.40, "TXN-00255"),
    ("2025-05-11", "SBB", -38.00, "TXN-00256"),
    ("2025-05-10", "PARKING BERN", -14.00, "TXN-00257"),
    ("2025-05-09", "UBER", -21.80, "TXN-00258"),
    ("2025-05-08", "COOP ZURICH", -68.30, "TXN-00259"),
    ("2025-05-07", "H&M WINTERTHUR", -67.00, "TXN-00260"),
    ("2025-05-06", "MIGROS GENEVA", -45.60, "TXN-00261"),
    ("2025-05-05", "PHARMACY BERN", -28.00, "TXN-00262"),
    ("2025-05-04", "MANOR BASEL", -145.00, "TXN-00263"),
    ("2025-05-03", "COOP LAUSANNE", -52.70, "TXN-00264"),
    ("2025-05-02", "UDEMY", -44.90, "TXN-00265"),
    ("2025-05-01", "RENT", -1500.00, "TXN-00266"),
    ("2025-05-01", "NETFLIX", -12.90, "TXN-00267"),
    ("2025-05-01", "SPOTIFY", -9.90, "TXN-00268"),
    ("2025-05-01", "SWISSCOM", -65.00, "TXN-00269"),
    ("2025-05-01", "EWZ ELECTRICITY", -92.00, "TXN-00270"),
    ("2025-05-01", "CSS INSURANCE", -385.00, "TXN-00271"),
    
    # ══════════════════════════════════════════════════════════════
    # APRIL 2025
    # ══════════════════════════════════════════════════════════════
    ("2025-04-30", "MIGROS ZURICH", -71.20, "TXN-00272"),
    ("2025-04-29", "COOP BERN", -63.80, "TXN-00273"),
    ("2025-04-28", "SBB", -55.00, "TXN-00274"),
    ("2025-04-27", "UBER", -32.60, "TXN-00275"),
    ("2025-04-26", "AMAZON", -167.00, "TXN-00276"),
    ("2025-04-25", "SALARY", 6000.00, "TXN-00277"),
    ("2025-04-24", "RESTAURANT SUSHI", -88.00, "TXN-00278"),
    ("2025-04-23", "MIGROS BASEL", -49.70, "TXN-00279"),
    ("2025-04-22", "ZALANDO", -134.00, "TXN-00280"),
    ("2025-04-21", "COOP GENEVA", -76.40, "TXN-00281"),
    ("2025-04-20", "DENNER WINTERTHUR", -31.20, "TXN-00282"),
    ("2025-04-19", "ZVV", -8.80, "TXN-00283"),
    ("2025-04-18", "STARBUCKS BERN", -9.90, "TXN-00284"),
    ("2025-04-17", "MIGROS LAUSANNE", -58.30, "TXN-00285"),
    ("2025-04-16", "MEDIAMARKT SPREITENBACH", -549.00, "TXN-00286"),
    ("2025-04-15", "COOP ZURICH", -67.20, "TXN-00287"),
    ("2025-04-14", "SHELL WINTERTHUR", -88.00, "TXN-00288"),
    ("2025-04-13", "MCDONALD'S BASEL", -13.80, "TXN-00289"),
    ("2025-04-12", "MIGROS BERN", -54.60, "TXN-00290"),
    ("2025-04-11", "SBB", -42.00, "TXN-00291"),
    ("2025-04-10", "PARKING LAUSANNE", -16.00, "TXN-00292"),
    ("2025-04-09", "UBER", -25.40, "TXN-00293"),
    ("2025-04-08", "COOP BASEL", -59.80, "TXN-00294"),
    ("2025-04-07", "DIGITEC", -89.00, "TXN-00295"),
    ("2025-04-06", "MIGROS GENEVA", -47.90, "TXN-00296"),
    ("2025-04-05", "PIZZA HUT ZURICH", -38.50, "TXN-00297"),
    ("2025-04-04", "AMAVITA PHARMACY", -45.00, "TXN-00298"),
    ("2025-04-03", "COOP WINTERTHUR", -61.30, "TXN-00299"),
    ("2025-04-02", "ETH SEMESTER FEE", -380.00, "TXN-00300"),
    ("2025-04-01", "RENT", -1500.00, "TXN-00301"),
    ("2025-04-01", "NETFLIX", -12.90, "TXN-00302"),
    ("2025-04-01", "SPOTIFY", -9.90, "TXN-00303"),
    ("2025-04-01", "SWISSCOM", -65.00, "TXN-00304"),
    ("2025-04-01", "SERAFE", -28.00, "TXN-00305"),
    ("2025-04-01", "EWZ ELECTRICITY", -105.00, "TXN-00306"),
    ("2025-04-01", "CSS INSURANCE", -385.00, "TXN-00307"),
    
    # ══════════════════════════════════════════════════════════════
    # MARCH 2025
    # ══════════════════════════════════════════════════════════════
    ("2025-03-31", "COOP ZURICH", -72.40, "TXN-00308"),
    ("2025-03-30", "MIGROS BERN", -68.90, "TXN-00309"),
    ("2025-03-29", "SBB", -48.00, "TXN-00310"),
    ("2025-03-28", "UBER", -29.80, "TXN-00311"),
    ("2025-03-27", "AMAZON", -92.00, "TXN-00312"),
    ("2025-03-26", "RESTAURANT INDIAN", -72.00, "TXN-00313"),
    ("2025-03-25", "SALARY", 6000.00, "TXN-00314"),
    ("2025-03-25", "BONUS", 300.00, "TXN-00315"),
    ("2025-03-24", "MIGROS BASEL", -55.30, "TXN-00316"),
    ("2025-03-23", "ZALANDO", -189.00, "TXN-00317"),
    ("2025-03-22", "COOP GENEVA", -64.70, "TXN-00318"),
    ("2025-03-21", "DENNER ZURICH", -28.90, "TXN-00319"),
    ("2025-03-20", "ZVV", -8.80, "TXN-00320"),
    ("2025-03-19", "STARBUCKS WINTERTHUR", -8.40, "TXN-00321"),
    ("2025-03-18", "MIGROS LAUSANNE", -61.20, "TXN-00322"),
    ("2025-03-17", "DR. MUELLER ZURICH", -180.00, "TXN-00323"),
    ("2025-03-16", "COOP BERN", -58.40, "TXN-00324"),
    ("2025-03-15", "CONCERT VOLKSHAUS", -95.00, "TXN-00325"),
    ("2025-03-14", "MCDONALD'S GENEVA", -16.80, "TXN-00326"),
    ("2025-03-13", "MIGROS ZURICH", -52.70, "TXN-00327"),
    ("2025-03-12", "BP LAUSANNE", -85.00, "TXN-00328"),
    ("2025-03-11", "SBB", -65.00, "TXN-00329"),
    ("2025-03-10", "PARKING BASEL", -18.00, "TXN-00330"),
    ("2025-03-09", "UBER", -24.20, "TXN-00331"),
    ("2025-03-08", "COOP LAUSANNE", -69.30, "TXN-00332"),
    ("2025-03-07", "H&M ZURICH", -82.00, "TXN-00333"),
    ("2025-03-06", "MIGROS WINTERTHUR", -46.80, "TXN-00334"),
    ("2025-03-05", "KEBAB BASEL", -14.80, "TXN-00335"),
    ("2025-03-04", "DIGITEC", -199.00, "TXN-00336"),
    ("2025-03-03", "COOP ZURICH", -57.60, "TXN-00337"),
    ("2025-03-02", "COURSERA", -52.00, "TXN-00338"),
    ("2025-03-01", "RENT", -1500.00, "TXN-00339"),
    ("2025-03-01", "NETFLIX", -12.90, "TXN-00340"),
    ("2025-03-01", "SPOTIFY", -9.90, "TXN-00341"),
    ("2025-03-01", "SWISSCOM", -65.00, "TXN-00342"),
    ("2025-03-01", "EWZ ELECTRICITY", -135.00, "TXN-00343"),
    ("2025-03-01", "CSS INSURANCE", -385.00, "TXN-00344"),
    
    # ══════════════════════════════════════════════════════════════
    # FEBRUARY 2025
    # ══════════════════════════════════════════════════════════════
    ("2025-02-28", "MIGROS ZURICH", -64.30, "TXN-00345"),
    ("2025-02-27", "COOP BERN", -71.20, "TXN-00346"),
    ("2025-02-26", "SBB", -52.00, "TXN-00347"),
    ("2025-02-25", "SALARY", 6000.00, "TXN-00348"),
    ("2025-02-24", "UBER", -31.40, "TXN-00349"),
    ("2025-02-23", "AMAZON", -78.00, "TXN-00350"),
    ("2025-02-22", "RESTAURANT FONDUE", -145.00, "TXN-00351"),
    ("2025-02-21", "MIGROS BASEL", -48.60, "TXN-00352"),
    ("2025-02-20", "ZALANDO", -98.00, "TXN-00353"),
    ("2025-02-19", "COOP GENEVA", -62.30, "TXN-00354"),
    ("2025-02-18", "DENNER LAUSANNE", -34.70, "TXN-00355"),
    ("2025-02-17", "ZVV", -8.80, "TXN-00356"),
    ("2025-02-16", "STARBUCKS ZURICH", -7.80, "TXN-00357"),
    ("2025-02-15", "MIGROS WINTERTHUR", -56.40, "TXN-00358"),
    ("2025-02-14", "VALENTINES DINNER", -220.00, "TXN-00359"),
    ("2025-02-14", "FLOWERS SHOP ZURICH", -85.00, "TXN-00360"),
    ("2025-02-13", "COOP ZURICH", -53.80, "TXN-00361"),
    ("2025-02-12", "CINEMA BASEL", -24.00, "TXN-00362"),
    ("2025-02-11", "MCDONALD'S BERN", -15.60, "TXN-00363"),
    ("2025-02-10", "MIGROS BERN", -49.20, "TXN-00364"),
    ("2025-02-09", "SHELL GENEVA", -78.00, "TXN-00365"),
    ("2025-02-08", "SBB", -45.00, "TXN-00366"),
    ("2025-02-07", "PARKING WINTERTHUR", -12.00, "TXN-00367"),
    ("2025-02-06", "UBER", -22.80, "TXN-00368"),
    ("2025-02-05", "COOP BASEL", -66.40, "TXN-00369"),
    ("2025-02-04", "MANOR GENEVA", -112.00, "TXN-00370"),
    ("2025-02-03", "MIGROS LAUSANNE", -51.70, "TXN-00371"),
    ("2025-02-02", "PHARMACY WINTERTHUR", -35.00, "TXN-00372"),
    ("2025-02-01", "RENT", -1500.00, "TXN-00373"),
    ("2025-02-01", "NETFLIX", -12.90, "TXN-00374"),
    ("2025-02-01", "SPOTIFY", -9.90, "TXN-00375"),
    ("2025-02-01", "SWISSCOM", -65.00, "TXN-00376"),
    ("2025-02-01", "EWZ ELECTRICITY", -148.00, "TXN-00377"),
    ("2025-02-01", "CSS INSURANCE", -385.00, "TXN-00378"),
    
    # ══════════════════════════════════════════════════════════════
    # JANUARY 2025
    # ══════════════════════════════════════════════════════════════
    ("2025-01-31", "COOP ZURICH", -78.90, "TXN-00379"),
    ("2025-01-30", "MIGROS BERN", -62.40, "TXN-00380"),
    ("2025-01-29", "SBB", -58.00, "TXN-00381"),
    ("2025-01-28", "UBER", -28.60, "TXN-00382"),
    ("2025-01-27", "AMAZON", -145.00, "TXN-00383"),
    ("2025-01-26", "RESTAURANT CHINESE", -68.00, "TXN-00384"),
    ("2025-01-25", "SALARY", 6000.00, "TXN-00385"),
    ("2025-01-24", "MIGROS BASEL", -54.30, "TXN-00386"),
    ("2025-01-23", "ZALANDO WINTER SALE", -234.00, "TXN-00387"),
    ("2025-01-22", "COOP GENEVA", -69.80, "TXN-00388"),
    ("2025-01-21", "DENNER WINTERTHUR", -32.40, "TXN-00389"),
    ("2025-01-20", "ZVV", -8.80, "TXN-00390"),
    ("2025-01-19", "STARBUCKS BERN", -9.20, "TXN-00391"),
    ("2025-01-18", "MIGROS LAUSANNE", -58.60, "TXN-00392"),
    ("2025-01-17", "STEAM WINTER SALE", -89.90, "TXN-00393"),
    ("2025-01-16", "COOP BERN", -64.20, "TXN-00394"),
    ("2025-01-15", "BP ZURICH", -92.00, "TXN-00395"),
    ("2025-01-14", "MCDONALD'S LAUSANNE", -14.40, "TXN-00396"),
    ("2025-01-13", "MIGROS ZURICH", -67.80, "TXN-00397"),
    ("2025-01-12", "SBB", -42.00, "TXN-00398"),
    ("2025-01-11", "PARKING GENEVA", -24.00, "TXN-00399"),
    ("2025-01-10", "UBER", -26.20, "TXN-00400"),
    ("2025-01-09", "COOP WINTERTHUR", -71.30, "TXN-00401"),
    ("2025-01-08", "DIGITEC", -329.00, "TXN-00402"),
    ("2025-01-07", "MIGROS GENEVA", -49.40, "TXN-00403"),
    ("2025-01-06", "KEBAB LAUSANNE", -16.20, "TXN-00404"),
    ("2025-01-05", "AMAVITA PHARMACY", -52.00, "TXN-00405"),
    ("2025-01-04", "COOP BASEL", -58.70, "TXN-00406"),
    ("2025-01-03", "IKEA SPREITENBACH", -423.00, "TXN-00407"),
    ("2025-01-02", "MIGROS BERN", -45.30, "TXN-00408"),
    ("2025-01-01", "RENT", -1500.00, "TXN-00409"),
    ("2025-01-01", "NETFLIX", -12.90, "TXN-00410"),
    ("2025-01-01", "SPOTIFY", -9.90, "TXN-00411"),
    ("2025-01-01", "SWISSCOM", -65.00, "TXN-00412"),
    ("2025-01-01", "SERAFE", -28.00, "TXN-00413"),
    ("2025-01-01", "EWZ ELECTRICITY", -142.00, "TXN-00414"),
    ("2025-01-01", "CSS INSURANCE", -385.00, "TXN-00415"),
    ("2025-01-01", "CARRYOVER FROM THE PREVIOUS YEAR", 20000.00, "TXN-00416"),
    
    # ══════════════════════════════════════════════════════════════
    # ANOMALIES (Suspicious transactions - each only once!)
    # ══════════════════════════════════════════════════════════════
    ("2025-11-15", "BP ZURICH", -1500.00, "TXN-00417"),              # Way too much for gas
    ("2025-09-08", "SHELL BERN", -2200.00, "TXN-00418"),             # Impossible gas amount
    ("2025-07-22", "WEAPONS STORE SOMALIA", -3500.00, "TXN-00419"),  # Suspicious transaction for testing
    ("2025-05-18", "ANONYMOUS TRANSFER", -5000.00, "TXN-00420"),    # Anonymous outgoing
    ("2025-03-12", "ANONYMOUS", 8000.00, "TXN-00421"),              # Anonymous incoming
    ("2025-10-25", "CASINO ONLINE", -1200.00, "TXN-00422"),         # Gambling
    ("2025-08-14", "CRYPTO EXCHANGE", -2500.00, "TXN-00423"),       # Crypto purchase
    ("2025-06-28", "CASH WITHDRAWAL ATM", -9000.00, "TXN-00424"),   # Large cash withdrawal
    ("2025-04-19", "UNKNOWN MERCHANT XYZ", -750.00, "TXN-00425"),   # Unknown merchant
    ("2025-02-22", "TRANSFER CAYMAN ISLANDS", -12000.00, "TXN-00426"),  # Offshore
    ("2025-12-05", "NIGHT CLUB IBIZA", -890.00, "TXN-00427"),       # Party expenses
    ("2025-01-28", "LUXURY WATCHES GENEVA", -4500.00, "TXN-00428"), # Expensive luxury
]


def seed_transactions():
    """Seed transactions for the entire year (hardcoded)."""
    print("\nSeeding transactions...")
    
    db_path = DATA_DIR / "transactions.db"
    conn = sqlite3.connect(db_path)
    
    # Clear existing data
    conn.execute("DELETE FROM transactions")
    
    for tx_date, description, amount, ref in TRANSACTIONS_2025:
        conn.execute(
            "INSERT INTO transactions (reference, date, description, amount, currency) VALUES (?, ?, ?, ?, ?)",
            (ref, tx_date, description, amount, "CHF")
        )
    
    conn.commit()
    conn.close()
    
    print(f"   Added {len(TRANSACTIONS_2025)} transactions (Jan-Dec 2025)")


def seed_stocks():
    """Seed 10 sample stocks with invested amounts."""
    print("\nSeeding stocks...")
    
    # (ticker, quantity, invested CHF)
    stocks = [
        ("AAPL", 10, 2000.00),   # ~$185 per share
        ("MSFT", 5, 1700.00),    # ~$380 per share
        ("GOOGL", 3, 510.00),    # ~$170 per share
        ("TSLA", 2, 900.00),     # ~$350 per share
        ("AMZN", 4, 820.00),     # ~$180 per share
    ]
    
    db_path = DATA_DIR / "stocks.db"
    conn = sqlite3.connect(db_path)
    
    # Clear existing data
    conn.execute("DELETE FROM stocks")
    
    for ticker, quantity, invested in stocks:
        conn.execute(
            "INSERT INTO stocks (ticker, quantity, invested) VALUES (?, ?, ?)",
            (ticker, quantity, invested)
        )
    
    conn.commit()
    conn.close()
    
    print(f"   Added {len(stocks)} stocks")


def seed_recurring():
    """Seed 2 sample recurring transactions."""
    print("\nSeeding recurring transactions...")
    
    recurring = [
        ("Rent", -1500.00, "CHF", "monthly", None, 1, None, None),
        ("Netflix", -12.90, "CHF", "monthly", None, 15, None, None),
    ]
    
    db_path = DATA_DIR / "recurring.db"
    conn = sqlite3.connect(db_path)
    
    # Clear existing data
    conn.execute("DELETE FROM recurring_transactions")
    
    for desc, amount, currency, freq, dow, dom, month, doy in recurring:
        conn.execute(
            """INSERT INTO recurring_transactions 
               (description, amount, currency, frequency, day_of_week, day_of_month, month, day_of_year)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (desc, amount, currency, freq, dow, dom, month, doy)
        )
    
    conn.commit()
    conn.close()
    
    print(f"   Added {len(recurring)} recurring transactions")


def main():
    print("\n" + "=" * 50)
    print("MockBank - Seed Sample Data")
    print("=" * 50)
    
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize databases first (create tables)
    import database
    database.init_databases()
    
    # Seed data
    seed_transactions()
    seed_stocks()
    seed_recurring()
    
    print("\n" + "=" * 50)
    print("Done! Sample data seeded successfully.")
    print("=" * 50)
    print("\nStart MockBank to see the data:")
    print("  uv run uvicorn server:app --reload --port 8080")
    print()


if __name__ == "__main__":
    main()