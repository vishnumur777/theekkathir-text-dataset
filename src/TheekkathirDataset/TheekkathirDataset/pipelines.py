# Define your item pipelines here

# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import os
import re
import pandas as pd

def clean_text(text):
    if not isinstance(text, str):
        return text

    text = text.replace("\xa0", " ")
    text = text.replace("\\xa0", " ")

    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def safe_filename(name: str) -> str:
    """Make a string usable as a file name on Linux."""
    name = name.replace("/", "-").replace("\\", "-").replace("\x00", "")
    return name.strip().strip(".")


class ArticleSpiderPipeline:
    def __init__(self):
        self.content_list = []
        self.text_list = []
        self.index_list = []
        self.title_list = []
        self.parquet_output_dir = "/home/TheekkathirDataset/parquets/"
        self.txt_output_dir = "/home/TheekkathirDataset/texts/"
        os.makedirs(self.parquet_output_dir,exist_ok=True)
        os.makedirs(self.txt_output_dir,exist_ok=True)

    @classmethod
    def from_crawler(cls, crawler):
        # Scrapy no longer passes the spider to pipeline methods, so keep the
        # crawler around and read crawler.spider when needed.
        pipeline = cls()
        pipeline.crawler = crawler
        return pipeline

    @property
    def spider(self):
        return getattr(self.crawler, "spider", None)

    def process_item(self, item):
        if self.spider is not None and self.spider.name == "ArticleSpider":
            self.index_list.append(item["index"])
            self.title_list.append(item["title"])
            self.text_list.append(item["full-text"])
            self.content_list.append(item["content"])
        return item

    def close_spider(self):
        if self.spider is None or self.spider.name != "ArticleSpider":
            return

        if not self.title_list:
            print("No articles were scraped, skipping parquet/text export.")
            return

        others = pd.read_json("./TheekkathirDataset/extracted.json")
        # states = pd.read_json("./TheekkathirDataset/states.json")


        df = others.drop_duplicates(subset="இணைப்பு").reset_index(drop=True)

        for index,content in zip(self.index_list,self.content_list):
            df.loc[index,"உள்ளடக்கம்"] = content

        # Normalize Unicode non-breaking spaces in text fields

        text_columns = [
            "தலைப்பு",
            "உள்ளடக்கம்",
        ]
        for column in text_columns:
            if column in df.columns:
                df[column] = df[column].apply(clean_text)

        # saving parquet files

        df = df[["வெளியிட்ட தேதி","தலைப்பு","செய்தி-வகை","எழுத்தாளர்","இணைப்பு","மொழி","குறிமுறைத் தரநிலை","உள்ளடக்கம்","சேகரிக்கப்பட்ட தேதி"]]

        released_date = df["வெளியிட்ட தேதி"].iloc[0]
        parquet_file_name = os.path.join(self.parquet_output_dir,f"{released_date}.parquet")
        df.to_parquet(parquet_file_name,compression="gzip",engine="pyarrow",index=False)
        print(f"{released_date}.parquet is saved under {self.parquet_output_dir}")

        # saving text files with dates as folders and titles as file name

        text_file_directory = os.path.join(self.txt_output_dir,str(released_date))
        os.makedirs(text_file_directory,exist_ok=True)

        for title, text in zip(self.title_list, self.text_list):

            title_length = len(title.split(' '))
            if title_length > 6:
                title = " ".join(title.split(" ")[:5])
                title += f" - {released_date}"

            text_filename = os.path.join(text_file_directory, f"{safe_filename(title)}.txt")

            with open(text_filename,"w",encoding="utf-8") as file:
                file.write(text)
            print(f"{text_filename} is saved under {text_file_directory}")
