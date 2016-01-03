# coding=utf-8
"""
Example
=======

.. code :: python

   with spark_common.SparkAPP('ipynb spartapp exp') as app:
       nic = NewsItemCollection.objects.get(id=2)
       qs = nic.items.filter(newsitemcollection=nic)[:1000]
       qs.query.add_fields(['text'], True)
       df = app.data_from_from_sql(qs)
       df.show()
       print(df.count())
"""
import logging
import re

import nltk
from nltk.stem.snowball import SnowballStemmer

__author__ = 'Daniël'
_log = logging.getLogger(__name__)

# findspark sets up path so we can import pyspark
import findspark
findspark.init('/home/daniel/spark-1.5.0-bin-hadoop2.6')

# noinspection PyUnresolvedReferences
import pyspark
# noinspection PyUnresolvedReferences
from pyspark import SparkContext, SparkConf, SQLContext


stopwords = {}
for _ in ['danish', 'dutch', 'english', 'finnish', 'french', 'german', 'hungarian',
          'italian', 'norwegian', 'portuguese', 'russian', 'spanish', 'swedish',
          'turkish']:
    stopwords[_] = nltk.corpus.stopwords.words(_)


def get_spark_context(name='default-app-name'):
    master = 'spark://10.0.3.6:7077'
    app_name = name
    conf = SparkConf().setAppName(app_name).setMaster(master)
    sc = SparkContext(conf=conf)
    return sc


class SparkAPP:
    def __init__(self, name='default-app-name'):
        self.master = 'spark://10.0.3.6:7077'
        self.app_name = name
        self.conf = SparkConf().\
            setAppName(self.app_name).\
            setMaster(self.master)
        self.sc = SparkContext(conf=self.conf)

    def __enter__(self):
        self.sc.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        return self.sc.__exit__(*args, **kwargs)

    def __del__(self):
        # ensure stopped
        self.sc.stop()

    def data_from_from_sql(self, query):
        """Make a DataFrame from the passed query.

        ..note ::
               Spark (or postgresql jdbc) freaks out on jsonb and tsvector fields.
               Either cast those to text or only select supported field
               types. With a Django QuerySet: `qs.query.add_fields(['text'], True)`
               `tsvector` fields result in `java.sql.SQLException: Unsupported type 1111`

        :type query str or object with attr query (such as Django ORM QuerySet):
        :param query: Used as sub-select by spark
        """
        if not isinstance(query, str):
            query = str(query.query)

        sql_context = SQLContext(self.sc)
        df = sql_context.read.format('jdbc').options(
            url='jdbc:postgresql://10.0.3.7/naggdb?user=nagg&password=nagg',
            # WARNING sql string formatting! Only pass trusted sql
            # Instead of a table name we may pass a sub select in
            # parenthesis to `dbtable`.
            dbtable='({}) as item'.format(query)
        ).load()

        return df


def guess_lang(text, n=2):
    doc_words = set(nltk.word_tokenize(text))
    scores = {}
    for lang, sw_words in stopwords.items():
        scores[lang] = len(sw_words.intersection(doc_words))
    return [(l, s) for l, s in sorted(scores.items(), key=lambda x: -x[1])][0:n]


def tokenize_and_stem(text):
    text = text.replace("'", " ").replace(',', ' ').replace('.', ' ').replace('twitter.com', '').replace('class=', ''.replace('lockquote', ''))
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stemmer = SnowballStemmer("dutch")
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems


def tokenize_only(text):
    text = text.replace("'", " ").replace(',', ' ').replace('.', ' ').replace('twitter.com', '').replace('class=', ''.replace('lockquote', ''))
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens