import scrapy
import sys
from datetime import datetime, timedelta
from tamil_date_converter.tamil_date_converter import date_to_tamildate_converter

class TheekkathirspiderSpider(scrapy.Spider):

    name = "TheekkathirSpider"
    allowed_domains = ["theekkathir.in"]
    start_urls_with_metadata = {
        "https://theekkathir.in/category/articles":{"category":"articles"},
        "https://theekkathir.in/category/headlines":{"category":"headlines"},
        "https://theekkathir.in/category/games":{"category":"games"},
        "https://theekkathir.in/category/politics":{"category":"politics"},
        "https://theekkathir.in/category/india":{"category":"india"},
        "https://theekkathir.in/category/world":{"category":"world"},
        "https://theekkathir.in/category/economics":{"category":"economics"},
        "https://theekkathir.in/category/science":{"category":"science"},
        "https://theekkathir.in/category/technology":{"category":"technology"},
        "https://theekkathir.in/category/states":{"category":"states"}}

    def __init__(self):
        self.categories = {
            "world":"உலகம்",
            "india": "தேசியம்",
            "articles": "கட்டுரை",
            "headlines": "தலையங்கம்",
            "politics":"அரசியல்",
            "games": "விளையாட்டு",
            "economics": "பொருளாதாரம்",
            "science": "அறிவியல்",
            "technology": "தொழில்நுட்பம்",
            "states": "மாநிலங்கள்",
        }

    def tamildate_convert(self, yesterday_date):
        convert_date = date_to_tamildate_converter(yesterday_date)
        return convert_date

    def start_requests(self):
        for url,metadata in self.start_urls_with_metadata.items():
            yield scrapy.Request(url=url,callback=self.parse,meta=metadata)

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

    def parse(self, response):
        for card in response.css("div.category-news-list a.category-news-card"):
            dt_now = datetime.now()

            title = card.css("div.category-news-copy h2::text").get(default="").strip()
            if not title:
                continue

            meta_text = " ".join(card.css("div.category-news-copy > p::text").getall()).strip()
            if not meta_text:
                self.logger.warning(f"Skipped item without metadata: {title!r}")
                continue

            parts = [part.strip() for part in meta_text.split("•") if part.strip()]
            if len(parts) < 2:
                self.logger.warning(f"Skipped item with unexpected date text: {meta_text!r}")
                continue

            date = parts[0]
            author = parts[1]
            url = response.urljoin(card.css("::attr(href)").get(default=""))

            if date.lower() == "yesterday":
                result_data = {
                    "வெளியிட்ட தேதி": self.tamildate_convert((dt_now - timedelta(days=1)).date()),
                    "தலைப்பு": title,
                    "செய்தி-வகை": self.categories[response.meta.get("category")],
                    "எழுத்தாளர்": author,
                    "இணைப்பு": url,
                    "மொழி": "தமிழ்",
                    "குறிமுறைத் தரநிலை": "UTF-8",
                    "சேகரிக்கப்பட்ட தேதி": str(dt_now),
                }

                # print(result_data)
                yield result_data
            else:
                break
