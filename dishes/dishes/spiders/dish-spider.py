from os.path import abspath, join, dirname
import scrapy

filename = join(dirname(abspath(__file__)), '../../data', 'restaurants.csv')
data = []

next_page_xpath = ".//div[@class='pager']/ul/li[@class='next']/a/@href"
pizza_xpath = "//div/p[re:test(text(), '(Пицца|Кальцоне)')]/following-sibling::ul"
soup_xpath = "//div/p[re:test(text(), '(Первые блюда|Борщи|Супы)')]/following-sibling::ul"
salad_xpath = "//div/p[re:test(text(), '(Салаты)')]/following-sibling::ul"
pasta_xpath = "//div/p[re:test(text(), '(Паста|Лапша|Равиоли)')]/following-sibling::ul"
burger_xpath = "//div/p[re:test(text(), '(Бургеры)')]/following-sibling::ul"
sushi_xpath = "//div/p[re:test(text(), '(Суши|Роллы|Сеты)')]/following-sibling::ul"

name_selector = '.course__name::text'
price_selector = '.course__price-value::text'
restaurant_selector = '.card__title-link::attr(href)'

def appendData(select, type, restaurant_name, href):
    names = select.css(name_selector).extract()
    prices = select.css(price_selector).extract()
    for i, name in enumerate(names):
        price = prices[i]
        data.append({
            'name': name,
            'price': price,
            'type': type,
            'restaurant': restaurant_name,
            'link': href,
        })

def csvify(data):
    csv = 'Тип,Название,Цена,Ресторан,Ссылка\n'
    wrap = lambda x: '"' + x + '"'

    for obj in data:
        csv += wrap(obj['type']) + ',' + \
               wrap(obj['name']) + ',' + \
               wrap(obj['price']) + ',' + \
               wrap(obj['restaurant']) + ',' + \
               wrap(obj['link']) + '\n'

    return csv

class DishSpider(scrapy.Spider):
    name = 'dishes'
    start_urls = ['https://eda.ua/restorany']

    def parse(self, response):
        restaurants = response.css(restaurant_selector).extract()
        restaurants_list = ['https://eda.ua' + href for href in restaurants]
        for href in restaurants_list:
            parse_next = self.parse_restaurant(href)
            yield response.follow(href, parse_next)

        next_page_url = response.xpath(next_page_xpath).extract_first()
        if next_page_url is not None:
            yield scrapy.Request(next_page_url)

    def parse_restaurant(self, href):
        def next(response):
            restaurant_name = response.css('.title-link::text').extract_first()

            pizza_select = response.xpath(pizza_xpath)
            appendData(pizza_select, 'Пицца', restaurant_name, href)

            soup_select = response.xpath(soup_xpath)
            appendData(soup_select, 'Суп', restaurant_name, href)

            salad_select = response.xpath(salad_xpath)
            appendData(salad_select, 'Салат', restaurant_name, href)

            pasta_select = response.xpath(pasta_xpath)
            appendData(pasta_select, 'Паста', restaurant_name, href)

            burger_select = response.xpath(burger_xpath)
            appendData(burger_select, 'Бургер', restaurant_name, href)

            sushi_select = response.xpath(sushi_xpath)
            appendData(sushi_select, 'Суши', restaurant_name, href)

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
