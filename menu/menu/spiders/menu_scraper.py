from typing import Any, Dict, Generator

import scrapy
from scrapy import Selector
from scrapy.http import Response
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By


class MenuScraperSpider(scrapy.Spider):
    name = "menu_scraper"
    allowed_domains = ["www.mcdonalds.com"]
    start_urls = ["https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html"]

    def parse(
            self,
            response: Response
    ) -> Generator[scrapy.Request, None, None]:
        for product_url in response.css(
                "li.cmp-category__item a::attr(href)"
        ).getall():
            product_page = response.urljoin(product_url)
            yield SeleniumRequest(
                url=product_page, callback=self.parse_product, wait_time=3
            )

    def _parse_product_nutritions(
            self, response: Response
    ) -> Selector:
        driver = response.meta['driver']

        button = driver.find_element(
            By.ID, "accordion-29309a7a60-item-9ea8a10642-button"
        )
        button.click()

        page_source = driver.page_source
        selector = Selector(text=page_source)

        return selector

    def parse_product(self, response: Response) -> Dict[str, Any]:
        nutritions = self._parse_product_nutritions(response) #TODO: implement loop for every product

        yield {
            "name": response.css(
                "span.cmp-product-details-main__heading-title::text"
            ).get(),
            "description": response.xpath(
                "string(//div[@class='cmp-text'])"
            ).get().strip().replace("\n", ""),
            "calories": nutritions.css(
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
            ).get().strip()
        }
