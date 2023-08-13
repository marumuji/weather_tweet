import json
import requests
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import os
from requests_oauthlib import OAuth1Session
from io import BytesIO
from PIL import Image
import tweepy

TENKI_URL = os.environ['TENKI_URL']

def downloadImage(url, timeout=10):
    response = requests.get(url, allow_redirects=False, timeout=timeout)
    if response.status_code != 200:
      e = Exception("HTTP status: " + response.status_code)
      print(e)
  
    content_type = response.headers["content-type"]
    if 'image' not in content_type:
      e = Exception("Content-type: " + content_type)
      print(e)
  
    # print(vars(response))
    return response.content

def generate_weather_string(date, weather_info):
    # 更新日時
    JST = timezone(timedelta(hours=+9))
    updatedAt = datetime.now(JST).strftime('%Y/%m/%d %H:%M (JST)')

    # 降水確率のデータ取得
    timeTable = []
    rainProbatility = []
    for element in weather_info.find(class_ = 'precip-table').find_all('th'):
      timeTable.append(element.text)
    
    for element in weather_info.find(class_ = 'rain-probability').find_all('td'):
      rainProbatility.append(element.text)
 
    # 天気予報のテキスト
    weather_string = date.strftime('%Y/%m/%d') + 'の天気' + ' [' + updatedAt + ' 更新]' + '\n' \
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

def tweet(string, image):
  CK = os.environ['CK'] # API Key
  CS = os.environ['CS'] # API Secret
  AT = os.environ['AT'] # Access Token
  AS = os.environ['AS'] # Access Token Secret
  
  auth = tweepy.OAuthHandler(CK, CS)
  auth.set_access_token(AT, AS)
  api = tweepy.API(auth)

  client = tweepy.Client(
    consumer_key = CK,
    consumer_secret = CS,
    access_token = AT,
    access_token_secret = AS
  )

  media = api.media_upload(filename = image)
  client.create_tweet(text = string, media_ids=[media.media_id])

def lambda_handler(event, context):
    response = requests.get(TENKI_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    todayWeather = soup.find(class_='today-weather')
    tomorrowWeather = soup.find(class_='tomorrow-weather')

    todayWeatherImageUrl = todayWeather.find('img').get('src')
    tomorrowWeatherImageUrl = tomorrowWeather.find('img').get('src')

    todayWeatherFilePath = '/tmp/todayWeather.png'
    tomorrowWeatherFilePath = '/tmp/tomorrowWeather.png'

    JST = timezone(timedelta(hours=+9))
    today = datetime.now(JST)
    tomorrow = today + timedelta(days=1)

    todayWeatherImage = Image.open(BytesIO(downloadImage(todayWeatherImageUrl))).resize((94,60))
    todayWeatherImage.save(todayWeatherFilePath, format='PNG')
    tomorrowWeatherImage = Image.open(BytesIO(downloadImage(tomorrowWeatherImageUrl))).resize((94,60))
    tomorrowWeatherImage.save(tomorrowWeatherFilePath, format='PNG')
    
    # tweet only text
    # tweet(generate_weather_string(today, todayWeather))
    # tweet(generate_weather_string(tomorrow, tomorrowWeather))

    # tweet text and image
    tweet(generate_weather_string(today, todayWeather), todayWeatherFilePath)
    tweet(generate_weather_string(tomorrow, tomorrowWeather), tomorrowWeatherFilePath)
    
    return {
        'statusCode': 200,
    }
