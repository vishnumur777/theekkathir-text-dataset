#!/bin/bash

scrapy crawl TheekkathirSpider -o TheekkathirDataset/extracted.json

scrapy crawl StateArticleSpider -o TheekkathirDataset/states.json

scrapy crawl ArticleSpider