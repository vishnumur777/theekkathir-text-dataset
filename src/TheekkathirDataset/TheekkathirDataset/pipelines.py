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
        self.title_list = []
        self.parquet_output_dir = "/home/TheekkathirDataset/parquets/"
        self.txt_output_dir = "/home/TheekkathirDataset/texts/"
        os.makedirs(self.parquet_output_dir,exist_ok=True)
        os.makedirs(self.txt_output_dir,exist_ok=True)

    def process_item(self, item, spider):
        if spider.name=="ArticleSpider":
            self.index_list.append(item["index"])
            self.title_list.append(item["title"])
            self.text_list.append(item["full-text"])
            self.content_list.append(item["content"])
        return item

    def close_spider(self,spider):
        if spider.name == "ArticleSpider":
            others = pd.read_json("./TheekkathirDataset/extracted.json")
            states = pd.read_json("./TheekkathirDataset/states.json")

            df = pd.concat([others, states])

            df = df.drop_duplicates(subset="இணைப்பு").reset_index(drop=True)

            for index,content in zip(self.index_list,self.content_list):
                df.loc[index,"உள்ளடக்கம்"] = content

            # saving parquet files

            df = df[["வெளியிட்ட தேதி","தலைப்பு","செய்தி-வகை","எழுத்தாளர்","இணைப்பு","மொழி","குறிமுறைத் தரநிலை","உள்ளடக்கம்","சேகரிக்கப்பட்ட தேதி"]]
            
            parquet_file_name = os.path.join(self.parquet_output_dir,f"{df["வெளியிட்ட தேதி"][0]}.parquet")
            df.to_parquet(parquet_file_name,compression="gzip",engine="pyarrow",index=False)
            print(f"{df["வெளியிட்ட தேதி"][0]}.parquet is saved under {self.parquet_output_dir}")

            # saving text files with dates as folders and titles as file name

            text_file_directory = os.path.join(self.txt_output_dir,str(df["வெளியிட்ட தேதி"][0]))
            os.makedirs(text_file_directory,exist_ok=True)
            os.chdir(text_file_directory)

            inc = 0
            for title in self.title_list:

                title_length = len(title.split(' '))
                if title_length > 6:
                    title = " ".join(title.split(" ")[:5])
                    title += f" - {df["வெளியிட்ட தேதி"][0]}"

                text_filename = f"{title}.txt"

                file = open(text_filename,"w",encoding="utf-8")
                file.write(self.text_list[inc])
                inc += 1
                print(f"{title}.txt is saved under {text_file_directory}")
