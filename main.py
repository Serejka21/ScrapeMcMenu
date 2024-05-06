import os
import subprocess
import sys

from fastapi import FastAPI, Query, HTTPException, Header

from menu.api import utils


app = FastAPI(
    docs_url="/docs",
    openapi_url="/openapi.json",
)


SECRET_KEY = os.environ.get("SECRET_KEY")


@app.get("/run_spider/",
         description=
         """
         Send GET request to this endpoint to run Spider script
         and scrape data from source. It will save the data to
         data.json file.
         IMPORTANT: to get access for present endpoint you need to
         set environment SECRET_KEY due to example in .env.sample
         and provide it in request headers .
         """)
async def run_spiders(secret_key: str = Header(None)) -> dict:
    if secret_key != SECRET_KEY:
        raise HTTPException(
            status_code=403, detail="Forbidden: Invalid secret key"
        )

    command = ["scrapy", "crawl", "menu_scraper", "-o", "data.json"]

    os.chdir("menu")
    sys.path.append("menu")
    with open("scrapy_output.log", "w") as log_file:
        result = subprocess.run(
            command, stdout=log_file, stderr=log_file, text=True, check=False
        )

    if result.returncode != 0:
        with open("scrapy_output.log", "r") as log_file:
            error_message = log_file.read()
        raise HTTPException(
            status_code=500,
            detail=f"Spider failed: {error_message}"
        )

    return {"status": "Spider started", "output": result.stdout}


@app.get("/all_products/",
         description=
         """
         Sen GET request to this endpoint to get all products
         from scraped data in data.json file.
         If source doesn't exist, it will cause error.
         Run scrapy crawl menu_scraper data.json from terminal
         to scrape data and try again.
         """)
async def get_all_products(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=97)
) -> dict:
    start = (page - 1) * size
    end = start + size
    try:
        scraped_data = utils.get_json_data()
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail="No data scraped now"
        )

    if not scraped_data:
        raise HTTPException(
            status_code=404, detail="No data scraped now"
        )

    if not isinstance(scraped_data, list):
        raise HTTPException(status_code=500, detail="Unexpected data format")

    if start >= len(scraped_data):
        raise HTTPException(status_code=404, detail="Page out of range")

    paginated_data = scraped_data[start:end]

    return {
        "total_items": len(scraped_data),
        "current_page": page,
        "page_size": size,
        "data": paginated_data
    }


@app.get("/{product_name}/",
         description=
         """
         Send GET request and provide product_name attrib to find
         all similar products data with related name.
         If name does not exist it will return info message.
         Register does not matter
         """)
async def get_product(product_name: str) -> dict:
    try:
        scraped_data = utils.get_json_data()
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail="No data scraped now"
        )
    product_data = []

    for product in scraped_data:
        if product_name.lower() in product["name"].lower():
            product_data.append(product)

    if len(product_data) == 0:
        raise HTTPException(
            status_code=404, detail="No product found"
        )

    return {"products": product_data}


@app.get("/{product_name}/{product_field}/",
         description=
         """
         Send GET request and provide product_name and product_field attribs
         to get all similar products field data with related product name.
         If name does not exist it will return info message.
         Register does not matter
         """)
async def get_product_field(product_name: str, product_field: str) -> dict:
    try:
        scraped_data = utils.get_json_data()
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail="No data scraped now"
        )

    product_data = {}

    for product in scraped_data:
        if product_name.lower() in product["name"].lower():
            product_data[product["name"]] = product.get(product_field)

    if len(product_data) == 0:
        raise HTTPException(
            status_code=404, detail="No product found"
        )

    return product_data
