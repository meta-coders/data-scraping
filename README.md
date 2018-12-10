# data-scraping

Установить scrapy:
```shell
pip install Scrapy
```
Запустить скрипт: 
```shell
scrapy crawl dishes
```
Результат(CSV-файл) сохраняется в дирректорию `data` под названием `restaurants.csv`  

#### PostgreSQL integration

Установить psycopg2:
```shell
pip install psycopg2
```

Создать базу данных `dishes` в PostgreSQL:
```shell
postgres#: CREATE DATABASE dishes;
```

Запустить скрипт: 
```
python3 dishes/data/load-to-pgsql.py
```

###### Note:

Конфигурация PostgreSQL:
* host - `localhost`
* user - `postgres`
* password - `postgres`
