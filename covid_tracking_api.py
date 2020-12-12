# import pandas as pd
# from datetime import date
# from dateutil.relativedelta import relativedelta
from time import sleep
import speedtest
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
from inky import InkyWHAT


while True:
    # covid stats
    # today = pd.to_datetime('today')
    # iowa = pd.read_csv("https://api.covidtracking.com/v1/states/ia/daily.csv")
    # iowa['date'] = pd.to_datetime(iowa['date'], format="%Y%m%d")
    # iowa['positive_test_rate'] = iowa['positiveIncrease'] / (iowa['positiveIncrease'] + iowa['negative_increase'])
    #
    # last_seven_deaths = iowa[iowa['date'] > (today + relativedelta(days=-7))][['date', 'deathIncrease']]
    #
    # # internet
    st = speedtest.Speedtest()
    download_mbit = st.download() / 1_000_000
    upload_mbit = st.upload() / 1_000_000

    # 7-day rolling average positivity rate

    # inky stuff

    inky_display = InkyWHAT("red")
    inky_display.set_border(inky_display.WHITE)
    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FredokaOne, 36)
    message = f'D: {download_mbit:.1f} | U: {upload_mbit:.1f}'
    w, h = font.getsize(message)
    x = (inky_display.WIDTH / 2) - (w / 2)
    y = (inky_display.HEIGHT / 2) - (h / 2)

    draw.text((x, y), message, inky_display.BLACK, font)
    inky_display.set_image(img)
    inky_display.show()
    sleep(60)
