"""
MockBank Configuration - Categories, Merchants, and Recurring Types
"""

# Categories with their merchants (for dropdowns)
CATEGORIES = {
    "Food & Dining": [
        "Migros", "Coop", "Denner", "Aldi", "Lidl", 
        "Starbucks", "McDonald's", "Restaurant", "Café", 
        "Kebab", "Pizza", "Sushi"
    ],
    "Transportation": [
        "SBB", "ZVV", "Uber", "Taxi", "Parking", 
        "Shell", "BP", "Esso"
    ],
    "Shopping": [
        "Zalando", "Amazon", "H&M", "Zara", "IKEA", 
        "MediaMarkt", "Digitec", "Galaxus", "Manor"
    ],
    "Entertainment": [
        "Netflix", "Spotify", "Disney+", "Apple Music", 
        "Steam", "PlayStation", "Cinema", "Concert"
    ],
    "Bills & Utilities": [
        "Rent", "Swisscom", "Sunrise", "Salt", 
        "EWZ", "Serafe", "CSS", "Swica"
    ],
    "Health": [
        "Pharmacy", "Doctor", "Dentist", "Gym", 
        "Migros Fitness", "Amavita"
    ],
    "Education": [
        "ETH", "UZH", "HSG", "Udemy", "Coursera", "Bookstore"
    ],
    "Income": [
        "Bonus", "Transfer", "Salary"
    ],
}

# Amount ranges for random transaction generation
AMOUNT_RANGES = {
    "Food & Dining": (-10, -150),
    "Transportation": (-5, -80),
    "Shopping": (-20, -300),
    "Entertainment": (-10, -50),
    "Bills & Utilities": (-50, -200),
    "Health": (-20, -150),
    "Education": (-20, -500),
    "Income": (2000, 4000),  # Positive!
}

# Recurring transaction types (for dropdown)
RECURRING_TYPES = [
    {"name": "Rent", "default_amount": -1500.00, "default_freq": "monthly", "default_day": 1},
    {"name": "Netflix", "default_amount": -12.90, "default_freq": "monthly", "default_day": 15},
    {"name": "Spotify", "default_amount": -9.90, "default_freq": "monthly", "default_day": 15},
    {"name": "Swisscom", "default_amount": -65.00, "default_freq": "monthly", "default_day": 1},
    {"name": "Salary", "default_amount": 4500.00, "default_freq": "monthly", "default_day": 25},
    {"name": "Gym", "default_amount": -79.00, "default_freq": "monthly", "default_day": 1},
    {"name": "Insurance", "default_amount": -350.00, "default_freq": "monthly", "default_day": 1},
    {"name": "SBB GA", "default_amount": -340.00, "default_freq": "monthly", "default_day": 1},
    {"name": "Custom", "default_amount": 0.00, "default_freq": "monthly", "default_day": 1},
]

# Days of week for recurring (weekly)
DAYS_OF_WEEK = [
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
]

# Months for recurring (yearly)
MONTHS = [
    (1, "January"),
    (2, "February"),
    (3, "March"),
    (4, "April"),
    (5, "May"),
    (6, "June"),
    (7, "July"),
    (8, "August"),
    (9, "September"),
    (10, "October"),
    (11, "November"),
    (12, "December"),
]

# Swiss cities for random descriptions
CITIES = ["ZURICH", "BERN", "BASEL", "GENEVA", "LAUSANNE", "WINTERTHUR", "ST. GALLEN"]

# Merchants that don't need a location
NO_LOCATION_MERCHANTS = [
    "Zalando", "Amazon", "Galaxus", "Digitec",  # Online shops
    "Netflix", "Spotify", "Disney+", "Apple Music", "Steam", "PlayStation",  # Streaming/Gaming
    "Swisscom", "Sunrise", "Salt", "Serafe",  # Telco/TV
    "CSS", "Swica",  # Insurance
    "Udemy", "Coursera", "ETH", "UZH", "HSG", "Bookstore",  # Education
    "Uber",  # App-based
    "SBB", "ZVV",  # Public transport (tickets via app)
]

