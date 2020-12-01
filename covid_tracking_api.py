import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

now = date.today()
iowa = pd.read_csv("https://api.covidtracking.com/v1/status.csv")

last_seven_deaths = iowa[iowa['date']]['death']

