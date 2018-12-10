from os.path import abspath, join, dirname
import scrapy
import logging

filename = join(dirname(abspath(__file__)), '../../data', 'restaurants.csv')
data = []

next_page_xpath = ".//div[@class='pager']/ul/li[@class='next']/a/@href"
pizza_xpath = "//div/p[re:test(text(), '(Пицца|Кальцоне)')]/following-sibling::ul"
soup_xpath = "//div/p[re:test(text(), '(Первые блюда|Борщи|Супы)')]/following-sibling::ul"
salad_xpath = "//div/p[re:test(text(), '(Салаты)')]/following-sibling::ul"
pasta_xpath = "//div/p[re:test(text(), '(Паста|Лапша|Равиоли)')]/following-sibling::ul"
burger_xpath = "//div/p[re:test(text(), '(Бургеры)')]/following-sibling::ul"
sushi_xpath = "//div/p[re:test(text(), '(Суши|Роллы|Сеты)')]/following-sibling::ul"
drink_xpath = "//div/p[re:test(text(), '(Напитки|Пиво|Вино)')]/following-sibling::ul"

name_selector = '.course__name::text'
price_selector = '.course__price-value::text'
restaurant_selector = '.card__title-link::attr(href)'

def get_dish_type(name):
    if 'пив' in name.lower():
        return 'Пиво'
    if 'вино' in name.lower():
        return 'Вино'
    else:
        return 'Напиток'


def appendData(select, typeDish, restaurant_name, href, restaurant_address):
    names = select.css(name_selector).extract()
    prices = select.css(price_selector).extract()
    for i, name in enumerate(names):
        type_of_dish = typeDish if typeDish != 'Напитки' else get_dish_type(name)
        price = prices[i]
        data.append({
            'name': name,
            'price': price,
            'type': type_of_dish,
            'restaurant': restaurant_name,
            'link': href,
            'address': restaurant_address,
        })

def csvify(data):
    csv = 'Тип,Название,Цена,Ресторан,Ссылка,Адресс\n'
    wrap = lambda x: '"' + x + '"'

    for obj in data:
        csv += wrap(obj['type']) + ',' + \
               wrap(obj['name']) + ',' + \
               wrap(obj['price']) + ',' + \
               wrap(obj['restaurant']) + ',' + \
               wrap(obj['link']) + ',' + \
               wrap(obj['address']) + '\n'

    return csv

class DishSpider(scrapy.Spider):
    name = 'dishes'
    start_urls = ['https://eda.ua/restorany']

    def parse(self, response):
        restaurants = response.css(restaurant_selector).extract()
        restaurants_list = ['https://eda.ua' + href for href in restaurants]
        for href in restaurants_list:
            clean_href = (href.split('?')[0]) if href.find('?') != -1 else href
            parse_next = self.parse_restaurant(clean_href)
            yield response.follow(clean_href, parse_next)

        next_page_url = response.xpath(next_page_xpath).extract_first()
        if next_page_url is not None:
            yield scrapy.Request(next_page_url)

    def parse_address(self, href, restaurant_name, restaurant_href, selections):
        def next(response):
            addresses = response.css('.addresses__item-link::text').extract()
            restaurant_address = '; '.join(addresses) if len(addresses) != 0 else ''

            (pizza_select,
            soup_select,
            salad_select,
            pasta_select,
            burger_select,
            sushi_select,
            drink_select,
            ) = selections

            appendData(pizza_select, 'Пицца', restaurant_name, restaurant_href, restaurant_address)

            appendData(soup_select, 'Суп', restaurant_name, restaurant_href, restaurant_address)

            appendData(salad_select, 'Салат', restaurant_name, restaurant_href, restaurant_address)

            appendData(pasta_select, 'Паста', restaurant_name, restaurant_href, restaurant_address)

            appendData(burger_select, 'Бургер', restaurant_name, restaurant_href, restaurant_address)

            appendData(sushi_select, 'Суши', restaurant_name, restaurant_href, restaurant_address)

            appendData(drink_select, 'Напитки', restaurant_name, restaurant_href, restaurant_address)

        return next

    def parse_restaurant(self, href):
        def next(response):
            restaurant_name = response.css('.title-link::text').extract_first()
            about_href = href+'/about'

            pizza_select = response.xpath(pizza_xpath)

            soup_select = response.xpath(soup_xpath)

            salad_select = response.xpath(salad_xpath)

            pasta_select = response.xpath(pasta_xpath)

            burger_select = response.xpath(burger_xpath)

            sushi_select = response.xpath(sushi_xpath)

            drink_select = response.xpath(drink_xpath)

            selections = (
            pizza_select,
            soup_select,
            salad_select,
            pasta_select,
            burger_select,
            sushi_select,
            drink_select,
            )

            callback = self.parse_address(about_href, restaurant_name, href, selections)
            yield response.follow(about_href, callback)

        return next

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DishSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def spider_closed(self):
        csv = csvify(data)
        fp = open(filename, 'w')
        fp.write(csv)
