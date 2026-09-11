from tests.factories import employee_payload


def _seed(client, n, **overrides):
    for i in range(n):
        payload = employee_payload(email=f"person{i}@acme-corp.com", **overrides)
        client.post("/api/employees", json=payload)


def test_pagination_splits_results_correctly(client):
    _seed(client, 5)

    page1 = client.get("/api/employees", params={"page": 1, "page_size": 2}).json()
    page2 = client.get("/api/employees", params={"page": 2, "page_size": 2}).json()

    assert page1["total"] == 5
    assert page1["total_pages"] == 3
    assert len(page1["items"]) == 2
    assert len(page2["items"]) == 2
    assert {i["id"] for i in page1["items"]}.isdisjoint({i["id"] for i in page2["items"]})


def test_filter_by_department(client):
    _seed(client, 3, department="Engineering")
    client.post(
        "/api/employees",
        json=employee_payload(department="Sales", email="sales1@acme-corp.com"),
    )
    client.post(
        "/api/employees",
        json=employee_payload(department="Sales", email="sales2@acme-corp.com"),
    )

    resp = client.get("/api/employees", params={"department": "Sales", "page_size": 50})
    body = resp.json()
    assert body["total"] == 2
    assert all(item["department"] == "Sales" for item in body["items"])


def test_filter_by_status_excludes_deactivated_employees(client):
    active = client.post("/api/employees", json=employee_payload(email="active@acme-corp.com")).json()
    inactive = client.post(
        "/api/employees", json=employee_payload(email="inactive@acme-corp.com")
    ).json()
    client.delete(f"/api/employees/{inactive['id']}")

    resp = client.get("/api/employees", params={"status": "active", "page_size": 50})
    ids = [i["id"] for i in resp.json()["items"]]
    assert active["id"] in ids
    assert inactive["id"] not in ids


def test_search_matches_name_and_email(client):
    client.post(
        "/api/employees",
        json=employee_payload(
            first_name="Grace", last_name="Hopper", email="grace.hopper@acme-corp.com"
        ),
    )
    client.post("/api/employees", json=employee_payload(email="unrelated@acme-corp.com"))

    resp = client.get("/api/employees", params={"search": "grace"})
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["first_name"] == "Grace"
