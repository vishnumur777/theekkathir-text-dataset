---
license: cc-by-nc-4.0
dataset_info:
  features:
    - name: தேதி
      dtype: string
    - name: தலைப்பு
      dtype: string
    - name: செய்தி-வகை
      dtype: string
    - name: எழுத்தாளர்
      dtype: string
    - name: இணைப்பு
      dtype: string
    - name: மொழி
      dtype: string
    - name: குறிமுறை தரநிலை
      dtype: string
    - name: உள்ளடக்கம்
      dtype: string
    - name: சேகரிக்கப்பட்ட தேதி
      dtype: string
configs:
  - config_name: sample parquets
    data_files: TheekkathirDataset/parquets/டிசம்பர்*
    
language:
- ta
task_categories:
- text-generation
size_categories:
- 100K<n<1M
---

<h1 align="center"><b>theekkathir-text-dataset <-> தீக்கதிர் தரவுத்தொகுப்பு</b></h1>
<p align="center">
  <img src="https://github.com/user-attachments/assets/3731edf1-70b9-4e0a-98c1-6b89c4e03395" />
</p>

---

<a href="https://github.com/vishnumur777/theekkathir-text-dataset/tree/main">
<p align="center">
  <img src="https://cdn-uploads.huggingface.co/production/uploads/64d848ce620c17bfa092e051/4ySVV0-jiAT_P3iIde0ei.png" alt="hugging face group" width="500px" height="700px"/>
</p>
</a>

<h2 align="center">Click above button to view GitHub Repository</h2>

<h3>இலக்கு:</h3>

இந்த திட்டத்தின் இலக்கு தீக்கதிர் இதழின் செய்தி கட்டுரைகளை தரவுத்தொகுப்பாக மாற்றுவதாகும், இது இயற்கை மொழி பதிவு (NLP) மற்றும் LLM ஆராய்ச்சி நோக்கங்களுக்கு பயன்படுத்தப்படலாம்.

<h3>Goal:</h3> 

The goal of the project is to convert news articles from theekkathir magazine into dataset, which can be used for Natural Language Processing (NLP) and LLM research purposes


# Columns in .parquet

  - வெளியிட்ட தேதி (Released Date)
  - தலைப்பு (Title)
  - செய்தி வகை (Categories)
  - எழுத்தாளர் (Author)
  - மொழி (Language)
  - குறிமுறைத் தரநிலை (Character Encoding)
  - உள்ளடக்கம் (Content)
  - சேகரிக்கப்பட்ட தேதி (Scraped Date)

### You can also get [texts](https://huggingface.co/datasets/aiwithvarun7/theekkathir-text-dataset/tree/main/TheekkathirDataset/texts) apart from parquet files.

# How to Contribute

If you want to contribute to this project, Contact me via [LinkedIn](https://linkedin.com/in/varun-muralidhar)

- If possible, write CONTRIBUTING.md and make Pull Request here.
- Able to Read and Write Tamil.
- Follow [Medium](https://medium.com/@VARUNMURALIDHAR), For detailed documentation and I will update on any contribution.
- Raise issues and PR, if possible.

# எவ்வாறு பங்களிக்கலாம்

இந்த திட்டத்திற்கு பங்களிக்க விரும்பினால், [LinkedIn](https://linkedin.com/in/varun-muralidhar) மூலம் என்னை தொடர்பு கொள்ளவும்.

- தமிழ் மொழியை படிக்க, எழுத தெரிய வேண்டும்.
- சாத்தியமானால், CONTRIBUTING.md எழுதி இங்கு Pull Request செய்யவும்.
- விரிவான ஆவணங்களுக்காக [Medium](https://medium.com/@VARUNMURALIDHAR) பின்தொடரவும். நான் எந்தவொரு பங்களிப்பையும் புதுப்பிக்கிறேன்.
- சாத்தியமானால், பிரச்சினைகளையும் PR (Pull Request) யையும் உயர்த்தவும்.
