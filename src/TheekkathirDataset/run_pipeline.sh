#!/bin/bash

rm -rf TheekkathirDataset/extracted.json TheekkathirDataset/states.json

scrapy crawl TheekkathirSpider -o TheekkathirDataset/extracted.json

scrapy crawl StateArticleSpider -o TheekkathirDataset/states.json

scrapy crawl ArticleSpider

python3 upload_huggingface.py
