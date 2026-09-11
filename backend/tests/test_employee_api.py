from tests.factories import employee_payload


def test_create_employee_returns_full_detail_with_initial_salary(client):
    resp = client.post("/api/employees", json=employee_payload())
    assert resp.status_code == 201

    body = resp.json()
    assert body["employee_code"] == "EMP-000001"
    assert body["first_name"] == "Ada"
    assert len(body["salary_records"]) == 1
    assert body["salary_records"][0]["base_salary"] == 1_800_000


def test_create_employee_assigns_sequential_codes(client):
    client.post("/api/employees", json=employee_payload(email="a@acme-corp.com"))
    resp = client.post("/api/employees", json=employee_payload(email="b@acme-corp.com"))
    assert resp.json()["employee_code"] == "EMP-000002"


def test_get_employee_not_found_returns_404(client):
    resp = client.get("/api/employees/9999")
    assert resp.status_code == 404


def test_create_employee_rejects_invalid_salary(client):
    payload = employee_payload()
    payload["starting_salary"]["base_salary"] = -100
    resp = client.post("/api/employees", json=payload)
    assert resp.status_code == 422  # Pydantic validation: base_salary must be > 0


def test_create_employee_rejects_invalid_email(client):
    payload = employee_payload(email="not-an-email")
    resp = client.post("/api/employees", json=payload)
    assert resp.status_code == 422


def test_update_employee_patches_only_provided_fields(client):
    created = client.post("/api/employees", json=employee_payload()).json()
    emp_id = created["id"]

    resp = client.patch(f"/api/employees/{emp_id}", json={"department": "Product"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["department"] == "Product"
    assert body["first_name"] == "Ada"  # untouched fields survive the partial update


def test_deactivate_employee_soft_deletes_and_keeps_salary_history(client):
    created = client.post("/api/employees", json=employee_payload()).json()
    emp_id = created["id"]

    resp = client.delete(f"/api/employees/{emp_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "inactive"
    assert len(body["salary_records"]) == 1  # history is preserved, not wiped

    # The employee is still fetchable directly by id (soft delete, not a hard delete).
    assert client.get(f"/api/employees/{emp_id}").status_code == 200
