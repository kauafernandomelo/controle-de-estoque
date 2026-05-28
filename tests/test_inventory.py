from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient


def create_product(
    client: TestClient, headers: dict[str, str], payload: dict[str, object]
) -> dict[str, object]:
    """Create a product through the public API."""

    response = client.post("/api/v1/products", headers=headers, json=payload)
    assert response.status_code == 201
    return response.json()


def test_product_crud_and_sku_validation(
    client: TestClient, admin_headers: dict[str, str], product_payload: dict[str, object]
) -> None:
    product = create_product(client, admin_headers, product_payload)
    assert product["sku"] == "NOTE-001"

    duplicate_response = client.post(
        "/api/v1/products", headers=admin_headers, json=product_payload
    )
    assert duplicate_response.status_code == 409

    list_response = client.get("/api/v1/products?nome=Notebook", headers=admin_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    sku_response = client.get("/api/v1/products/sku/NOTE-001", headers=admin_headers)
    assert sku_response.status_code == 200
    assert sku_response.json()["nome"] == "Notebook Dell"

    update_response = client.patch(
        f"/api/v1/products/{product['id']}",
        headers=admin_headers,
        json={"nome": "Notebook Dell Pro", "estoque_minimo": 5},
    )
    assert update_response.status_code == 200
    assert update_response.json()["nome"] == "Notebook Dell Pro"

    delete_response = client.delete(f"/api/v1/products/{product['id']}", headers=admin_headers)
    assert delete_response.status_code == 204


def test_movements_update_stock_and_prevent_negative_stock(
    client: TestClient, admin_headers: dict[str, str], product_payload: dict[str, object]
) -> None:
    product = create_product(client, admin_headers, product_payload)

    entry_response = client.post(
        "/api/v1/movements",
        headers=admin_headers,
        json={
            "produto_id": product["id"],
            "tipo_movimentacao": "ENTRADA",
            "quantidade": 5,
            "observacao": "Compra inicial",
        },
    )
    assert entry_response.status_code == 201

    exit_response = client.post(
        "/api/v1/movements",
        headers=admin_headers,
        json={"produto_id": product["id"], "tipo_movimentacao": "SAIDA", "quantidade": 3},
    )
    assert exit_response.status_code == 201

    current_product = client.get(f"/api/v1/products/{product['id']}", headers=admin_headers).json()
    assert current_product["quantidade_estoque"] == 12

    negative_response = client.post(
        "/api/v1/movements",
        headers=admin_headers,
        json={"produto_id": product["id"], "tipo_movimentacao": "SAIDA", "quantidade": 99},
    )
    assert negative_response.status_code == 400

    delete_response = client.delete(f"/api/v1/products/{product['id']}", headers=admin_headers)
    assert delete_response.status_code == 409


def test_reports_return_inventory_indicators(
    client: TestClient, admin_headers: dict[str, str], product_payload: dict[str, object]
) -> None:
    product_payload["quantidade_estoque"] = 2
    product = create_product(client, admin_headers, product_payload)

    client.post(
        "/api/v1/movements",
        headers=admin_headers,
        json={"produto_id": product["id"], "tipo_movimentacao": "ENTRADA", "quantidade": 4},
    )
    client.post(
        "/api/v1/movements",
        headers=admin_headers,
        json={"produto_id": product["id"], "tipo_movimentacao": "AJUSTE", "quantidade": -3},
    )

    low_stock_response = client.get("/api/v1/reports/low-stock", headers=admin_headers)
    assert low_stock_response.status_code == 200
    assert low_stock_response.json()[0]["sku"] == "NOTE-001"

    most_moved_response = client.get("/api/v1/reports/most-moved", headers=admin_headers)
    assert most_moved_response.status_code == 200
    assert most_moved_response.json()[0]["quantidade_total"] == 7

    start_at = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    end_at = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    entries_response = client.get(
        "/api/v1/reports/entries",
        headers=admin_headers,
        params={"start_at": start_at, "end_at": end_at},
    )
    assert entries_response.status_code == 200
    assert entries_response.json()["quantidade_total"] == 4

    exits_response = client.get(
        "/api/v1/reports/exits",
        headers=admin_headers,
        params={"start_at": start_at, "end_at": end_at},
    )
    assert exits_response.status_code == 200
    assert exits_response.json()["quantidade_total"] == 0

    totals_response = client.get("/api/v1/reports/inventory-totals", headers=admin_headers)
    assert totals_response.status_code == 200
    assert totals_response.json()["quantidade_total_itens"] == 3


def test_invalid_token_is_rejected(client: TestClient) -> None:
    response = client.get("/api/v1/products", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
