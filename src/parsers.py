from datetime import datetime

from bs4 import BeautifulSoup

from utils.log import logger


def parse_home_sales(response) -> list:
    soup = BeautifulSoup(response, "html.parser")

    products = []

    container = soup.select_one("div.box.product_featured")

    if not container:
        logger.warning("Container div.box.product_featured not found")
        return []

    for li in container.select("li.product"):
        item = li.select_one("div.item-product")
        if not item:
            continue

        # URL e nome
        name_tag = item.select_one(".name a.product-name")
        url = name_tag["href"] if name_tag else None
        name = name_tag.get_text(strip=True) if name_tag else None

        # Autor
        author_tag = item.select_one("p.author a")
        author_name = author_tag.get_text(strip=True) if author_tag else None
        author_id = None
        if author_tag and "author_id=" in author_tag["href"]:
            author_id = author_tag["href"].split("author_id=")[-1]

        # Preços
        price_old = None
        price_new = None

        old_tag = item.select_one(".price .price-old")
        new_tag = item.select_one(".price .price-new")

        if old_tag:
            price_old = old_tag.get_text(strip=True)

        if new_tag:
            price_new = new_tag.get_text(strip=True)

        # Desconto
        discount_tag = item.select_one(".flag-discount")
        discount = discount_tag.get_text(strip=True) if discount_tag else None

        # Flags
        is_new = bool(item.select_one(".flag.novidade"))

        date_scrap = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        products.append(
            {
                "name": name,
                "url": url,
                "author_name": author_name,
                "author_id": author_id,
                "price_old": price_old,
                "price_new": price_new,
                "discount": discount,
                "is_new": is_new,
                "source": "home_featured",
                "created_at": date_scrap,
            }
        )
        list_size = len(products)
        logger.info(f"Retrieved {list_size} registers.")

    return products
