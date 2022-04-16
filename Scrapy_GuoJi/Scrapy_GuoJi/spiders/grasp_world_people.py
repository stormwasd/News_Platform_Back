"""
@Description :
@File        : grasp_world_people
@Project     : Scrapy_GuoJi
@Time        : 2022/4/12 16:07
@Author      : LiHouJian
@Software    : PyCharm
@issue       :
@change      :
@reason      :
"""

import scrapy
from scrapy.utils import request
from Scrapy_GuoJi.items import ScrapyGuojiItem
from datetime import datetime


class GraspWorldPeopleSpider(scrapy.Spider):
    name = 'grasp_world_people'
    allowed_domains = ['world.people.com.cn']
    # start_urls = ['https://finance.jrj.com.cn/list/industrynews-1.shtml/']
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def start_requests(self):
        for i in range(1, 2):
            url = f'http://world.people.com.cn/GB/14549/index{i}.html'
            req = scrapy.Request(url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        url_list = response.xpath(
            "//ul[@class='list_ej2  mt20']/li/a/@href").extract()
        titles = response.xpath(
            "//ul[@class='list_ej2  mt20']/li/a/text()").extract()
        pub_time_list = response.xpath(
            "//ul[@class='list_ej2  mt20']/li/i/text()").extract()
        for i in range(len(url_list)):
            url = 'http://world.people.com.cn' + url_list[i]
            req = scrapy.Request(
                url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            title = titles[i]
            pub_time = pub_time_list[i]
            req.meta.update({"news_id": news_id})
            req.meta.update({"title": title})
            req.meta.update({"pub_time": pub_time.lstrip('[ ').rstrip(' ]')})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.meta['title']
        pub_time = response.meta['pub_time']
        source = response.xpath(
            "//div[@class='col-1-1 fl']/a/text()").extract_first()
        content = ''.join(response.xpath(
            "//div[@class='rm_txt_con cf']").extract())

        item = ScrapyGuojiItem()
        item['news_id'] = news_id
        item['category'] = '国际'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '人民网'
        item['content'] = content
        item['source'] = source
        item['author'] = None
        item['images'] = None
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_world_people'])
