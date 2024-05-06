
# FastAPI Service: McDonald`s Menu Scraper
FastAPI based application to view data as a result of scraping from McDonald`s menu.
Technologies used:
- FastAPI: for generating relevant endpoints and viewing resources
- Scrapy: for scraping and parsing data from a source
- Selenium: for emulating interactive actions on pages where dynamic content is expected to be loaded.

# How to start
Firstly, you should to clone repo locally

```
git clone the-link-from-your-forked-repo
```

In next step install and run venv
```
python -m venv venv
venv\Scripts\activate (Windows)
source venv/bin/activate (on macOS)
```

After that run and install requirement packages

```
pip install -r requirements.txt
```

Finally, you can run server and try to get data by API endpoints

```
uvicorn main:app --reload
```

To run scraping spider move to menu dir and execute
scrapy crawl Script
```
cd menu
scrapy crawl menu_scraper -o data.json
```
WARNING: If you want to change the file name, you must also change the value in FEEDS of the settings.py file and the corresponding name in utils.py of the get_json_data() method inside scraped_data variable
## API Reference

You can read short resources description in generated Swagger UI visited /docs endpoint
```http
  GET /docs
```

#### Get all items

```http
  GET /all_products/
```
Present endpoint will return a collect data in result of page scraping from .json data file
If data file doesn`t exist it will cause client-side error

It maintains pagination, provide 2 query params:
page (min=1) - to select page number
size (min=1, max=97) - to set count of elements once the page

If you set invalid param it will be handle by validation

Example request:
/all_products/?page=1&size=10


#### Get item by product_name

```http
  GET /{product_name}/
```

Provide product_name on ukrainian (The site is scraped on Ukrainian localization). It will return all entries in data collection from data.json.

Example:
```
{
  "products": [
    {
      "name": "Дабл Чізбургер",
      "description": "Два біфштекси з натуральної яловичини, два шматочки сиру «Чедер», два мариновані огірки, цибуля, гірчиця, кетчуп, булочка.",
      "calories": "475ккал",
      "fats": "27.3г",
      "carbs": "31.1г",
      "proteins": "26.5г",
      "unsaturated fats": "12.6г",
      "sugar": "6.5г",
      "salt": "2.5г",
      "portion": "163г"
    },
    {
      "name": "Чізбургер",
      "description": "Біфштекс із натуральної яловичини, шматочок сиру “Чеддер”, шматочок маринованого огірка та цибуля, заправлені гірчицею і кетчупом, у булочці з пшеничного борошна.",
      "calories": "298ккал",
      "fats": "13г",
      "carbs": "29г",
      "proteins": "16г",
      "unsaturated fats": "6.1г",
      "sugar": "7.6г",
      "salt": "1.6г",
      "portion": "108г"
    }
  ]
}
```

**INFO**: it will return client-side error if objects weren`t find with name or contains provided data in name field

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `product_name`  | `string` | **Required**.|

#### Get field value by field name from selected product

```http
  GET /{product_name}/{product_field}/
```
Provide product_name on ukrainian (The site is scraped on Ukrainian localization). 

It will return all entries in data collection from data.json. However, product_field should be provided on eng

It returns dict in format 
__{key(product_name): value(product_field)}__

Example:
```
{
  "Дабл Чізбургер": "2.5г",
  "Чізбургер": "1.6г",
  "Роял Чізбургер": "2.6г",
  "Чізбургер з беконом": "1.9г",
  "Дабл Роял Чізбургер": "3.0г"
}
```

**INFO**: it will return client-side error if objects weren't find with name or contains provided data in name field.
If you provide doesn't exist field you will get in result dict mull value

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `product_name`  | `string` | **Required**.|
| `product_field`  | `string` | **Required**.|


### Additional endpoint: Run scrape process
**Be carefule, this can cause a blockage on the victim's server side**

```http
  GET /run_spider/
```

Present endpoint run scrapy crawl from terminal and collect data to data.json file. 

It may take some time to finish scraping process.

For your security, this method requires to set in .env a SECRET_KEY variable (like it show in .env.sample)

If provided SECRET_KEY doesn`t no equal to value from .env file it will raise and return client-side error

## Authors

- [@Serhii Buryk](https://www.github.com/Serejka21)

If you have a suggestion or notice an error, please let me know:
Gmail: serhii.buryk02@gmail.com
Telegram: @sergeevich21

