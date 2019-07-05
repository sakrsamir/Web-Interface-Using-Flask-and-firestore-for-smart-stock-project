
import requests
from datetime import date


API_KEY = 'YOUR_API_KEY'
r = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey=' + API_KEY)
if (r.status_code == 200):
  #print r.json()
  today = date.today()
  print (today)
  result = r.json()
  dataForAllDays = result['Time Series (Daily)']
  dataForSingleDate = dataForAllDays['2019-05-17']
  print (dataForSingleDate['1. open'])
  print (dataForSingleDate['2. high'])
  print (dataForSingleDate['3. low'])
  print (dataForSingleDate['4. close'])
  print (dataForSingleDate['5. volume'])