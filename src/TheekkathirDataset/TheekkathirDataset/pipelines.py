# Define your item pipelines here

# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import os
import pandas as pd

class ArticleSpiderPipeline:
    def __init__(self):
        self.content_list = []
        self.text_list = []
        self.index_list = []
        self.parquet_output_dir = "/home/hdd/pythonPract/TheekkathirDataset/parquets/"
        self.txt_output_dir = "/home/hdd/pythonPract/TheekkathirDataset/texts/"
        os.makedirs(self.parquet_output_dir,exist_ok=True)
        os.makedirs(self.txt_output_dir,exist_ok=True)

    def process_item(self, item, spider):
        if spider.name == "ArticleSpider":
            self.index_list.append(item["index"])
            self.text_list.append(item["full-text"])
            self.content_list.append(item["content"])
        return item

    def close_spider(self,spider):
        df = pd.read_json("./TheekkathirDataset/extracted.json")
        df = df.drop_duplicates(subset="இணைப்பு").reset_index(drop=True)

        for index in self.index_list:
            df.loc[index,"உள்ளடக்கம்"] = self.content_list[index]

        # saving parquet files

        parquet_file_name = os.path.join(self.parquet_output_dir,f"{df["தேதி"][0]}.parquet")
        df.to_parquet(parquet_file_name,compression="gzip",engine="pyarrow",index=False)
        print(f"{df["தேதி"][0]}.parquet is saved under {self.parquet_output_dir}")

        # saving text files with dates as folders and titles as file name

        text_file_directory = os.path.join(self.txt_output_dir,str(df["தேதி"][0]))
        os.makedirs(text_file_directory,exist_ok=True)
        os.chdir(text_file_directory)

        for index in self.index_list:
            text_filename = f"{df["தலைப்பு"][index]}.txt"

            file = open(text_filename,"w")
            file.write(self.text_list[index])
            print(f"{df["தலைப்பு"][index]}.txt is saved under {text_file_directory}")
