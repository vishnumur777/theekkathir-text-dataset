import scrapy
import pandas as pd


class ArticlespiderSpider(scrapy.Spider):
    name = "ArticleSpider"
    allowed_domains = ["theekkathir.in"]
    custom_pipeline = True

    def __init__(self):
        self.others = pd.read_json("./TheekkathirDataset/extracted.json")
        self.states = pd.read_json("./TheekkathirDataset/states.json")

        self.data = pd.concat([self.others, self.states])
        
        self.dataset = self.data.drop_duplicates(subset="இணைப்பு").reset_index(drop=True)
        self.urls = list(self.dataset["இணைப்பு"])

    def get_index_from_url(self,urls: list,target: str) -> int:
        for index in range(0,len(urls)):
            if urls[index] == target:
                return index
        return 0

    def start_requests(self):
        for url in self.urls:
            index = self.get_index_from_url(self.urls,url)
            yield scrapy.Request(url=url,callback=self.parse,meta={"index":index},dont_filter=True)

    def parse(self, response):

        data_scrape = response.css("div.zm-post-content p")
        full_text=""
        orginal_content=""
        index = response.meta.get("index")

        full_text += f"தலைப்பு: {self.dataset["தலைப்பு"][index]}\n"
        full_text += f"தேதி: {self.dataset["வெளியிட்ட தேதி"][index]}\n"
        full_text += f"செய்தி வகை: {self.dataset["செய்தி-வகை"][index]}\n"
        full_text += f"எழுத்தாளர்: {self.dataset["எழுத்தாளர்"][index]}\n"
        full_text += f"இணைப்பு: {self.dataset["இணைப்பு"][index]}\n\n"
        
        for data in data_scrape:
            # content = data.css("::text").get().strip()
            content = "\n".join(data.xpath(".//text()").getall()).strip()
            orginal_content += content
            full_text += content
            content += "\n"
            full_text += "\n"


        print(full_text)
        yield {"index":index, "title": self.dataset["தலைப்பு"][index], "full-text":full_text, "content":orginal_content}
