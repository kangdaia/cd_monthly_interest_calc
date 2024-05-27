import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import os
from utils import get_month_diff
from mongo_handler import MongoHandler

load_dotenv()

def get_holiday(year):
    base_url = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
    format_type = "json"
    params = {
        "ServiceKey": os.getenv("OPEN_DATA_API_KEY"),
        "solYear": year,
        "_type": format_type,
        "numOfRows": 100
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        if response.content:
            res_content = response.json()
            data = res_content.get("response", {}).get("body", {})
            if data.get("totalCount") >= 1:
                items = data.get("items", {}).get("item", [])
                cursor = MongoHandler()
                if len(items) > 0:
                    cursor.insert_item_many(items, db_name="interest_calc", collection_name="kr_holiday")
                    print(data.get("totalCount"), "datas inserted")
                else:
                    print(f"empty_inner_data")
            else:
                print("No items found")
        else:
            print("Empty response content")
    else:
        response.raise_for_status()

def get_rate(page_start, item_code, period_start, period_end, sub_item_code):
    base_url = "https://ecos.bok.or.kr/api/StatisticSearch"
    format_type = "json"
    lang = "kr"
    api_key = os.getenv('ECOS_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set it in the .env file.")
    cursor = MongoHandler()
    start_date = datetime.strptime(period_start.strip(), "%Y%m%d")
    end_date = datetime.strptime(period_end.strip(), "%Y%m%d")
    if end_date < start_date:
        print("Error. Start Date of {0} is greater than End Date of {1}?!".format(start_date, end_date))
        raise Exception("시작 날짜가 올바르지 않습니다.")
    rate_per_date = list()
    for i in range(1, get_month_diff(start_date, end_date)+1):
        next_month_date = start_date + relativedelta(months=i)
        period_end = next_month_date.strftime("%Y%m%d")
        while 5 <= next_month_date.weekday() <= 6 or cursor.find_item_one({"locdate": period_end}, db_name="interest_calc", collection_name="kr_holiday"):
            next_month_date = next_month_date + relativedelta(days=1)
            period_end = next_month_date.strftime("%Y%m%d")
        if next_month_date > datetime.now():
            period_end = datetime.now().strftime("%Y%m%d")
        if period_start == period_end:
            period_end = (next_month_date + relativedelta(days=1)).strftime("%Y%m%d")
        url = f"{base_url}/{api_key}/{format_type}/{lang}/{page_start}/1/{item_code}/D/{period_start}/{period_end}/{sub_item_code}/?/?/?"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            each_period = dict()
            each_period["startdate"] = period_start
            each_period["rate"] = data["StatisticSearch"]["row"][0]["DATA_VALUE"]
            rate_per_date.append(each_period)
        else:
            response.raise_for_status()
        period_start = period_end
    cursor.insert_item_many(rate_per_date, db_name="interest_calc", collection_name="cd_rate")
    return rate_per_date

if __name__ == "__main__":
    page_start = 1
    item_code = "817Y002"
    sub_item_code = "010502000"  # CD 금리
    try:
        get_rate(page_start, item_code, "20210110", "20240526", sub_item_code)
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
    except ValueError as e:
        print(f"JSON decoding failed: {e}")
    except KeyError as e:
        print(f"Key error: {e}")