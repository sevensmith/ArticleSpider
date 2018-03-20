# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobboleArticleItem, ArticleItemLoader
from ArticleSpider.utils import common
import datetime
# from scrapy.loader import ItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):

        # post_urls = response.css('#archive .floated-thumb .post-thumb a::attr(href)').extract_first("")
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')

        # for post_url in post_urls:
        for post_node in post_nodes:
            img_url = post_node.css('img::attr(src)').extract_first("")
            post_url = post_node.css('::attr(href)').extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={'front_img_url': parse.urljoin(response.url, img_url)}, callback=self.parse_detail)

        next_url = response.css('.next.page-numbers ::attr(href)')
        next_url = next_url.extract_first("")
        # print(next_url)
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # item = JobboleArticleItem()
        front_img_url = response.meta.get("front_img_url", "")
        # re_selector = response.xpath('//*[@class="entry-header"]/h1/text()')
        # # re_selector2 = response.xpath('//div[@class="entry-header"]/h1')
        # title = re_selector.extract_first()
        # create_date = response.xpath('//*[@class="entry-meta-hide-on-mobile"]/text()').extract_first().replace('·', '').strip()
        # praise_nums = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract_first("")
        # if praise_nums:
        #     praise_nums = int(praise_nums)
        # else:
        #     praise_nums = 0
        # fav_nums = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract_first("")
        # match_re = re.match('.*(\d+).*', fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        # comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract_first("")
        # match_re = re.match('.*(\d+).*', comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        #
        # content = response.xpath('//div[@class="entry"]').extract_first("")
        #
        # tags_list = response.xpath('//*[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tags_list = [element for element in tags_list if not element.strip().endswith('评论')]
        # tag = ','.join(tags_list)
        #
        # item['title'] = title
        # item['url'] = response.url
        # item['url_object_id'] = common.get_md5(response.url)
        # try:
        #     create_date = datetime.datetime.strptime(create_date, '%Y/%m/%d').date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        #     print(e)
        # item['create_date'] = create_date
        # item['front_img_url'] = [front_img_url]
        # item['praise_nums'] = praise_nums
        # item['fav_nums'] = fav_nums
        # item['comment_nums'] = comment_nums
        # item['tag'] = tag
        # item['content'] = content

        # 通过Itemloader加载Item
        item_loader = ArticleItemLoader(item=JobboleArticleItem(), response=response)
        item_loader.add_css('title', '.entry-header h1::text')
        item_loader.add_css('create_date', 'p.entry-meta-hide-on-mobile::text')
        item_loader.add_value('front_img_url', [front_img_url])
        item_loader.add_css('praise_nums', '.vote-post-up h10::text')
        item_loader.add_css('fav_nums', '.bookmark-btn::text')
        item_loader.add_css('comment_nums', 'a[href="#article-comment"] span::text')
        item_loader.add_css('tag', 'p.entry-meta-hide-on-mobile a::text')
        item_loader.add_css('content', 'div.entry')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', common.get_md5(response.url))
        # item_loader.add_xpath()
        # item_loader.add_value()
        article_item = item_loader.load_item()
        yield article_item
