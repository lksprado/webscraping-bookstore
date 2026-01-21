from datetime import datetime
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup

from .utils.log import logger


def get_routes():
    """
    Obter o "historia.html" em Devtools > Sources
    """
    BASE_URL = "https://videeditorial.com.br/"

    with open("data/historia.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    routes = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(strip=True)

        # ignora âncoras vazias e JS
        if not href or href.startswith("#") or href.lower().startswith("javascript"):
            continue

        # transforma em URL absoluta (se for relativa)
        full_url = urljoin(BASE_URL, href)

        routes.append(
            {
                "text": text,
                "href_raw": href,
                "href_full": full_url,
            }
        )

    df = pd.DataFrame(routes)
    created_at = datetime.now().strftime("%Y-%m-%d")
    df.drop_duplicates(inplace=True)
    df.to_csv(f"data/all_hrefs_{created_at}.csv", sep=";", index=False)


def parse_products_page(
    response: str,
    *,
    container_selector: str,
    item_selector: str,
    source: str,
    has_category: bool = False,
) -> list:
    soup = BeautifulSoup(response, "html.parser")
    products = []

    # Categoria (só para páginas de categoria)
    category_name = None
    if has_category:
        category_tag = soup.select_one(".back-category a")
        category_name = category_tag.get_text(strip=True) if category_tag else None

    container = soup.select_one(container_selector)
    if not container:
        logger.warning(f"Container {container_selector} not found")
        return []

    for li in container.select(item_selector):
        item = li.select_one("div.item-product")
        if not item:
            continue

        # Nome + URL
        name_tag = item.select_one(".name a.product-name")
        name = name_tag.get_text(strip=True) if name_tag else None

        raw_url = name_tag["href"] if name_tag and name_tag.has_attr("href") else None
        url = urljoin("https://videeditorial.com.br/", raw_url) if raw_url else None

        # Autor
        author_tag = item.select_one("p.author a")
        author_name = author_tag.get_text(strip=True) if author_tag else None

        author_id = None
        if author_tag and "author_id=" in author_tag.get("href", ""):
            author_id = author_tag["href"].split("author_id=")[-1]

        # Preços
        old_tag = item.select_one(".price .price-old")
        new_tag = item.select_one(".price .price-new")

        price_old = old_tag.get_text(strip=True) if old_tag else None
        price_new = new_tag.get_text(strip=True) if new_tag else None

        # Desconto
        discount_tag = item.select_one(".flag-discount")
        discount = discount_tag.get_text(strip=True) if discount_tag else None

        # Flags
        is_new = bool(item.select_one(".flag.novidade"))

        date_scrap = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        product = {
            "name": name,
            "url": url,
            "author_name": author_name,
            "author_id": author_id,
            "price_old": price_old,
            "price_new": price_new,
            "discount": discount,
            "is_new": is_new,
            "source": source,
            "created_at": date_scrap,
        }

        if has_category:
            product["category"] = category_name

        products.append(product)

    logger.info(f"[{source}] Retrieved {len(products)} registers.")
    return products


def parse_home_sales(response) -> list:
    return parse_products_page(
        response,
        container_selector="div.box.product_featured",
        item_selector="li.product",
        source="home_featured",
        has_category=False,
    )


def parse_content_pages(response) -> list:
    return parse_products_page(
        response,
        container_selector="div.product-list",
        item_selector="div.product",
        source="category_page",
        has_category=True,
    )


if __name__ == "__main__":
    # get_routes()
    with open("data/content_page.html", "r", encoding="utf-8") as f:
        books = parse_content_pages(f)

    print(books)
