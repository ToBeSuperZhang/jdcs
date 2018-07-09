# -*- coding: utf-8 -*-
import time
import re
import json
import scrapy
from scrapy import Request
from jdcs.items import JdcsItem


class SupermarketSpider(scrapy.Spider):
    name = 'supermarket'
    allowed_domains = ['chaoshi.jd.com', 'search.jd.com']
    start_urls = ['https://chaoshi.jd.com/']

    def parse(self, response):
        r = response.xpath('//*[@class="mod_container"]/script').extract()[0]
        first_name = re.compile('navFirst:(.*?)\n').findall(r)[0][:-1]
        json_first_name_list = json.loads(first_name)
        next_name_list = re.compile('navThird\d+:(.*?)\n').findall(r)
        json_next_name_list = [json.loads(i[:-1]) for i in next_name_list]
        for first_name, next_name_list in zip(json_first_name_list, json_next_name_list):
            for next_name in next_name_list:
                for last_info in next_name.get('children'):
                    last_name = last_info.get('NAME')
                    from_url = last_info.get('URL')
                    if not from_url.startswith('https'):
                        from_url = 'https:' + from_url
                    if from_url.find('search') != -1:
                        keyword = re.compile('keyword=(.*?)&').findall(from_url)[0]
                        request = Request(from_url, callback=self.parse_goods)
                        request.meta['keyword'] = keyword
                        cates = [first_name.get('NAME'), next_name.get('NAME'), last_name]
                        request.meta['cates'] = cates
                        request.meta['from_url'] = from_url
                        yield request

    def parse_goods(self, response, num=2):
        url_list = response.xpath('//*[@id="J_goodsList"]/ul/li//div[@class="p-img"]/a/@href').extract()
        url_list = ['https:' + url if not url.startswith('https') else url for url in url_list]
        cates = response.meta['cates']
        from_url = response.meta['from_url']
        print(from_url, type(from_url), '========================')
        for url in url_list:
            print(url, type(url), '++++++++++++++++++++')
            jdcs_item = JdcsItem()
            jdcs_item['cates'] = cates
            jdcs_item['from_url'] = from_url
            jdcs_item['url'] = url
            yield jdcs_item
        num = response.meta.get('num', num)
        keyword = response.meta['keyword']
        pid_list = response.xpath('//*[@id="J_goodsList"]/ul/li/@data-sku').extract()
        show_items = ','.join([str(i) for i in pid_list])
        s_init = response.xpath('//body/script').extract_first()
        s = s_init.split(',')[-4]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        links = 'https://search.jd.com/s_new.php?keyword={0}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq={1}&stock=1&page={2}&s={3}&scrolling=y&tpl=3_M&show_items={4}'.format(
            keyword, keyword, str(num), s, show_items)
        request = Request(links, headers=headers, callback=self.parse_next)
        request.meta['cates'] = cates
        request.meta['from_url'] = from_url
        request.meta['keyword'] = keyword
        num += 1
        request.meta['num'] = num
        yield request

    def parse_next(self, response):
        cates = response.meta['cates']
        from_url = response.meta['from_url']
        r = response.xpath('//script[last()]').extract()[0].split(',')
        s = r[-4]
        over = int(r[1])
        num = response.meta['num']
        if over >= num:
            url_list1 = response.xpath('//li[@class="gl-item"]//div[@class="p-img"]/a/@href').extract()
            url_list1 = ['https:' + i if not i.startswith('https') else i for i in url_list1]
            for url in url_list1:
                jdcs_item = JdcsItem()
                jdcs_item['cates'] = cates
                jdcs_item['from_url'] = from_url
                jdcs_item['url'] = url
                yield jdcs_item
            keyword = response.meta['keyword']
            link1 = 'https://search.jd.com/Search?keyword={0}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq={1}&stock=1&page={2}&s={3}&click=0'.format(
                keyword, keyword, str(num), s)
            request = Request(link1, callback=self.parse_goods)
            request.meta['from_url'] = link1
            request.meta['cates'] = cates
            num += 1
            request.meta['num'] = num
            request.meta['keyword'] = keyword
            yield request
