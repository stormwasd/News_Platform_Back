"""
@Description :
@File        : grasp_hntynews
@Project     : Scrapy_TiYu
@Time        : 2022/4/11 17:28
@Author      : LiHouJian
@Software    : PyCharm
@issue       :
@change      :
@reason      :
"""


import scrapy
from scrapy.utils import request
from Scrapy_TiYu.items import ScrapyTiyuItem
from datetime import datetime


class GraspFinanceJrjSpider(scrapy.Spider):
    name = 'grasp_hntynews'
    allowed_domains = ['www.hntynews.com']
    start_urls = ['http://www.hntynews.com/list-16-1.html']
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def parse(self, response):
        url_list = response.xpath(
            "//div[@class='neiron_liebiao']/ul/li/a/@href").extract()
        titles = response.xpath(
            "//div[@class='neiron_liebiao']/ul/li/a/text()").extract()
        pub_time_list = response.xpath(
            "//div[@class='neiron_liebiao']/ul/li/span/text()").extract()
        for i in range(len(url_list)):
            url = url_list[i]
            req = scrapy.Request(
                url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            title = titles[i]
            pub_time = pub_time_list[i]
            req.meta.update({"news_id": news_id})
            req.meta.update({"title": title})
            req.meta.update({"pub_time": pub_time.split(' ')[0]})
            yield req
        next_url = response.xpath(
            "//div[@class='neiron_liebiao']/ul/a[@class='a1'][3]/@href").extract_first()
        if next_url:
            yield scrapy.Request(url='http://www.hntynews.com/' + next_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.meta['title']
        pub_time = response.meta['pub_time']
        source = response.xpath(
            "//div[@class='neiron_hh']/li[2]/text()").extract_first().strip('来源：')
        content = ''.join(response.xpath(
            "//div[@class='neiron_theme']").extract())

        item = ScrapyTiyuItem()
        item['news_id'] = news_id
        item['category'] = '体育'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '河南体育新闻网'
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
    cmd.execute(['scrapy', 'crawl', 'grasp_hntynews'])
