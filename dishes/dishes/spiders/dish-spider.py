from os.path import abspath, join, dirname
import json
import scrapy

filename = join(dirname(abspath(__file__)), '../../data', 'restaurants.json')
data = []

name_selector = '.item-holder .course .course__title .course__name::text'
price_selector = '.item-holder .course .course__footer .course__price-value::text'
href_selector = '.card__title-link::attr(href)'

class DishSpider(scrapy.Spider):
    name = 'dishes'
    start_urls = ['https://eda.ua/restorany']

    def parse(self, response):
        hrefs = response.css(href_selector).extract()
        hrefs_list = ['https://eda.ua' + href for href in hrefs]
        for href in hrefs_list:
            parse_next = self.parse_restaurant(href)
            yield response.follow(href, parse_next)

    def parse_restaurant(self, href):
        def next(response):
            menu = []
            restaurant_name = response.css('.title-link::text').extract_first()
            names = response.css(name_selector).extract()
            prices = response.css(price_selector).extract()

            for i, name in enumerate(names):
                price = prices[i]
                menu.append({ 'name': name, 'price': price })

            data.append({
                'name': restaurant_name,
                'href': href,
                'menu': menu
            })
        return next

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DishSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def spider_closed(self):
        fp = open(filename, 'w')
        json.dump(data, fp, ensure_ascii = False, indent = 2)

print()