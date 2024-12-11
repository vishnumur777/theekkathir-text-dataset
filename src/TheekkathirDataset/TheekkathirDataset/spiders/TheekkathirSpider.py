import scrapy
from datetime import datetime, timedelta
from tamil_date_converter.tamil_date_converter import tamildate_to_date_converter

class TheekkathirspiderSpider(scrapy.Spider):

    name = "TheekkathirSpider"
    allowed_domains = ["theekkathir.in"]
    start_urls_with_metadata = {"https://theekkathir.in/News/articles/":{"category":"articles"},
        "https://theekkathir.in/News/headlines/":{"category":"headlines"},
        "https://theekkathir.in/News/games/":{"category":"games"},
        "https://theekkathir.in/News/politics/":{"category":"politics"},
        "https://theekkathir.in/News/india/":{"category":"india"},
        "https://theekkathir.in/News/world/":{"category":"world"},
        "https://theekkathir.in/News/economics/":{"category":"economics"}}

    def __init__(self):
        self.categories = {
            "world":"உலகம்",
            "india": "தேசியம்",
            "articles": "கட்டுரை",
            "headlines": "தலையங்கம்",
            "politics":"அரசியல்",
            "games": "விளையாட்டு",
            "economics": "பொருளாதாரம்",
            "state": "மாநிலம் - "
        }

    def date_checker(self,tamildate:str):
        convert_date = tamildate_to_date_converter(tamildate)
        current_date = datetime.now()
        yesterday_date = current_date - timedelta(days=1)
        if convert_date == yesterday_date:
            return True
        return False

    def start_requests(self):
        for url,metadata in self.start_urls_with_metadata.items():
            yield scrapy.Request(url=url,callback=self.parse,meta=metadata)

    def parse(self, response):

        titles_scrape = response.css("div.ArticleList h1.zm-post-title")
        dates_scrape = response.css("div.ArticleList a.zm-date")
        author_scrape = response.css("div.ArticleList a.zm-author")

        for titles,dates,authors in zip(titles_scrape,dates_scrape,author_scrape):
            dt_now = datetime.now()
            yesterday = dt_now - timedelta(days=1)
            yesterday = yesterday.replace(hour=0,minute=0,second=0,microsecond=0)
            date = dates.css("::text").get()
            author = authors.css("::text").get()
            dt_convert = tamildate_to_date_converter(date)
            print(yesterday,dt_convert)
            if dt_convert == yesterday:
                title = titles.css("a::text").get().strip()
                url = titles.css("a::attr(href)").get()


                result_data = {
                            "வெளியிட்ட தேதி":date,
                            "தலைப்பு":title,
                            "செய்தி-வகை":self.categories[response.meta.get("category")],
                            "எழுத்தாளர்": author,
                            "இணைப்பு":url,
                            "மொழி":"தமிழ்",
                            "குறிமுறைத் தரநிலை":"UTF-8",
                            "சேகரிக்கப்பட்ட தேதி": str(dt_now)
                        }

                print(result_data)
                yield result_data
            elif dt_convert < yesterday:
                break
