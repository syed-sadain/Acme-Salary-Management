from tests.factories import employee_payload


def test_adding_a_salary_record_does_not_overwrite_history(client):
    created = client.post("/api/employees", json=employee_payload()).json()
    emp_id = created["id"]

    raise_payload = {
        "base_salary": 2_200_000,
        "currency": "INR",
        "bonus_target_pct": 12,
        "effective_date": "2023-06-01",
        "reason": "Annual merit increase",
    }
    resp = client.post(f"/api/employees/{emp_id}/salary-records", json=raise_payload)
    assert resp.status_code == 201

    detail = client.get(f"/api/employees/{emp_id}").json()
    # Both the original hire salary and the new raise must both still exist.
    assert len(detail["salary_records"]) == 2
    salaries = {r["base_salary"] for r in detail["salary_records"]}
    assert salaries == {1_800_000, 2_200_000}


def test_salary_history_is_returned_most_recent_first(client):
    created = client.post("/api/employees", json=employee_payload()).json()
    emp_id = created["id"]

    client.post(
        f"/api/employees/{emp_id}/salary-records",
        json={
            "base_salary": 2_000_000,
            "currency": "INR",
            "bonus_target_pct": 10,
            "effective_date": "2023-01-01",
            "reason": "Promotion",
        },
    )
    client.post(
        f"/api/employees/{emp_id}/salary-records",
        json={
            "base_salary": 2_400_000,
            "currency": "INR",
            "bonus_target_pct": 15,
            "effective_date": "2024-01-01",
            "reason": "Promotion",
        },
    )

    detail = client.get(f"/api/employees/{emp_id}").json()
    dates = [r["effective_date"] for r in detail["salary_records"]]
    assert dates == sorted(dates, reverse=True)


def test_current_salary_in_list_view_reflects_latest_raise(client):
    created = client.post("/api/employees", json=employee_payload()).json()
    emp_id = created["id"]

    client.post(
        f"/api/employees/{emp_id}/salary-records",
        json={
            "base_salary": 3_000_000,
            "currency": "INR",
            "bonus_target_pct": 10,
            "effective_date": "2024-01-01",
            "reason": "Promotion",
        },
    )

    listing = client.get("/api/employees").json()
    row = next(i for i in listing["items"] if i["id"] == emp_id)
    assert row["current_salary"] == 3_000_000  # not the original 1.8M hire salary


def test_adding_salary_record_to_missing_employee_returns_404(client):
    resp = client.post(
        "/api/employees/9999/salary-records",
        json={
            "base_salary": 1000,
            "currency": "USD",
            "bonus_target_pct": 0,
            "effective_date": "2024-01-01",
        },
    )
    assert resp.status_code == 404
