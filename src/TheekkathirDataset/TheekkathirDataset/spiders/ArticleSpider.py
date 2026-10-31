import os
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
        self.dataset = self._load_dataset()
        self.urls = self.dataset["இணைப்பு"].tolist() if not self.dataset.empty else []
        if not self.urls:
            self.logger.warning(
                "No article links found in TheekkathirDataset/extracted.json, "
                "nothing to crawl."
            )

    @staticmethod
    def _load_dataset() -> pd.DataFrame:
        """Load the feed produced by TheekkathirSpider, tolerating an empty feed."""
        feed_path = "./TheekkathirDataset/extracted.json"
        if not os.path.exists(feed_path) or os.path.getsize(feed_path) == 0:
            return pd.DataFrame()

        try:
            others = pd.read_json(feed_path)
        except ValueError:
            # pandas raises ValueError for an empty/invalid JSON feed.
            return pd.DataFrame()

        if others.empty or "இணைப்பு" not in others.columns:
            return pd.DataFrame()

        return others.drop_duplicates(subset="இணைப்பு").reset_index(drop=True)

    async def start(self):
        for index, url in enumerate(self.urls):
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=self.handle_error,
                meta={"index": index},
                dont_filter=True,
            )

    def handle_error(self, failure):
        response = getattr(failure.value, "response", None)
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
