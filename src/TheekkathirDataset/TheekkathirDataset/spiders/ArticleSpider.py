import re
import html
import scrapy
import sys
import pandas as pd


class ArticlespiderSpider(scrapy.Spider):
    name = "ArticleSpider"
    allowed_domains = ["theekkathir.in"]
    custom_pipeline = True

    def __init__(self):
        self.others = pd.read_json("./TheekkathirDataset/extracted.json")
        self.dataset = self.others.drop_duplicates(subset="இணைப்பு").reset_index(drop=True)
        self.urls = list(self.dataset["இணைப்பு"])

    def get_index_from_url(self, urls: list, target: str) -> int:
        for index in range(0, len(urls)):
            if urls[index] == target:
                return index
        return 0

    def start_requests(self):
        for url in self.urls:
            index = self.get_index_from_url(self.urls, url)
            yield scrapy.Request(url=url, callback=self.parse, meta={"index": index}, dont_filter=True)

    def handle_error(self, failure):
        response = failure.value.response
        if response and response.status == 404:
            self.logger.error(f"Page not found: {response.url}")
            sys.exit(1)
        elif response and response.status == 500:
            self.logger.error(f"Internal server error at: {response.url}")
            sys.exit(1)
        else:
            self.logger.error(f"Request failed: {failure}")

    def _remove_html_tags(self, text: str) -> str:
        if not text:
            return text
        # Strip any remaining HTML tags
        cleaned = re.sub(r"<[^>]+>", " ", text)
        # Unescape HTML entities like &amp; &nbsp; etc.
        cleaned = html.unescape(cleaned)
        # Collapse repeated whitespace left behind by tag removal
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)
        return cleaned.strip()

    def _extract_article_text(self, response):
        containers = response.css("div.full-article-body, article, .article-content, .entry-content, .post-content")
        if not containers:
            containers = response

        text_parts = []
        for container in containers:
            for node in container.css("p, div, span, li"):
                content = " ".join(node.xpath(".//text()").getall()).strip()
                if content:
                    text_parts.append(content)

        if text_parts:
            return "\n\n".join(text_parts)

        return "\n\n".join(
            " ".join(paragraph.xpath(".//text()").getall()).strip()
            for paragraph in response.css("p")
            if " ".join(paragraph.xpath(".//text()").getall()).strip()
        )

    def parse(self, response):
        full_text = ""
        original_content = ""
        index = response.meta.get("index")

        full_text += f"தலைப்பு: {self.dataset.at[index, 'தலைப்பு']}\n"
        full_text += f"தேதி: {self.dataset.at[index, 'வெளியிட்ட தேதி']}\n"
        full_text += f"செய்தி வகை: {self.dataset.at[index, 'செய்தி-வகை']}\n"
        full_text += f"எழுத்தாளர்: {self.dataset.at[index, 'எழுத்தாளர்']}\n"
        full_text += f"இணைப்பு: {self.dataset.at[index, 'இணைப்பு']}\n\n"

        article_text = self._extract_article_text(response)
        if article_text:
            original_content = article_text
            full_text += article_text

        full_text = self._remove_html_tags(full_text)
        original_content = self._remove_html_tags(original_content)

        print(full_text)
        yield {
            "index": index,
            "title": self.dataset.at[index, "தலைப்பு"],
            "full-text": full_text,
            "content": original_content,
        }