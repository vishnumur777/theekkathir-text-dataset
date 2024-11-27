import scrapy
import pandas as pd


class ArticlespiderSpider(scrapy.Spider):
    name = "ArticleSpider"
    allowed_domains = ["theekkathir.in"]

    def __init__(self):
        self.data = pd.read_json("./TheekkathirDataset/extracted.json")
        self.dataset = self.data.drop_duplicates(subset="இணைப்பு").reset_index(drop=True)
        self.urls = list(self.dataset["இணைப்பு"])

    def get_index_from_url(self,urls: list,target: str) -> int:
        for index in range(0,len(urls)):
            if urls[index] == target:
                return index
                break
        return 0

    def start_requests(self):
        for url in self.urls:
            index = self.get_index_from_url(self.urls,url)
            yield scrapy.Request(url=url,callback=self.parse,meta={"index":index})

    def parse(self, response):

        data_scrape = response.css("div.zm-post-content p")
        full_text=""
        orginal_content=""
        index = response.meta.get("index")

        full_text += f"தலைப்பு: {self.dataset["தலைப்பு"][index]}\n"
        full_text += f"கட்டுரையாளர்: {self.dataset["கட்டுரையாளர்"][index]}\n"
        full_text += f"தேதி: {self.dataset["தேதி"][index]}\n"
        full_text += f"செய்தி-வகை: {self.dataset["செய்தி-வகை"][index]}\n\n"
        for data in data_scrape:
            content = data.css("::text").get()
            orginal_content += content
            full_text += content
            content += "\n\n"
            full_text += "\n\n"


        print(full_text)
        yield {"index":index, "full-text":full_text, "content":orginal_content}
