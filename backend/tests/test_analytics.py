from tests.factories import employee_payload


def test_analytics_summary_counts_active_and_inactive(client):
    e1 = client.post("/api/employees", json=employee_payload(email="a@acme-corp.com")).json()
    client.post("/api/employees", json=employee_payload(email="b@acme-corp.com"))
    client.delete(f"/api/employees/{e1['id']}")

    resp = client.get("/api/analytics/summary")
    body = resp.json()
    assert body["total_employees"] == 2
    assert body["active_employees"] == 1
    assert body["inactive_employees"] == 1


def test_analytics_department_pay_index_uses_current_salary_not_history(client):
    # India L1 base pay is 700,000 INR (see app/constants.py) -> a 5,000,000 INR
    # salary is a pay index of ~7.14x entry-level pay for that country.
    created = client.post(
        "/api/employees",
        json=employee_payload(department="Engineering", email="eng1@acme-corp.com"),
    ).json()
    emp_id = created["id"]

    # Give this employee a raise — analytics should reflect the NEW salary only,
    # not double-count both the old and new value in the average.
    client.post(
        f"/api/employees/{emp_id}/salary-records",
        json={
            "base_salary": 5_000_000,
            "currency": "INR",
            "bonus_target_pct": 10,
            "effective_date": "2025-01-01",
            "reason": "Promotion",
        },
    )

    resp = client.get("/api/analytics/summary")
    dept = next(d for d in resp.json()["by_department"] if d["group"] == "Engineering")
    assert dept["headcount"] == 1
    assert dept["avg_pay_index"] == round(5_000_000 / 700_000, 3)


def test_by_department_never_naively_averages_across_currencies(client):
    """
    Regression guard: department/level breakdowns span multiple countries, so they
    must report a currency-independent pay index, never a raw "avg_salary" in a
    single (misleading) currency.
    """
    client.post(
        "/api/employees",
        json=employee_payload(
            department="Engineering", country="India", email="in-eng@acme-corp.com"
        ),
    )
    payload = employee_payload(
        department="Engineering",
        country="United States",
        email="us-eng@acme-corp.com",
    )
    payload["starting_salary"] = {
        "base_salary": 150_000,
        "currency": "USD",
        "bonus_target_pct": 10,
        "effective_date": "2022-01-15",
        "reason": "Initial hire",
    }
    client.post("/api/employees", json=payload)

    resp = client.get("/api/analytics/summary")
    dept = next(d for d in resp.json()["by_department"] if d["group"] == "Engineering")
    assert dept["headcount"] == 2
    assert "avg_salary" not in dept  # never a fake blended currency figure
    assert "avg_pay_index" in dept


def test_analytics_excludes_inactive_employees_from_averages(client):
    active = client.post(
        "/api/employees",
        json=employee_payload(department="Marketing", email="active-mkt@acme-corp.com"),
    ).json()
    inactive = client.post(
        "/api/employees",
        json=employee_payload(department="Marketing", email="left-mkt@acme-corp.com"),
    ).json()
    client.delete(f"/api/employees/{inactive['id']}")

    resp = client.get("/api/analytics/summary")
    dept = next(d for d in resp.json()["by_department"] if d["group"] == "Marketing")
    assert dept["headcount"] == 1  # only the active employee counted


def test_analytics_country_median_is_correct_for_odd_group_size(client):
    # Three India-based employees with base salaries 1M / 2M / 3M INR (single
    # currency) -> by_country CAN safely report real medians/totals.
    for i, salary in enumerate([1_000_000, 2_000_000, 3_000_000]):
        payload = employee_payload(
            department="Finance",
            country="India",
            email=f"fin{i}@acme-corp.com",
        )
        payload["starting_salary"]["base_salary"] = salary
        client.post("/api/employees", json=payload)

    resp = client.get("/api/analytics/summary")
    india = next(c for c in resp.json()["by_country"] if c["group"] == "India")
    assert india["median_salary"] == 2_000_000
    assert india["total_cost"] == 6_000_000
    assert india["currency"] == "INR"


def test_reference_data_lists_are_non_empty(client):
    resp = client.get("/api/analytics/reference-data")
    body = resp.json()
    assert len(body["departments"]) > 0
    assert len(body["job_levels"]) > 0
    assert len(body["countries"]) > 0
