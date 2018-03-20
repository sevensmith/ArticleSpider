# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import json
import codecs
from scrapy.exporters import JsonItemExporter
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):

    def process_item(self, item, spider):
        return item


class JsonExporterPipeline(JsonItemExporter):
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


# insert mysql demo
class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('localhost', 'root', '', 'article_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """insert into jobbole_article(title, url, create_date, fav_nums)
                        VALUES (%s, %s, %s, %s)
                      """
        self.cursor.execute(insert_sql, (item['title'], item['url'], item['create_date'], item['fav_nums']))
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.close()


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(host=settings['MYSQL_HOST'],
                       db=settings['MYSQL_DBNAME'],
                       user=settings['MYSQL_USER'],
                       passwd=settings['MYSQL_PASSWORD'],
                       charset='utf8',
                       cursorclass=MySQLdb.cursors.DictCursor,
                       use_unicode=True)

        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql = """insert into jobbole_article(title, url, url_object_id, create_date, front_img_url, front_img_path, comment_nums, praise_nums, tag, content, fav_nums)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                              """
        cursor.execute(insert_sql, (item['title'], item['url'], item['url_object_id'], item['create_date'], item['front_img_url'], item['front_img_path'], item['comment_nums'], item['praise_nums'], item['tag'], item['content'], item['fav_nums']))


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item

    def close_spider(self, spider):
        self.file.close()


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value['path']
        item['front_img_path'] = image_file_path
        return item
