from datetime import datetime
from pathlib import Path

from extractor import Extractor
from loader import load_data
from parsers import parse_home_sales
from utils.log import logger


def extraction_featured_books(output_dir: Path):
    url_base = "https://videeditorial.com.br/"
    extract = Extractor()
    html = extract.make_request(url=url_base, mode="text")
    products = parse_home_sales(html)

    file_date = datetime.now().strftime("%Y-%m-%d")
    new_filename = f"vide_livros_em_destaque_{file_date}"

    extract.save_json(data=products, output_dir=output_dir, filename=new_filename)
    logger.info("Extraction complete!")


if __name__ == "__main__":
    path = "/media/lucas/Files/2.Projetos/0.mylake/raw/vide"

    extraction_featured_books(path)

    load_data(
        dir=path,
        file_extension="json",
        schema="raw",
        table_name="vide_raw_livros_em_destaque",
    )
