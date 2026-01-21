from datetime import datetime
from pathlib import Path

import yaml

from .extractor import Extractor
from .parsers import parse_home_sales
from .utils.log import logger


def extraction_featured_books(output_dir: Path):
    url_base = "https://videeditorial.com.br/"
    extract = Extractor()
    html = extract.make_request(url=url_base, mode="text")
    products = parse_home_sales(html)

    file_date = datetime.now().strftime("%Y-%m-%d")
    new_filename = f"vide_livros_em_destaque_{file_date}"

    extract.save_json(data=products, output_dir=output_dir, filename=new_filename)
    logger.info("Extraction complete!")


def extract_link_content():
    extract = Extractor()
    with open("data/config.yml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    hrefs = cfg.get("hrefs", [])
    links = [item["link"] for item in hrefs if "link" in item]
    for link in links:
        html = extract.make_request(url=link, mode="text")

        return html


if __name__ == "__main__":
    from bs4 import BeautifulSoup
    # path = "/media/lucas/Files/2.Projetos/0.mylake/raw/vide"

    # extraction_featured_books(path)

    # load_data(
    #     dir=path,
    #     file_extension="json",
    #     schema="raw",
    #     table_name="vide_raw_livros_em_destaque",
    # )
    html = extract_link_content()
    soup = BeautifulSoup(html, "html.parser")
    html = soup.prettify()
    with open("data/content_page.html", "w", encoding="utf-8") as f:
        f.write(html)
