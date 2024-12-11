from datetime import datetime

tamil_months = {
    1:"ஜனவரி",
    2:"பிப்ரவரி",
    3:"மார்ச்",
    4:"ஏப்ரல்",
    5:"மே",
    6:"ஜூன்",
    7:"ஜூலை",
    8:"ஆகஸ்ட்",
    9:"செப்டம்பர்",
    10:"அக்டோபர்",
    11:"நவம்பர்",
    12:"டிசம்பர்"
}

def date_to_tamildate_converter(given_date: datetime) -> str:
    month = given_date.month
    date = given_date.day
    year = given_date.year

    result_date = tamil_months[month] + " " + str(date) +", " + str(year)

    return result_date

def tamildate_to_date_converter(given_tamildate: str) -> datetime:
    list_tamil_date = given_tamildate.split(" ")
    list_tamil_date[1] = list_tamil_date[1].replace(",","")

    month = [month_no for month_no,month_name in tamil_months.items() if list_tamil_date[0]==month_name][0]
    date = int(list_tamil_date[1])
    year = int(list_tamil_date[2])

    result_dt = datetime(year,month,date)
    return result_dt

# if __name__ == "__main__":

#     a = datetime.now()
#     tam_str = date_to_tamildate_converter(a)
#     dt = tamildate_to_date_converter(tam_str)
#     print(tam_str)
#     print(dt)
