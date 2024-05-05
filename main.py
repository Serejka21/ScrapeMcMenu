from fastapi import FastAPI, Query, HTTPException
from menu.api import utils

app = FastAPI()


@app.get("/all_products/")
async def get_all_products(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100)
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


@app.get("/{product_name}/")
async def get_product(product_name: str) -> dict:
    return {}


@app.get("/{product_name}/{product_field}/")
async def get_product_field(product_name: str, product_field: str) -> dict:
    return {}
