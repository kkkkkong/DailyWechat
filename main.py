from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import os
import json
from datetime import datetime, timedelta
import requests
from borax.calendars.lunardate import LunarDate

nowtime = datetime.utcnow() + timedelta(hours=8)
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")


def get_time():
    dictDate = {'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三', 'Thursday': '星期四',
                'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期天'}
    a = dictDate[nowtime.strftime('%A')]
    return nowtime.strftime("%Y年%m月%d日") + a


def get_words():
    words = requests.get("https://apis.tianapi.com/zaoan/index?key=a98b3d2eda6c6e8c9dfd1f8cd4dd7295").json()
    print(words)
    if words['code'] != 200:
        return get_words()
    # 获取原始内容
    content = words['result']['content']
    # 在句号、问号、感叹号后添加HTML换行标签
    content = content.replace('。', '。<br>').replace('？', '？<br>').replace('！', '！<br>')
    return content

def get_weather(city, key):
    url = f"https://api.seniverse.com/v3/weather/daily.json?key={key}&location={city}&language=zh-Hans&unit=c&start=-1&days=5"
    res = requests.get(url).json()
    print(res)
    weather = (res['results'][0])["daily"][0]
    city = (res['results'][0])["location"]["name"]
    return city, weather

def get_count(born_date):
    delta = today - datetime.strptime(born_date, "%Y-%m-%d")
    return delta.days


def get_birthday(birthday):
    nextdate = datetime.strptime(str(today.year) + "-" + birthday, "%Y-%m-%d")
    if nextdate < today:
        nextdate = nextdate.replace(year=nextdate.year + 1)
    return (nextdate - today).days

def get_lunar_days(today):
    # 获取当前日期的农历月份和日期
    lunar_date = LunarDate.from_solar_date(today.year, today.month, today.day)
    # 如果当前已经是十五号，返回0
    if lunar_date.day == 15:
        return 0
    
    # 如果当前日期小于十五号，计算到本月十五的天数
    if lunar_date.day < 15:
        # 获取本月十五的日期
        current_fifteen = LunarDate(lunar_date.year, lunar_date.month, 15)
        solar_fifteen = current_fifteen.to_solar_date()
        next_date = datetime(solar_fifteen.year, solar_fifteen.month, solar_fifteen.day)
        days = (next_date - today).days
    # 如果当前日期大于十五号，计算到下月十五的天数
    else:
        # 获取下月十五的日期
        if lunar_date.month == 12:
            next_fifteen = LunarDate(lunar_date.year + 1, 1, 15)
        else:
            next_fifteen = LunarDate(lunar_date.year, lunar_date.month + 1, 15)
        solar_fifteen = next_fifteen.to_solar_date()
        next_date = datetime(solar_fifteen.year, solar_fifteen.month, solar_fifteen.day)
        days = (next_date - today).days
    return days

def get_lunar_layue_seven(today):
    # Convert today's date to LunarDate
    lunar_today = LunarDate.from_solar_date(today.year, today.month, today.day)
    
    # Initialize the next 腊月初七 date
    if lunar_today.month == 12 and lunar_today.day <= 7:
        # If we're in 腊月 but haven't passed 初七 yet
        next_layue_seven = LunarDate(lunar_today.year, 12, 7)
    elif lunar_today.month == 12 and lunar_today.day > 7:
        # If we're in 腊月 but already passed 初七
        next_layue_seven = LunarDate(lunar_today.year + 1, 12, 7)
    elif lunar_today.month < 12:
        # If we haven't reached 腊月 yet this year
        next_layue_seven = LunarDate(lunar_today.year, 12, 7)
    else:
        # For any other case, get next year's 腊月初七
        next_layue_seven = LunarDate(lunar_today.year + 1, 12, 7)
    
    # Convert lunar date to solar date
    solar_date = next_layue_seven.to_solar_date()
    next_date = datetime(solar_date.year, solar_date.month, solar_date.day)
    
    # Calculate days difference
    return (next_date - today).days

def get_lunar_september_nineteen(today):
    # Convert today's date to LunarDate
    lunar_today = LunarDate.from_solar_date(today.year, today.month, today.day)
    
    # Initialize the next 九月十九 date
    if lunar_today.month < 9:
        # If we haven't reached 九月 yet this year
        next_date = LunarDate(lunar_today.year, 9, 19)
    elif lunar_today.month == 9 and lunar_today.day <= 19:
        # If we're in 九月 but haven't passed 十九 yet
        next_date = LunarDate(lunar_today.year, 9, 19)
    else:
        # If we've passed 九月十九, get next year's date
        next_date = LunarDate(lunar_today.year + 1, 9, 19)
    
    # Convert lunar date to solar date
    solar_date = next_date.to_solar_date()
    next_date = datetime(solar_date.year, solar_date.month, solar_date.day)
    
    # Calculate days difference
    return (next_date - today).days

if __name__ == "__main__":
    app_id = os.getenv("APP_ID")
    app_secret = os.getenv("APP_SECRET")
    template_id = os.getenv("TEMPLATE_ID")
    weather_key = os.getenv("WEATHER_API_KEY")
    # 定义恋爱纪念日的起始日期
    love_date = "2024-09-17"
    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)

    f = open("users_info.json", encoding="utf-8")
    js_text = json.load(f)
    f.close()
    data = js_text['data']
    num = 0
    words=get_words()
    out_time=get_time()

    print(words, out_time)

    for user_info in data:
        born_date = user_info['born_date']
        birthday = born_date[5:]
        city = user_info['city']
        user_id = user_info['user_id']
        name = user_info['user_name'].upper()


        wea_city,weather = get_weather(city,weather_key)
        data = dict()
        data['time'] = {'value': out_time}
        data['words'] = {'value': words}
        data['weather'] = {'value': weather['text_day']}
        data['city'] = {'value': wea_city}
        data['tem_high'] = {'value': weather['high']}
        data['tem_low'] = {'value': weather['low']}
        data['born_days'] = {'value': get_count(born_date)}
        data['birthday_left'] = {'value': get_birthday(birthday)}
        data['wind'] = {'value': weather['wind_direction']}
        data['name'] = {'value': name}
        # 计算恋爱纪念日的天数并添加到data中
        data['love_days'] = {'value': get_count(love_date)}
        # 计算未来最近的农历十五距离现在多少天
        data['lunar_days'] = {'value': get_lunar_days(today)}
        # 距离人物1生日还有多少天
        data['layue_days'] = {'value': get_lunar_layue_seven(today)}
        # 距离人物2生日还有多少天
        data['lunar_birthday_person2'] = {'value': get_lunar_september_nineteen(today)}
        print(data)

        res = wm.send_template(user_id, template_id, data)
        print(res)
        num += 1
    print(f"成功发送{num}条信息")
