from typing import Any, Dict, Generator

import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tenacity import (
    retry,
    wait_fixed,
    stop_after_attempt,
    retry_if_exception_type
)


class MenuScraperSpider(scrapy.Spider):
    name = "menu_scraper"
    allowed_domains = ["www.mcdonalds.com"]
    start_urls = ["https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html"]
    download_delay = 3

    def __init__(self):
        super().__init__()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options)

    def parse(
            self,
            response: Response,
            **kwargs
    ) -> Generator[scrapy.Request, None, None]:
        for product_url in response.css(
                "li.cmp-category__item a::attr(href)"
        ).getall():
            product_url = response.urljoin(product_url)
            nutritions_data = self._parse_product_nutritions(product_url)
            yield scrapy.Request(
                product_url,
                callback=self.parse_product,
                meta=nutritions_data,
            )

    @retry(
        wait=wait_fixed(2),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(exception_types=(AttributeError, ValueError)),
    )
    def _parse_product_nutritions(self, url: str) -> Dict[str, Any]:
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(
                    (By.ID, "accordion-29309a7a60-item-9ea8a10642")
                )
            )
            button = self.driver.find_element(
                By.ID, "accordion-29309a7a60-item-9ea8a10642-button"
            )
            button.click()
        except Exception as error:
            raise ValueError("Element nof found")

        page_source = self.driver.page_source
        nutritions = Selector(text=page_source)

        nutrition_data = {"calories": nutritions.css(
                "ul.cmp-nutrition-summary__heading-primary "
                "> li:nth-child(1) > span.value "
                "> span:nth-child(3)::text"
            ).get().strip(),
            "fats": nutritions.css(
                "ul.cmp-nutrition-summary__heading-primary "
                "> li:nth-child(2) > span.value "
                "> span:nth-child(3)::text"
            ).get().strip(),
            "carbs": nutritions.css(
                "ul.cmp-nutrition-summary__heading-primary "
                "> li:nth-child(3) > span.value "
                "> span:nth-child(3)::text"
            ).get().strip(),
            "proteins": nutritions.css(
                "ul.cmp-nutrition-summary__heading-primary "
                "> li:nth-child(4) > span.value "
                "> span:nth-child(3)::text"
            ).get().strip(),
            "unsaturated fats": nutritions.css(
                "div.secondarynutritions ul > li:nth-child(1) "
                "> span.value > span:nth-child(2)::text"
            ).get().split()[0].strip(),
            "sugar": nutritions.css(
                "div.secondarynutritions ul > li:nth-child(2) "
                "> span.value > span:nth-child(2)::text"
            ).get().split()[0].strip(),
            "salt": nutritions.css(
                "div.secondarynutritions ul > li:nth-child(3) "
                "> span.value > span:nth-child(2)::text"
            ).get().split()[0].strip(),
            "portion": nutritions.css(
                "div.secondarynutritions ul > li:nth-child(4) "
                "> span.value > span:nth-child(2)::text"
            ).get().strip().split()[0],
        }

        return nutrition_data

    @staticmethod
    def parse_product(response: Response) -> Dict[str, Any]:
        translation_table = str.maketrans({
            '\n': '',
            '\r': '',
        })
        yield {
            "name": response.css(
                "span.cmp-product-details-main__heading-title::text"
            ).get().translate(translation_table),
            "description": response.xpath(
                "string(//div[@class='cmp-text'])"
            ).get().strip().translate(translation_table),
            "calories": response.meta.get("calories", 0),
            "fats": response.meta.get("fats", 0),
            "carbs": response.meta.get("carbs", 0),
            "proteins": response.meta.get("proteins", 0),
            "unsaturated fats": response.meta.get("unsaturated fats", 0),
            "sugar": response.meta.get("sugar", 0),
            "salt": response.meta.get("salt", 0),
            "portion": response.meta.get("portion", 0),
        }
