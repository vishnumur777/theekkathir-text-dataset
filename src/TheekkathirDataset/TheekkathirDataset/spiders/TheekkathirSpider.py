import scrapy
from datetime import datetime, timedelta
import tamil_date_converter
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
        self.states_category = {
            "andhra-pradesh": "ஆந்திரப் பிரதேசம்",
            "arunachal-pradesh": "அருணாசல பிரதேசம்",
            "assam": "அசாம்",
            "bihar": "பிகார்",
            "chhattisgarh": "சத்தீஸ்கர்",
            "goa": "கோவா",
            "gujarat": "குஜராத்",
            "haryana": "ஹரியானா",
            "himachal-pradesh": "இமாச்சல பிரதேசம்",
            "jammu-and-kashmir": "ஜம்மு மற்றும் காஷ்மீர்",
            "jharkhand": "ஜார்க்கண்ட்",
            "karnataka": "கர்நாடகா",
            "kerala": "கேரளா",
            "madhya-pradesh": "மத்திய பிரதேசம்",
            "maharashtra": "மகாராஷ்டிரா",
            "manipur": "மணிப்பூர்",
            "meghalaya": "மேகாலயா",
            "mizoram": "மிசோரம்",
            "nagaland": "நாகாலாந்து",
            "odisha": "ஒடிசா",
            "punjab": "பஞ்சாப்",
            "rajasthan": "ராஜஸ்தான்",
            "sikkim": "சிக்கிம்",
            "tamil-nadu": "தமிழ்நாடு",
            "telangana": "தெலுங்கானா",
            "tripura": "திரிபுரா",
            "uttar-pradesh": "உத்தரப் பிரதேசம்",
            "uttarakhand": "உத்தராகண்டம்",
            "west-bengal": "மேற்கு வங்காளம்",
            "andaman-and-nicobar-islands": "அந்தமான் நிகோபார் தீவுகள்",
            "chandigarh": "சண்டிகர்",
            "dadra-and-nagar-haveli-and-daman-and-diu": "தாத்ரா மற்றும் நகர் ஹவேலி மற்றும் தாமன் மற்றும் தியு",
            "delhi": "தில்லி",
            "lakshadweep": "லட்சத்வீப்",
            "puducherry": "புதுச்சேரி"
        }

    def get_author(self,title: str) -> str:
        title_list = title.split("-");
        if title_list is not None:
            if len(title_list) >=2:
                return title_list[-1].strip()
            else:
                return ""
        return ""

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

        for titles,dates in zip(titles_scrape,dates_scrape):
            dt_now = datetime.now()
            yesterday = dt_now - timedelta(days=1)
            yesterday = yesterday.replace(hour=0,minute=0,second=0,microsecond=0)
            date = dates.css("::text").get()
            dt_convert = tamildate_to_date_converter(date)
            print(yesterday,dt_convert)
            if dt_convert == yesterday:
                title = titles.css("a::text").get().strip()
                url = titles.css("a::attr(href)").get()
                author = self.get_author(title)

                result_data = {"தேதி":date,
                            "தலைப்பு":title,
                            "கட்டுரையாளர்":author,
                            "செய்தி-வகை":self.categories[response.meta.get("category")],
                            "இணைப்பு":url}

                print(result_data)
                yield result_data
            elif dt_convert < yesterday:
                break
