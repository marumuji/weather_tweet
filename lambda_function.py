import json
import requests
import datetime
from bs4 import BeautifulSoup
import os
from requests_oauthlib import OAuth1Session

TENKI_URL = 'https://tenki.jp/forecast/3/17/4610/14130/'

def generate_weather_string(date, weather_info):
    # 降水確率のデータ取得
    timeTable = []
    rainProbatility = []
    for element in weather_info.find(class_ = 'precip-table').find_all('th'):
      timeTable.append(element.text)
    
    for element in weather_info.find(class_ = 'rain-probability').find_all('td'):
      rainProbatility.append(element.text)
 
    # 天気予報のテキスト
    weather_string = date.strftime('%Y/%m/%d') + 'の天気' + '\n' \
           + weather_info.find(class_ = 'weather-telop').text + '\n' \
           + weather_info.find(class_ = 'high-temp sumarry').text + ':' \
           + weather_info.find(class_ = 'high-temp temp').text + '\n' \
           + weather_info.find(class_ = 'low-temp sumarry').text + ':' \
           + weather_info.find(class_ = 'low-temp temp').text + '\n' \
           + timeTable[1] + ':' + rainProbatility[0] + '\n' \
           + timeTable[2] + ':' + rainProbatility[1] + '\n' \
           + timeTable[3] + ':' + rainProbatility[2] + '\n' \
           + timeTable[4] + ':' + rainProbatility[3] 
    return weather_string

def tweet(string):
# def tweet(string, image):
  CK = os.environ['CK']
  CS = os.environ['CS']
  AT = os.environ['AT']
  AS = os.environ['AS']
  
  URL = 'https://api.twitter.com/1.1/statuses/update.json'
  URL_MEDIA ="https://upload.twitter.com/1.1/media/upload.json"
  session = OAuth1Session(CK, CS, AT, AS)
  
  # files = {'media' : image}
  # req_media = session.post(URL_MEDIA, files=files)

  # if req_media.status_code != 200:
  #   print('upload failed : %s', req_media.text)
  #   exit()

  # media_id = json.loads(req_media.text)['media_id']

  print('string: ', string)
  # params = {'media_ids' : [media_id], 'status': string}
  params = {'status': string}
  result = session.post(URL, params=params)  
  print('result: ', result)


def lambda_handler(event, context):
    response = requests.get(TENKI_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    todayWeather = soup.find(class_='today-weather')
    tomorrowWeather = soup.find(class_='tomorrow-weather')

    today = datetime.date.today() + datetime.timedelta(hours=9);
    tomorrow = today + datetime.timedelta(days=1);

    tweet(generate_weather_string(today, todayWeather))
    tweet(generate_weather_string(tomorrow, tomorrowWeather))
    
    return {
        'statusCode': 200,
    }
