# coding=utf-8
import datetime
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime

__author__ = 'daniel'


class DB:
    def __init__(self):
        super().__init__()
        self._db_host = '[2001:888:10e2:3:216:3eff:fe5a:52f6]'
        self.engine = create_engine(
            'postgresql+psycopg2://nagg:nagg@{host}:5432/naggdb'.format(host=self._db_host),
            echo=True)
        self.metadata = MetaData()

        self.news_items = Table(
            'news_items', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('source_plugin', String),
            Column('url', String),
            Column('text', String),
            Column('publish_date', DateTime),
            Column('retrieval_date', DateTime),
        )

        self.metadata.create_all(self.engine)

    def insert_news_item(self, source_plugin, url, text, publish_date):
        data = {
            'source_plugin': source_plugin,
            'url': url,
            'text': text,
            'publish_date': publish_date,
            'retrieval_date': datetime.datetime.now()
        }
        ins = self.news_items.insert()

        with self.engine.begin() as conn:
            conn.execute(ins, data)
