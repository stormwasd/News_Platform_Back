"""
@Description :
@File        : grasp_chinanews
@Project     : Scrapy_JunShi
@Time        : 2022/4/12 17:52
@Author      : LiHouJian
@Software    : PyCharm
@issue       :
@change      :
@reason      :
"""

import scrapy
from scrapy.utils import request
from Scrapy_JunShi.items import ScrapyJunshiItem
from Scrapy_JunShi import upload_file
from datetime import datetime


class GraspChinaSpider(scrapy.Spider):
    name = 'grasp_chinanews'
    allowed_domains = ['www.chinanews.com.cn']
    start_urls = ['https://www.chinanews.com.cn/mil/news.shtml']
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def parse(self, response):
        url_list = response.xpath(
            "//ul/li/div[@class='dd_bt']/a/@href").extract()
        titles = response.xpath(
            "//ul/li/div[@class='dd_bt']/a/text()").extract()
        pub_time_list = response.xpath(
            "//ul/li/div[@class='dd_time']/text()").extract()
        for i in range(len(url_list)):
            url = 'https://www.chinanews.com.cn' + url_list[i]
            req = scrapy.Request(
                url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            title = titles[i]
            pub_time = pub_time_list[i]
            req.meta.update({"news_id": news_id})
            req.meta.update({"title": title})
            req.meta.update({"pub_time": '2022-' + pub_time.split()[0]})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.meta['title']
        pub_time = response.meta['pub_time']
        source = response.xpath(
            "//div[@class='left-time']/div[@class='left-t']/text()").extract_first().split('：')[1]
        if len(source) == 0:
            source = None
        content = ''.join(response.xpath("//div[@class='left_zw']").extract())
        content_img = response.xpath(
            "//div[@class='left_zw']//img/@src").extract()
        if content_img:
            content_img_list = list()
            for index, value in enumerate(content_img):
                img_name = title + str(index)
                res = upload_file.send_file(value, img_name, self.headers)
                if res['msg'] == 'success':
                    content = content.replace(value, res['url'][0])
                    content_img_list.append(res['url'][0])
                else:
                    self.logger.info(f'内容图片 {value} 上传失败，返回数据：{res}')

            imgs = ','.join(content_img_list)
        else:
            imgs = None

        item = ScrapyJunshiItem()
        item['news_id'] = news_id
        item['category'] = '军事'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '中国新闻网'
        item['content'] = content
        item['source'] = source
        item['author'] = None
        item['images'] = imgs
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_chinanews'])
