"""
Domain constants shared by the seed script, models, and analytics.

Kept as plain Python data (not DB tables) deliberately: for a v1 system of record,
these are a fixed, small reference set an HR admin doesn't need to CRUD through the
UI. Promoting them to tables is a natural next step if the org needs custom
departments per business unit.
"""

DEPARTMENTS = [
    "Engineering",
    "Sales",
    "Marketing",
    "Finance",
    "Human Resources",
    "Operations",
    "Product",
    "Customer Support",
]

JOB_LEVELS = [
    "L1 - Associate",
    "L2 - Mid",
    "L3 - Senior",
    "L4 - Lead",
    "L5 - Principal/Manager",
]

# Relative pay multiplier per level, applied on top of a country's base salary band.
LEVEL_MULTIPLIER = {
    "L1 - Associate": 1.0,
    "L2 - Mid": 1.4,
    "L3 - Senior": 1.9,
    "L4 - Lead": 2.5,
    "L5 - Principal/Manager": 3.3,
}

# country -> (currency code, annual base salary for an L1 employee, in local currency)
COUNTRIES = {
    "India": ("INR", 700_000),
    "United States": ("USD", 75_000),
    "United Kingdom": ("GBP", 34_000),
    "Germany": ("EUR", 42_000),
    "Canada": ("CAD", 58_000),
    "Australia": ("AUD", 65_000),
}

EMPLOYMENT_STATUSES = ["active", "inactive"]
