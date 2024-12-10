import scrapy
from tamil_date_converter.tamil_date_converter import tamildate_to_date_converter
from datetime import datetime, timedelta


class StatearticlespiderSpider(scrapy.Spider):
    name = "StateArticleSpider"
    allowed_domains = ["theekkathir.in"]
    url = "https://theekkathir.in/News/GetNewsListByCategory?CategoryName=states&SubCategoryName=&PageNo="

    def __init__(self):

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
        self.page_number = 1

    def start_requests(self):
        url_with_page = f"{self.url}{self.page_number}"
        yield scrapy.Request(url=url_with_page,callback=self.parse)

    def state_validation(self,states):
        if states in self.states_category:
            return self.states_category[states]
        return states

    # def test_cases(self):
    #     yesterday = datetime(2024,12,5,0,0,0)
    #     dt_now = datetime.now()
    #     return yesterday,dt_now

    def parse(self,response):
        titles_scrape = response.css("article.zm-single-post h1.zm-post-title")
        dates_scrape = response.css("article.zm-single-post div.zm-post-meta a.zm-date")
        category_scrape = response.css("article.zm-single-post div.zm-category a.cat-btn")
        author_scrape = response.css("article.zm-single-post div.zm-post-meta a.zm-author")

        dt_convert: datetime
        yesterday: datetime
        for titles,dates,category,authors in zip(titles_scrape,dates_scrape,category_scrape,author_scrape):
            dt_now = datetime.now()
            yesterday = dt_now - timedelta(days=1)
            yesterday = yesterday.replace(hour=0,minute=0,second=0,microsecond=0)
            date = dates.css("::text").get()
            dt_convert = tamildate_to_date_converter(date)
            print(yesterday,dt_convert)
            if dt_convert == yesterday:
                title = titles.css("a::text").get().strip()
                url = titles.css("a::attr(href)").get()
                state = category.css("::text").get()
                author = authors.css("::text").get()

                result_data = {
                            "வெளியிட்ட தேதி":date,
                            "தலைப்பு":title,
                            "செய்தி-வகை":f"மாநிலம் - {self.state_validation(state)}",
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

        if dt_convert is not None and yesterday is not None and dt_convert >= yesterday:
            self.page_number += 1
            next_page_url = f"{self.url}{self.page_number}"
            yield scrapy.Request(url=next_page_url,callback=self.parse)
        else:
            return
