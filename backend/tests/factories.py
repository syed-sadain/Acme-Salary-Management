import datetime as dt


def employee_payload(**overrides) -> dict:
    payload = {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada.lovelace@acme-corp.com",
        "department": "Engineering",
        "job_title": "Senior Software Engineer",
        "job_level": "L3 - Senior",
        "country": "India",
        "hire_date": "2022-01-15",
        "status": "active",
        "starting_salary": {
            "base_salary": 1_800_000,
            "currency": "INR",
            "bonus_target_pct": 10,
            "effective_date": "2022-01-15",
            "reason": "Initial hire",
        },
    }
    payload.update(overrides)
    return payload
