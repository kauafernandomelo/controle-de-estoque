from decimal import Decimal

from fastapi.testclient import TestClient


# ─── Brands ───────────────────────────────────────────────────────────────────


def test_brand_crud(client: TestClient, admin_headers: dict[str, str]) -> None:
    create = client.post(
        "/api/v1/brands",
        headers=admin_headers,
        json={"nome": "Dell", "slug": "dell", "descricao": "Computadores"},
    )
    assert create.status_code == 201
    brand = create.json()
    assert brand["nome"] == "Dell"
    brand_id = brand["id"]

    get = client.get(f"/api/v1/brands/{brand_id}", headers=admin_headers)
    assert get.status_code == 200
    assert get.json()["slug"] == "dell"

    patch = client.patch(
        f"/api/v1/brands/{brand_id}",
        headers=admin_headers,
        json={"descricao": "Atualizada"},
    )
    assert patch.status_code == 200
    assert patch.json()["descricao"] == "Atualizada"

    delete = client.delete(f"/api/v1/brands/{brand_id}", headers=admin_headers)
    assert delete.status_code == 204

    get2 = client.get(f"/api/v1/brands/{brand_id}", headers=admin_headers)
    assert get2.status_code == 404


def test_brand_list_active_only(client: TestClient, admin_headers: dict[str, str]) -> None:
    client.post("/api/v1/brands", headers=admin_headers, json={"nome": "Ativa", "slug": "ativa"})
    b2 = client.post(
        "/api/v1/brands", headers=admin_headers, json={"nome": "Inativa", "slug": "inativa", "ativo": False}
    ).json()

    all_brands = client.get("/api/v1/brands", headers=admin_headers).json()
    assert len(all_brands) == 2

    active_only = client.get("/api/v1/brands?active_only=true", headers=admin_headers).json()
    assert len(active_only) == 1
    assert active_only[0]["nome"] == "Ativa"

    client.delete(f"/api/v1/brands/{b2['id']}", headers=admin_headers)


# ─── Suppliers ────────────────────────────────────────────────────────────────


def test_supplier_crud(client: TestClient, admin_headers: dict[str, str]) -> None:
    create = client.post(
        "/api/v1/suppliers",
        headers=admin_headers,
        json={
            "nome": "Distribuidora ABC",
            "cnpj": "11.222.333/0001-44",
            "nome_contato": "Joao",
            "email": "joao@abc.com",
            "telefone": "11999999999",
        },
    )
    assert create.status_code == 201
    s = create.json()
    assert s["nome"] == "Distribuidora ABC"
    sid = s["id"]

    get = client.get(f"/api/v1/suppliers/{sid}", headers=admin_headers)
    assert get.status_code == 200
    assert get.json()["email"] == "joao@abc.com"

    patch = client.patch(
        f"/api/v1/suppliers/{sid}",
        headers=admin_headers,
        json={"telefone": "11888888888"},
    )
    assert patch.status_code == 200
    assert patch.json()["telefone"] == "11888888888"

    client.delete(f"/api/v1/suppliers/{sid}", headers=admin_headers)
    assert client.get(f"/api/v1/suppliers/{sid}", headers=admin_headers).status_code == 404


def test_supplier_list_filter(client: TestClient, admin_headers: dict[str, str]) -> None:
    client.post("/api/v1/suppliers", headers=admin_headers, json={"nome": "Fornecedor X"})
    s2 = client.post(
        "/api/v1/suppliers", headers=admin_headers, json={"nome": "Inativo", "ativo": False}
    ).json()

    all_s = client.get("/api/v1/suppliers", headers=admin_headers).json()
    assert len(all_s) >= 2

    active = client.get("/api/v1/suppliers?active_only=true", headers=admin_headers).json()
    assert all(a["ativo"] for a in active)

    client.delete(f"/api/v1/suppliers/{s2['id']}", headers=admin_headers)


# ─── Categories ───────────────────────────────────────────────────────────────


def test_category_crud_and_subcategories(client: TestClient, admin_headers: dict[str, str]) -> None:
    parent = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={"nome": "Eletronicos", "slug": "eletronicos", "ordem": 1},
    ).json()
    pid = parent["id"]

    child = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={"nome": "Notebooks", "slug": "notebooks", "categoria_pai_id": pid, "ordem": 1},
    ).json()
    assert child["categoria_pai_id"] == pid

    list_all = client.get("/api/v1/categories", headers=admin_headers).json()
    assert len(list_all) == 2

    filtered = client.get(f"/api/v1/categories?parent_id={pid}", headers=admin_headers).json()
    assert len(filtered) == 1
    assert filtered[0]["slug"] == "notebooks"

    patch = client.patch(
        f"/api/v1/categories/{child['id']}",
        headers=admin_headers,
        json={"nome": "Laptops"},
    )
    assert patch.status_code == 200
    assert patch.json()["nome"] == "Laptops"

    client.delete(f"/api/v1/categories/{child['id']}", headers=admin_headers)
    assert client.get(f"/api/v1/categories/{child['id']}", headers=admin_headers).status_code == 404
    client.delete(f"/api/v1/categories/{pid}", headers=admin_headers)


# ─── Tags ─────────────────────────────────────────────────────────────────────


def test_tag_lifecycle(client: TestClient, admin_headers: dict[str, str]) -> None:
    create = client.post(
        "/api/v1/tags",
        headers=admin_headers,
        json={"nome": "Promocao", "slug": "promocao"},
    )
    assert create.status_code == 201
    tag = create.json()
    assert tag["nome"] == "Promocao"
    tid = tag["id"]

    list_tags = client.get("/api/v1/tags", headers=admin_headers).json()
    assert any(t["id"] == tid for t in list_tags)

    client.delete(f"/api/v1/tags/{tid}", headers=admin_headers)
    after = client.get("/api/v1/tags", headers=admin_headers).json()
    assert not any(t["id"] == tid for t in after)


# ─── Reviews ──────────────────────────────────────────────────────────────────


def test_review_crud(client: TestClient, admin_headers: dict[str, str], product_payload: dict[str, object]) -> None:
    product = client.post("/api/v1/products", headers=admin_headers, json=product_payload).json()
    pid = product["id"]

    review = client.post(
        f"/api/v1/products/{pid}/reviews",
        headers=admin_headers,
        json={"avaliacao": 5, "titulo": "Excelente!", "comentario": "Muito bom"},
    )
    assert review.status_code == 201
    r = review.json()
    assert r["avaliacao"] == 5
    rid = r["id"]

    product_after = client.get(f"/api/v1/products/{pid}", headers=admin_headers).json()
    assert Decimal(product_after["rating_avg"]) == Decimal("5.0")
    assert product_after["rating_count"] == 1

    list_reviews = client.get(f"/api/v1/products/{pid}/reviews", headers=admin_headers).json()
    assert len(list_reviews) == 1

    client.delete(f"/api/v1/products/{pid}/reviews/{rid}", headers=admin_headers)
    product_final = client.get(f"/api/v1/products/{pid}", headers=admin_headers).json()
    assert Decimal(product_final["rating_avg"]) == Decimal("0.0")
    assert product_final["rating_count"] == 0

    client.delete(f"/api/v1/products/{pid}", headers=admin_headers)


def test_review_forbidden(client: TestClient, admin_headers: dict[str, str], product_payload: dict[str, object]) -> None:
    product = client.post("/api/v1/products", headers=admin_headers, json=product_payload).json()
    pid = product["id"]

    review = client.post(
        f"/api/v1/products/{pid}/reviews",
        headers=admin_headers,
        json={"avaliacao": 3},
    ).json()
    rid = review["id"]

    other_reg = client.post(
        "/api/v1/auth/register",
        json={"nome": "Other User", "email": "other@test.com", "senha": "strongpass456"},
    )
    assert other_reg.status_code == 201
    other_login = client.post(
        "/api/v1/auth/login", data={"username": "other@test.com", "password": "strongpass456"}
    )
    assert other_login.status_code == 200
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    delete_other = client.delete(
        f"/api/v1/products/{pid}/reviews/{rid}", headers=other_headers
    )
    assert delete_other.status_code == 403

    client.delete(f"/api/v1/products/{pid}/reviews/{rid}", headers=admin_headers)
    client.delete(f"/api/v1/products/{pid}", headers=admin_headers)


# ─── Cart ─────────────────────────────────────────────────────────────────────


def test_cart_full_lifecycle(client: TestClient, admin_headers: dict[str, str], product_payload: dict[str, object]) -> None:
    product = client.post("/api/v1/products", headers=admin_headers, json=product_payload).json()
    pid = product["id"]

    cart = client.get("/api/v1/cart", headers=admin_headers).json()
    assert cart["total_items"] == 0
    assert len(cart["items"]) == 0

    add = client.post(
        "/api/v1/cart/items",
        headers=admin_headers,
        json={"produto_id": pid, "quantidade": 2},
    )
    assert add.status_code == 201
    assert add.json()["total_items"] == 2
    assert len(add.json()["items"]) == 1
    item_id = add.json()["items"][0]["id"]

    update = client.patch(
        f"/api/v1/cart/items/{item_id}",
        headers=admin_headers,
        json={"quantidade": 5},
    )
    assert update.status_code == 200
    assert update.json()["total_items"] == 5

    remove = client.delete(f"/api/v1/cart/items/{item_id}", headers=admin_headers)
    assert remove.status_code == 200
    assert remove.json()["total_items"] == 0
    assert len(remove.json()["items"]) == 0

    add2 = client.post(
        "/api/v1/cart/items",
        headers=admin_headers,
        json={"produto_id": pid, "quantidade": 1},
    ).json()
    assert add2["total_items"] == 1
    assert len(add2["items"]) == 1

    cleared = client.delete("/api/v1/cart", headers=admin_headers)
    assert cleared.status_code == 200
    assert cleared.json()["total_items"] == 0
    assert len(cleared.json()["items"]) == 0

    client.delete(f"/api/v1/products/{pid}", headers=admin_headers)


def test_cart_persists_across_requests(client: TestClient, admin_headers: dict[str, str], product_payload: dict[str, object]) -> None:
    product = client.post("/api/v1/products", headers=admin_headers, json=product_payload).json()
    pid = product["id"]

    client.post("/api/v1/cart/items", headers=admin_headers, json={"produto_id": pid, "quantidade": 3})

    cart2 = client.get("/api/v1/cart", headers=admin_headers).json()
    assert cart2["total_items"] == 3
    assert len(cart2["items"]) == 1

    client.delete(f"/api/v1/products/{pid}", headers=admin_headers)
