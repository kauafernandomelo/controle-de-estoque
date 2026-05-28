"""
Seed script — populates the database with real products, brands, categories, and images.

Usage:
  python scripts/seed_products.py [--base-url http://127.0.0.1:8000]
"""

import argparse
import io
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from uuid import UUID

import requests

# ─── re-exported from src — avoid app-level imports ─────────────────────

API_PREFIX = "/api/v1"

# ─── Data ────────────────────────────────────────────────────────────────

BRANDS = [
    {"nome": "Apple", "slug": "apple", "descricao": "Tecnologia premium"},
    {"nome": "Samsung", "slug": "samsung", "descricao": "Eletrônicos e eletrodomésticos"},
    {"nome": "Dell", "slug": "dell", "descricao": "Computadores e periféricos"},
    {"nome": "Sony", "slug": "sony", "descricao": "Eletrônicos e entretenimento"},
    {"nome": "LG", "slug": "lg", "descricao": "Eletrônicos e eletrodomésticos"},
    {"nome": "Nike", "slug": "nike", "descricao": "Artigos esportivos"},
    {"nome": "Adidas", "slug": "adidas", "descricao": "Moda esportiva"},
    {"nome": "Philips", "slug": "philips", "descricao": "Saúde e iluminação"},
    {"nome": "Bosch", "slug": "bosch", "descricao": "Ferramentas e eletrodomésticos"},
    {"nome": "Logitech", "slug": "logitech", "descricao": "Periféricos e acessórios"},
]

CATEGORIES = [
    {"nome": "Eletrônicos", "slug": "eletronicos", "ordem": 1},
    {"nome": "Smartphones", "slug": "smartphones", "categoria_pai_slug": "eletronicos", "ordem": 1},
    {"nome": "Televisores", "slug": "televisores", "categoria_pai_slug": "eletronicos", "ordem": 2},
    {"nome": "Áudio", "slug": "audio", "categoria_pai_slug": "eletronicos", "ordem": 3},
    {"nome": "Informática", "slug": "informatica", "ordem": 2},
    {"nome": "Notebooks", "slug": "notebooks", "categoria_pai_slug": "informatica", "ordem": 1},
    {"nome": "Periféricos", "slug": "perifericos", "categoria_pai_slug": "informatica", "ordem": 2},
    {"nome": "Moda", "slug": "moda", "ordem": 3},
    {"nome": "Calçados", "slug": "calcados", "categoria_pai_slug": "moda", "ordem": 1},
    {"nome": "Roupas", "slug": "roupas", "categoria_pai_slug": "moda", "ordem": 2},
    {"nome": "Acessórios", "slug": "acessorios", "categoria_pai_slug": "moda", "ordem": 3},
    {"nome": "Casa", "slug": "casa", "ordem": 4},
    {"nome": "Eletrodomésticos", "slug": "eletrodomesticos", "categoria_pai_slug": "casa", "ordem": 1},
    {"nome": "Ferramentas", "slug": "ferramentas", "categoria_pai_slug": "casa", "ordem": 2},
]

PRODUCTS = [
    {"nome": "iPhone 16 Pro Max 256GB", "sku": "IP16PM256", "categoria": "Smartphones", "marca": "Apple",
     "descricao": "Smartphone topo de linha com chip A18 Pro, tela OLED 6.9\", câmera 48MP e bateria de longa duração.",
     "preco_custo": "6200.00", "preco_venda": "10999.00", "quantidade_estoque": 25, "estoque_minimo": 5,
     "ean": "1234567890123", "peso_g": 227, "altura_cm": "16.0", "largura_cm": "7.6", "profundidade_cm": "0.8", "destaque": True},
    {"nome": "Samsung Galaxy S25 Ultra", "sku": "SGS25ULT", "categoria": "Smartphones", "marca": "Samsung",
     "descricao": "Smartphone com tela Dynamic AMOLED 6.9\", câmera 200MP, S Pen e processador Exynos 2500.",
     "preco_custo": "5100.00", "preco_venda": "8999.00", "quantidade_estoque": 30, "estoque_minimo": 5,
     "ean": "2234567890123", "peso_g": 219, "altura_cm": "16.2", "largura_cm": "7.7", "profundidade_cm": "0.9", "destaque": True},
    {"nome": "MacBook Pro 16\" M4", "sku": "MBP16M4", "categoria": "Notebooks", "marca": "Apple",
     "descricao": "Notebook profissional com chip M4 Ultra, 36GB RAM unificada, SSD 1TB e tela Liquid Retina XDR 16.2\".",
     "preco_custo": "14500.00", "preco_venda": "24999.00", "quantidade_estoque": 10, "estoque_minimo": 2,
     "ean": "3234567890123", "peso_g": 2140, "altura_cm": "35.6", "largura_cm": "24.8", "profundidade_cm": "1.7", "destaque": True},
    {"nome": "Dell XPS 15 OLED", "sku": "DXPS15OL", "categoria": "Notebooks", "marca": "Dell",
     "descricao": "Notebook ultrafino com Intel Core Ultra 9, 32GB RAM, SSD 1TB e tela OLED 3.5K 15.6\".",
     "preco_custo": "8200.00", "preco_venda": "14999.00", "quantidade_estoque": 15, "estoque_minimo": 3,
     "ean": "4234567890123", "peso_g": 1800, "altura_cm": "34.4", "largura_cm": "23.0", "profundidade_cm": "1.8"},
    {"nome": "Samsung Smart TV 65\" OLED S95D", "sku": "SSTV65S95", "categoria": "Televisores", "marca": "Samsung",
     "descricao": "Smart TV OLED 4K 65\" com processador NQ4 AI, Dolby Atmos e taxa de atualização 144Hz.",
     "preco_custo": "5200.00", "preco_venda": "8999.00", "quantidade_estoque": 8, "estoque_minimo": 2,
     "ean": "5234567890123", "peso_g": 16200, "altura_cm": "144.3", "largura_cm": "82.9", "profundidade_cm": "2.5", "destaque": True},
    {"nome": "Sony WH-1000XM6", "sku": "SWH1000X6", "categoria": "Áudio", "marca": "Sony",
     "descricao": "Fone de ouvido Bluetooth com cancelamento de ruído ativo, 40h de bateria e som Hi-Res.",
     "preco_custo": "1400.00", "preco_venda": "2599.00", "quantidade_estoque": 40, "estoque_minimo": 8,
     "ean": "6234567890123", "peso_g": 250, "altura_cm": "18.5", "largura_cm": "15.0", "profundidade_cm": "7.5", "destaque": True},
    {"nome": "AirPods Pro 3", "sku": "APPRO3", "categoria": "Áudio", "marca": "Apple",
     "descricao": "Fones de ouvido True Wireless com cancelamento de ruído adaptativo, áudio espacial e chip H3.",
     "preco_custo": "1100.00", "preco_venda": "2499.00", "quantidade_estoque": 50, "estoque_minimo": 10,
     "ean": "7234567890123", "peso_g": 46, "altura_cm": "4.5", "largura_cm": "5.0", "profundidade_cm": "2.2", "destaque": True},
    {"nome": "Dell UltraSharp 27\" 4K U2724D", "sku": "DUS27U27", "categoria": "Periféricos", "marca": "Dell",
     "descricao": "Monitor IPS 4K UHD 27\" com USB-C Hub, 100% sRGB e ajuste de altura.",
     "preco_custo": "2100.00", "preco_venda": "3999.00", "quantidade_estoque": 12, "estoque_minimo": 3,
     "ean": "8234567890123", "peso_g": 4300, "altura_cm": "61.3", "largura_cm": "18.8", "profundidade_cm": "50.0"},
    {"nome": "Logitech MX Master 3S", "sku": "LMXMS3S", "categoria": "Periféricos", "marca": "Logitech",
     "descricao": "Mouse ergonômico sem fio com sensor 8000 DPI, rolagem MagSpeed e 3 dispositivos.",
     "preco_custo": "280.00", "preco_venda": "599.00", "quantidade_estoque": 60, "estoque_minimo": 15,
     "ean": "9234567890123", "peso_g": 141, "altura_cm": "12.4", "largura_cm": "8.5", "profundidade_cm": "5.1"},
    {"nome": "Nike Air Max 2025", "sku": "NAM2025", "categoria": "Calçados", "marca": "Nike",
     "descricao": "Tênis casual com amortecimento Air Max full-length, cabedal em mesh respirável e solado de borracha.",
     "preco_custo": "320.00", "preco_venda": "799.00", "quantidade_estoque": 45, "estoque_minimo": 10,
     "ean": "1023456789012", "peso_g": 380},
    {"nome": "Adidas Ultraboost 25", "sku": "ADUB25", "categoria": "Calçados", "marca": "Adidas",
     "descricao": "Tênis de corrida com entressola Boost, upper Primeknit e caimento sock-like.",
     "preco_custo": "350.00", "preco_venda": "899.00", "quantidade_estoque": 35, "estoque_minimo": 8,
     "ean": "1123456789012", "peso_g": 340},
    {"nome": "Samsung Galaxy Watch 7", "sku": "SGW7", "categoria": "Acessórios", "marca": "Samsung",
     "descricao": "Smartwatch com Wear OS 5, bio-sensores avançados, GPS e bateria de 5 dias.",
     "preco_custo": "1100.00", "preco_venda": "2199.00", "quantidade_estoque": 20, "estoque_minimo": 4,
     "ean": "1223456789012", "peso_g": 59, "destaque": True},
    {"nome": "Apple Watch Series 10", "sku": "AWS10", "categoria": "Acessórios", "marca": "Apple",
     "descricao": "Smartwatch com tela OLED always-on, sensor de temperatura, ECG e detecção de quedas.",
     "preco_custo": "1800.00", "preco_venda": "4499.00", "quantidade_estoque": 18, "estoque_minimo": 4,
     "ean": "1323456789012", "peso_g": 42, "destaque": True},
    {"nome": "Sony Bravia 75\" Mini LED XR", "sku": "SB75MLXR", "categoria": "Televisores", "marca": "Sony",
     "descricao": "TV Mini LED 4K 75\" com processador XR Cognitive, Dolby Vision e taxa de 120Hz.",
     "preco_custo": "7200.00", "preco_venda": "12999.00", "quantidade_estoque": 5, "estoque_minimo": 1,
     "ean": "1423456789012", "peso_g": 28500, "altura_cm": "167.0", "largura_cm": "95.8", "profundidade_cm": "4.5", "destaque": True},
    {"nome": "LG Soundbar S95TR", "sku": "LGSB95TR", "categoria": "Áudio", "marca": "LG",
     "descricao": "Soundbar 9.1.5 canais com Dolby Atmos, subwoofer wireless e caixas traseiras.",
     "preco_custo": "1800.00", "preco_venda": "3499.00", "quantidade_estoque": 14, "estoque_minimo": 3,
     "ean": "1523456789012", "peso_g": 5200, "altura_cm": "122.0", "largura_cm": "6.3", "profundidade_cm": "13.5"},
    {"nome": "Philips Hue White & Color Kit", "sku": "PHUEWCK", "categoria": "Casa", "marca": "Philips",
     "descricao": "Kit 3 lâmpadas inteligentes RGB, bridge Hue e app. Controle por voz e automação.",
     "preco_custo": "420.00", "preco_venda": "899.00", "quantidade_estoque": 30, "estoque_minimo": 6,
     "ean": "1623456789012", "peso_g": 680},
    {"nome": "Bosch Professional GSB 18V-50", "sku": "BPGSB1850", "categoria": "Ferramentas", "marca": "Bosch",
     "descricao": "Furadeira de impacto sem fio 18V, 50Nm de torque, 2 baterias ProCORE18V.",
     "preco_custo": "820.00", "preco_venda": "1899.00", "quantidade_estoque": 12, "estoque_minimo": 3,
     "ean": "1723456789012", "peso_g": 2100},
    {"nome": "LG French Door Refrigerator", "sku": "LGFDR635", "categoria": "Eletrodomésticos", "marca": "LG",
     "descricao": "Geladeira French Door 635L com Ice Maker, Smart ThinQ e eficiência A++.",
     "preco_custo": "3400.00", "preco_venda": "5999.00", "quantidade_estoque": 6, "estoque_minimo": 1,
     "ean": "1823456789012", "peso_g": 95000, "altura_cm": "179.0", "largura_cm": "91.2", "profundidade_cm": "73.0", "destaque": True},
    {"nome": "Samsung Bespoke AI Washer", "sku": "SBW22A", "categoria": "Eletrodomésticos", "marca": "Samsung",
     "descricao": "Lavadora de roupas 22kg com AI Ecobubble, autodosing e conectividade SmartThings.",
     "preco_custo": "1800.00", "preco_venda": "3499.00", "quantidade_estoque": 8, "estoque_minimo": 2,
     "ean": "1923456789012", "peso_g": 72000, "altura_cm": "98.0", "largura_cm": "68.6", "profundidade_cm": "72.5"},
    {"nome": "Nike Dri-FIT Adv Run Division Top", "sku": "NDFADVTP", "categoria": "Roupas", "marca": "Nike",
     "descricao": "Camiseta de corrida masculina com tecnologia Dri-FIT ADV, costuras planas e bolso traseiro.",
     "preco_custo": "85.00", "preco_venda": "249.00", "quantidade_estoque": 100, "estoque_minimo": 20,
     "ean": "2023456789012", "peso_g": 120},
    {"nome": "Adidas Essentials 3-Stripes Hoodie", "sku": "ADE3SH", "categoria": "Roupas", "marca": "Adidas",
     "descricao": "Moletom unissex com fleece macio, bolso canguru e punhos canelados.",
     "preco_custo": "95.00", "preco_venda": "299.00", "quantidade_estoque": 80, "estoque_minimo": 15,
     "ean": "2123456789012", "peso_g": 450},
    {"nome": "Logitech G Pro X Superlight 2", "sku": "LGPXSL2", "categoria": "Periféricos", "marca": "Logitech",
     "descricao": "Mouse gamer sem fio ultraleve 60g, sensor Hero 2 44K DPI e bateria de 95h.",
     "preco_custo": "420.00", "preco_venda": "999.00", "quantidade_estoque": 28, "estoque_minimo": 6,
     "ean": "2223456789012", "peso_g": 60},
    {"nome": "Sony Alpha A7 V", "sku": "SALPHA7V", "categoria": "Acessórios", "marca": "Sony",
     "descricao": "Câmera mirrorless full-frame 61MP com estabilização IBIS de 8 stops e vídeo 8K.",
     "preco_custo": "12800.00", "preco_venda": "22999.00", "quantidade_estoque": 5, "estoque_minimo": 1,
     "ean": "2323456789012", "peso_g": 650, "altura_cm": "13.1", "largura_cm": "9.6", "profundidade_cm": "7.6", "destaque": True},
    {"nome": "Dell PowerEdge R760xs", "sku": "DPER760", "categoria": "Informática", "marca": "Dell",
     "descricao": "Servidor rack 1U com Intel Xeon 6ª geração, 256GB RAM DDR5 e storage hot-swap.",
     "preco_custo": "18500.00", "preco_venda": "34999.00", "quantidade_estoque": 3, "estoque_minimo": 1,
     "ean": "2423456789012", "peso_g": 12700},
    {"nome": "Apple iPad Pro M4 13\"", "sku": "AIPM413", "categoria": "Notebooks", "marca": "Apple",
     "descricao": "Tablet profissional com chip M4, tela Ultra Retina XDR 13\", 1TB e Apple Pencil Pro.",
     "preco_custo": "7500.00", "preco_venda": "13999.00", "quantidade_estoque": 12, "estoque_minimo": 3,
     "ean": "2523456789012", "peso_g": 582, "altura_cm": "28.1", "largura_cm": "21.5", "profundidade_cm": "0.6", "destaque": True},
    {"nome": "Samsung Galaxy Tab S10 Ultra", "sku": "SGTS10U", "categoria": "Notebooks", "marca": "Samsung",
     "descricao": "Tablet com tela Dynamic AMOLED 14.6\", 12GB RAM, 512GB e S Pen incluída.",
     "preco_custo": "5200.00", "preco_venda": "8999.00", "quantidade_estoque": 10, "estoque_minimo": 2,
     "ean": "2623456789012", "peso_g": 718, "altura_cm": "32.6", "largura_cm": "20.8", "profundidade_cm": "0.6"},
    {"nome": "Philips Airfryer XXL Premium", "sku": "PAFXXLP", "categoria": "Eletrodomésticos", "marca": "Philips",
     "descricao": "Airfryer 7.3L com tecnologia Rapid Air, 14 modos de cozimento e display touch.",
     "preco_custo": "450.00", "preco_venda": "999.00", "quantidade_estoque": 22, "estoque_minimo": 5,
     "ean": "2723456789012", "peso_g": 7200, "altura_cm": "31.5", "largura_cm": "32.5", "profundidade_cm": "36.5"},
    {"nome": "Bosch Serie 8 Built-in Oven", "sku": "BS8BIOV", "categoria": "Eletrodomésticos", "marca": "Bosch",
     "descricao": "Forno elétrico embutido 71L com PerfectBake, autolimpeza pirolítica e Home Connect.",
     "preco_custo": "2400.00", "preco_venda": "4999.00", "quantidade_estoque": 7, "estoque_minimo": 2,
     "ean": "2823456789012", "peso_g": 37000, "altura_cm": "59.5", "largura_cm": "59.6", "profundidade_cm": "54.8"},
    {"nome": "Nike Pro 365 Leggings", "sku": "NP365LEG", "categoria": "Roupas", "marca": "Nike",
     "descricao": "Leggings feminino de alta compressão com tecnologia Dri-FIT e cintura larga.",
     "preco_custo": "75.00", "preco_venda": "199.00", "quantidade_estoque": 60, "estoque_minimo": 12,
     "ean": "2923456789012", "peso_g": 200},
    {"nome": "Adidas Predator Elite FG", "sku": "ADPEFG", "categoria": "Calçados", "marca": "Adidas",
     "descricao": "Chuteira de campo com cabedal Hybridtouch, laceless e solado de travas mistas.",
     "preco_custo": "420.00", "preco_venda": "1099.00", "quantidade_estoque": 25, "estoque_minimo": 5,
     "ean": "3023456789012", "peso_g": 290},
    {"nome": "LG UltraFine 32\" 4K Ergo", "sku": "LUF32ERG", "categoria": "Periféricos", "marca": "LG",
     "descricao": "Monitor IPS 4K 32\" com braço ergonômio C-Clamp, USB-C 90W e 98% DCI-P3.",
     "preco_custo": "2800.00", "preco_venda": "4999.00", "quantidade_estoque": 10, "estoque_minimo": 2,
     "ean": "3123456789012", "peso_g": 6700, "altura_cm": "71.4", "largura_cm": "21.0", "profundidade_cm": "56.0", "destaque": True},
]


# ─── Helpers ────────────────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "Smartphones": "smartphone",
    "Televisores": "television",
    "Áudio": "headphone",
    "Notebooks": "notebook,computer",
    "Informática": "computer",
    "Periféricos": "computer,peripheral",
    "Calçados": "sneaker",
    "Roupas": "clothing",
    "Acessórios": "smartwatch",
    "Casa": "lamp",
    "Eletrodomésticos": "drill",
    "Ferramentas": "drill",
    "Eletrônicos": "electronics",
    "Moda": "fashion",
}

def img_url(sku: str, category: str) -> str:
    kw = CATEGORY_KEYWORDS.get(category, "product")
    return f"https://loremflickr.com/640/640/{kw}?lock={hash(sku) & 0x7FFFFFFF}"


def check_health(base_url: str) -> bool:
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        return r.status_code == 200
    except requests.ConnectionError:
        return False


def log(msg: str) -> None:
    print(f"  • {msg}")


# ─── Main ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed database with real products and images")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="FastAPI server base URL")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    api = f"{base}{API_PREFIX}"

    print(f"\n═══ Seed Products ═══\n  Server: {base}\n")

    # ── Health ──────────────────────────────────────────────────────
    if not check_health(base):
        print("  ✖ Servidor não está rodando. Inicie com 'uvicorn src.main:app --reload'")
        sys.exit(1)
    print("  ✔ Servidor OK\n")

    s = requests.Session()

    # ── Auth ────────────────────────────────────────────────────────
    admin_email = "admin@seed.com"
    admin_pass = "seedadmin123"
    log("Registrando admin…")
    r = s.post(f"{api}/auth/register", json={"nome": "Admin Seed", "email": admin_email, "senha": admin_pass})
    if r.status_code == 409:  # already exists
        log("Admin já existe")
    elif r.status_code == 201:
        log("Admin criado")
    else:
        print(f"  ✖ Erro register: {r.status_code} {r.text}")
        sys.exit(1)

    log("Fazendo login…")
    r = s.post(f"{api}/auth/login", data={"username": admin_email, "password": admin_pass})
    if r.status_code != 200:
        print(f"  ✖ Erro login: {r.status_code} {r.text}")
        sys.exit(1)
    token = r.json()["access_token"]
    s.headers["Authorization"] = f"Bearer {token}"
    log("Autenticado\n")

    # ── Brands ──────────────────────────────────────────────────────
    brand_slug_to_id: dict[str, UUID] = {}
    log("Criando marcas…")
    for b in BRANDS:
        r = s.post(f"{api}/brands", json=b)
        if r.status_code == 201:
            brand_slug_to_id[b["slug"]] = r.json()["id"]
        elif r.status_code == 409:
            brand_slug_to_id[b["slug"]] = s.get(f"{api}/brands", params={"active_only": True}).json()[0]["id"]
        else:
            print(f"  ⚠ Marca {b['slug']}: {r.status_code} {r.text[:80]}")
    log(f"{len(BRANDS)} marcas\n")

    # ── Categories ──────────────────────────────────────────────────
    cat_slug_to_id: dict[str, UUID] = {}
    log("Criando categorias…")
    cats_flat = CATEGORIES.copy()
    while cats_flat:
        remaining = []
        for c in cats_flat:
            parent = c.pop("categoria_pai_slug", None)
            payload = {k: v for k, v in c.items() if v is not None}
            if parent:
                pid = cat_slug_to_id.get(parent)
                if not pid:
                    remaining.append({**c, "categoria_pai_slug": parent})
                    continue
                payload["categoria_pai_id"] = str(pid)
            r = s.post(f"{api}/categories", json=payload)
            if r.status_code == 201:
                cat_slug_to_id[c["slug"]] = r.json()["id"]
            elif r.status_code == 409:
                log(f"  Categoria {c['slug']} já existe — pulando")
                # Try to fetch existing
                cat_list = s.get(f"{api}/categories", params={"active_only": True}).json()
                for x in cat_list:
                    if x["slug"] == c["slug"]:
                        cat_slug_to_id[c["slug"]] = x["id"]
                        break
            else:
                print(f"  ⚠ Categoria {c['slug']}: {r.status_code} {r.text[:80]}")
        cats_flat = remaining
    log(f"{len(CATEGORIES)} categorias\n")

    # ── Products + Images ────────────────────────────────────────────
    log(f"Criando {len(PRODUCTS)} produtos com imagens…\n")

    def create_product(p: dict) -> tuple[str, str]:
        brand_id = brand_slug_to_id.get(p["marca"])
        cat_slug = p["categoria"].lower().replace(" ", "").replace("ç", "c").replace("ã", "a").replace("é", "e").replace("ó", "o")
        cat_id = cat_slug_to_id.get(cat_slug)

        payload = {
            "nome": p["nome"],
            "sku": p["sku"],
            "descricao": p["descricao"],
            "categoria": p["categoria"],
            "preco_custo": p["preco_custo"],
            "preco_venda": p["preco_venda"],
            "quantidade_estoque": p["quantidade_estoque"],
            "estoque_minimo": p["estoque_minimo"],
            "destaque": p.get("destaque", False),
            "ativo": True,
        }
        if brand_id:
            payload["marca_id"] = str(brand_id)
        if cat_id:
            payload["categoria_id"] = str(cat_id)
        if p.get("ean"):
            payload["ean"] = p["ean"]
        if p.get("peso_g"):
            payload["peso_g"] = p["peso_g"]
        if p.get("altura_cm"):
            payload["altura_cm"] = p["altura_cm"]
        if p.get("largura_cm"):
            payload["largura_cm"] = p["largura_cm"]
        if p.get("profundidade_cm"):
            payload["profundidade_cm"] = p["profundidade_cm"]

        r = s.post(f"{api}/products", json=payload)
        if r.status_code == 409:
            log(f"  Produto {p['sku']} já existe — pulando")
            return p["sku"], "skipped"
        if r.status_code != 201:
            print(f"  ⚠ Produto {p['sku']}: {r.status_code} {r.text[:100]}")
            return p["sku"], "error"
        prod = r.json()
        pid = prod["id"]

        # Upload image
        img_src = img_url(p["sku"], p["categoria"])
        try:
            img_resp = requests.get(img_src, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if img_resp.status_code != 200:
                # Fallback to picsum
                fallback = f"https://picsum.photos/seed/{p['sku'].lower()}/640/640"
                img_resp = requests.get(fallback, timeout=15)
            if img_resp.status_code == 200:
                files = {"file": (f"{p['sku']}.jpg", io.BytesIO(img_resp.content), "image/jpeg")}
                ir = s.post(f"{api}/products/{pid}/images", files=files)
                if ir.status_code == 201:
                    return p["sku"], "ok"
                else:
                    return p["sku"], f"img_err {ir.status_code}"
            return p["sku"], "img_dl_err"
        except requests.RequestException as e:
            return p["sku"], f"img_exc {e}"

    start = time.time()
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(create_product, p): p for p in PRODUCTS}
        ok = skipped = err = 0
        for f in as_completed(futures):
            sku, status = f.result()
            if status == "ok":
                ok += 1
            elif status == "skipped":
                skipped += 1
            else:
                err += 1
                print(f"  ⚠ {sku}: {status}")

    elapsed = time.time() - start
    print(f"\n  ✔ {ok} produtos criados com imagem, {skipped} já existiam, {err} com erro ({elapsed:.1f}s)\n")
    print("═══ Seed concluído! ═══\n")


if __name__ == "__main__":
    main()
