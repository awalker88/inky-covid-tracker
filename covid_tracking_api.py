import pandas as pd
from urllib.error import HTTPError
from datetime import datetime, timedelta
from time import sleep
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
from inky import InkyWHAT
from bs4 import BeautifulSoup
import requests

us_pop = 330_746_845


def main():
    first_day = pd.to_datetime('2020-1-20')  # first case in US

    iowa_pop = 3_182_025
    print('Pulling infection histories')
    iowa = get_infection_history("https://api.covidtracking.com/v1/states/ia/daily.csv")
    us = get_infection_history("https://api.covidtracking.com/v1/us/daily.csv")
    print('Received infection histories')

    print('Pulling infection histories')
    us_vacc, iowa_vacc = get_number_vaccinations("https://www.nytimes.com/interactive/2020/us/covid-19-vaccine-doses.html")
    us_vacc_per_100 = 100 * us_vacc / us_pop
    iowa_vacc_per_100 = 100 * iowa_vacc / iowa_pop

    print('Received vaccination histories')

    latest_date = iowa['date'][0]

    iowa_death_average = int(iowa['deathRollingSeven'].iloc[0])
    us_death_average = int(us['deathRollingSeven'].iloc[0])
    iowa_positive_average = int(iowa['positiveRollingSeven'].iloc[0])
    us_positive_average = int(us['positiveRollingSeven'].iloc[0])
    total_immune = us['positive'].iloc[0] + us_vacc

    # Set Inky Display stuff
    print('Initializing inky display')
    display = InkyWHAT(colour='red')
    img = Image.new("P", (display.WIDTH, display.HEIGHT))
    draw = ImageDraw.Draw(img)
    lrg_font, med_font, sml_font = ImageFont.truetype(FredokaOne, 26), ImageFont.truetype(FredokaOne, 22), ImageFont.truetype(FredokaOne, 16)
    left_pad = 3
    middle = display.WIDTH / 2
    header_y = 45
    y_cursor = header_y + 3
    max_line_length = 190
    extra_y_spacer = 3

    # header and section lines
    draw.text((left_pad, 5), f" {latest_date.strftime('%b %d')}           Day {(latest_date - first_day).days:,d}"
                             f" of COVID", display.BLACK, lrg_font)
    draw.line((left_pad, header_y, display.WIDTH - left_pad, header_y),
              fill=display.BLACK, width=3)
    draw.line((left_pad, header_y + (InkyWHAT.HEIGHT - header_y) / 3,
               display.WIDTH - left_pad, header_y + (InkyWHAT.HEIGHT - header_y) / 3),
              fill=display.BLACK, width=3)
    draw.line((left_pad, header_y + 2 * (InkyWHAT.HEIGHT - header_y) / 3,
               display.WIDTH - left_pad, header_y + 2 * (InkyWHAT.HEIGHT - header_y) / 3),
              fill=display.BLACK, width=3)
    draw.line((middle, header_y, middle, display.HEIGHT),
              fill=display.BLACK, width=3)

    # new deaths
    draw.text((get_centered_x('New Deaths', sml_font), y_cursor), 'New Deaths', display.RED, sml_font)
    y_cursor += sml_font.getsize('New Deaths')[1] + 5
    new_deaths_txt = f"IA: {iowa['deathIncrease'][0]:,d} | US: {us['deathIncrease'][0]:,d}"
    draw.text((get_centered_x(new_deaths_txt, med_font), y_cursor), new_deaths_txt, display.BLACK, med_font)
    y_cursor += med_font.getsize(new_deaths_txt)[1] + extra_y_spacer
    rolling_deaths_txt = f"Avg IA: {iowa_death_average:,d} | US: {us_death_average:,d}"
    rolling_deaths_font = ImageFont.truetype(FredokaOne, max_font_size(rolling_deaths_txt, max_line_length))
    draw.text((get_centered_x(rolling_deaths_txt, rolling_deaths_font), y_cursor),
              rolling_deaths_txt, display.BLACK, rolling_deaths_font)
    y_cursor = header_y + (InkyWHAT.HEIGHT - header_y) / 3 + 3  # reset cursor to beginning of col 1 row 2

    # new infections
    draw.text((get_centered_x('New Infections', sml_font), y_cursor), 'New Infections', display.RED, sml_font)
    y_cursor += sml_font.getsize('New Infections')[1] + 5
    new_positive_txt = f"IA: {iowa['positiveIncrease'][0]:,d} | US: {us['positiveIncrease'][0]:,d}"
    new_positive_font = ImageFont.truetype(FredokaOne, max_font_size(new_positive_txt, max_line_length))
    draw.text((get_centered_x(new_positive_txt, new_positive_font), y_cursor), new_positive_txt, display.BLACK,
              new_positive_font)
    y_cursor += med_font.getsize(new_positive_txt)[1] + extra_y_spacer
    rolling_positive_txt = f"Avg IA: {iowa_positive_average:,d} | US: {us_positive_average:,d}"
    rolling_positive_font = ImageFont.truetype(FredokaOne, max_font_size(rolling_positive_txt, max_line_length))
    draw.text((get_centered_x(rolling_positive_txt, rolling_positive_font), y_cursor), rolling_positive_txt,
              display.BLACK, rolling_positive_font)
    y_cursor = header_y + 2 * (InkyWHAT.HEIGHT - header_y) / 3 + 3  # reset cursor to beginning of col 1 row 2

    # positive test rate
    draw.text((get_centered_x('Positive Test Rate', sml_font), y_cursor), 'Positive Test Rate', display.RED, sml_font)
    y_cursor += sml_font.getsize('Positive Test Rate')[1] + 5

    # positive test rate numbers
    ptr_txt = f"IA: {100 * iowa['positiveTestRate'].iloc[0]:.1f}% | US: {100 * us['positiveTestRate'].iloc[0]:.1f}%"
    ptr_font = ImageFont.truetype(FredokaOne, max_font_size(ptr_txt, max_line_length))
    draw.text((get_centered_x(ptr_txt, ptr_font), y_cursor), ptr_txt, display.BLACK, ptr_font)
    y_cursor += med_font.getsize(ptr_txt)[1] + extra_y_spacer
    rolling_positive_txt = f"LW IA: {100 * iowa['positiveTestRate'].iloc[7]:.1f}% | " \
                           f"US: {100 * us['positiveTestRate'].iloc[7]:.1f}%"
    rolling_positive_font = ImageFont.truetype(FredokaOne, max_font_size(rolling_positive_txt, max_line_length))
    draw.text((get_centered_x(rolling_positive_txt, rolling_positive_font), y_cursor), rolling_positive_txt,
              display.BLACK, rolling_positive_font)

    # % dead
    y_cursor = header_y + 3
    draw.text((get_centered_x('US Percent Dead', sml_font, 'third'), y_cursor), 'US Percent Dead', display.RED, sml_font)
    y_cursor += sml_font.getsize('US Percent Dead')[1] + 10
    death_pct_text = f'{100 * us["death"].iloc[0] / us_pop:.2f}%'
    death_pct_font = ImageFont.truetype(FredokaOne, max_font_size(death_pct_text, max_line_length))
    draw.text((get_centered_x(death_pct_text, death_pct_font, 'third'), y_cursor), death_pct_text, display.BLACK, death_pct_font)
    y_cursor = header_y + (InkyWHAT.HEIGHT - header_y) / 3 + 3  # reset cursor to beginning of col 1 row 3

    # immunity
    draw.text((get_centered_x('US Percent "Immune"', sml_font, 'third'), y_cursor), 'US Percent "Immune"', display.RED, sml_font)
    y_cursor += sml_font.getsize('US Percent "Immune"')[1] + 10
    immune_text = f'{100 * (total_immune - us["death"].iloc[0]) / us_pop:.2f}%'  # have to subtract dead from immune :(
    immune_font = ImageFont.truetype(FredokaOne, max_font_size(immune_text, max_line_length))
    draw.text((get_centered_x(immune_text, immune_font, 'third'), y_cursor), immune_text, display.BLACK, immune_font)
    y_cursor = header_y + 2 * (InkyWHAT.HEIGHT - header_y) / 3 + 3  # reset cursor to beginning of col 1 row 3

    # num vaccinated
    draw.text((get_centered_x('People Vaccinated', sml_font, 'third'), y_cursor), 'People Vaccinated', display.RED, sml_font)
    y_cursor += sml_font.getsize('People Vaccinated')[1] + 3
    total_vacc_txt = f'US: {int(us_vacc):,d}'
    total_vacc_font = ImageFont.truetype(FredokaOne, max_font_size(total_vacc_txt, max_line_length, upper_lim=20))
    draw.text((get_centered_x(total_vacc_txt, total_vacc_font, 'third'), y_cursor), total_vacc_txt, display.BLACK, total_vacc_font)
    y_cursor += sml_font.getsize('Vaccination')[1] + 10

    # vacc per hundred
    vacc_per_hundred_txt = f'IA: {iowa_vacc_per_100:.2f} | US: {us_vacc_per_100:.2f}'
    vacc_per_hundred_font = ImageFont.truetype(FredokaOne, max_font_size(vacc_per_hundred_txt, max_line_length, upper_lim=20))
    draw.text((get_centered_x(vacc_per_hundred_txt, vacc_per_hundred_font, 'third'), y_cursor), vacc_per_hundred_txt,
              display.BLACK, vacc_per_hundred_font)

    # update display
    display.set_image(img)
    print('Updating display')
    display.show()
    print('Display updated')


def get_infection_history(link: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(link)
    except HTTPError:
        raise ConnectionError(f'Error when pulling infection data with {link}')
    df['date'] = pd.to_datetime(df['date'], format="%Y%m%d")
    df['positiveTestRate'] = df['positiveIncrease'] / (df['positiveIncrease'] + df['negativeIncrease'])
    df['deathRollingSeven'] = df.sort_values('date')['deathIncrease'].rolling(7).mean()
    df['positiveRollingSeven'] = df.sort_values('date')['positiveIncrease'].rolling(7).mean()
    df['positiveTestRate'] = df['positiveIncrease'] / (df['positiveIncrease'] + df['negativeIncrease'])
    df['ptrRollingSeven'] = df.sort_values('date')['positiveTestRate'].rolling(7).mean()
    return df


def get_number_vaccinations(link: str, state_name:str = 'Iowa'):
    try:
        page = requests.get(link)
    except HTTPError:
        raise ConnectionError(f'Error when pulling vaccination data with {link}')

    soup = BeautifulSoup(page.content, 'html.parser')
    us_vacc = int(soup.find("td", class_="g-cell g-align-r distributed").text.strip("\n").replace(",", ""))

    states = soup.find_all("tbody", class_="g-row-group g-row-group-hidden")
    selected_state = None
    for state in states:
        if state.attrs['data-name_display'] == 'Iowa':
            selected_state = state

    return us_vacc, selected_state.attrs['data-doses_administered']


def get_centered_x(text, font, first_or_third='first'):
    middle = 400 / 2
    first_quarter = middle / 2
    third_quarter = 3 * first_quarter
    if first_or_third == 'first':
        return first_quarter - (font.getsize(text)[0] / 2)
    else:
        return third_quarter - (font.getsize(text)[0] / 2)


def max_font_size(text, max_length=190, lower_lim: int = 12, upper_lim: int = 36):
    font_size = upper_lim
    font = ImageFont.truetype(FredokaOne, font_size)
    txt_len = font.getsize(text)[0]
    while (txt_len > max_length) and (font_size > lower_lim):
        font_size -= 1
        font = ImageFont.truetype(FredokaOne, font_size)
        txt_len = font.getsize(text)[0]
    return font_size


if __name__ == '__main__':
    while True:
        print('Starting loop')
        main()

        dt = datetime.now() + timedelta(hours=5, minutes=59)  # allow a minute for script to run

        while datetime.now() < dt:
            sleep(1)
