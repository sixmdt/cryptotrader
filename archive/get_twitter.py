import csv
# tweepy - Twitter API
import tweepy
import numpy as np
# Обработка "настроения" твита (sentiment analysis)
from textblob import TextBlob
import datetime
import time
import re

def main():

    # Различные логины для вытягивания данных
    consumer_key= 'MOe623rxcqck6x8y5XhzK8MJT'
    consumer_secret= 'mcBq9Km1f3OYERRD6vKmOfWSgCjsqzXAreIsn8klxAtPIo40E7'
    access_token='913787859630460928-RXF8NVN3gGbxD64NCZ7wBma5M2WPwlv'
    access_token_secret='P4UU9I2DimdnUown2EM6p4WZ0ftdPNsysDNW6xGh0Ts4f'

    # Путь csv-файла, если нет - создается
    path = 'live_tweet.csv'
    f = open(path,"a")
    # Здесь будут хранятся твиты
    f1 = open('tweet_data','a')
    # Подключаемся к twitter API, используя методы ниже
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    twitter_api = tweepy.API(auth)
    # Счетчик для показа работы
    i = 0
    while True:
        print(i)
        # Берем твиты используя keywords (кол-во: последние 100)
        tweets = twitter_api.search(q=['bitcoin, price, crypto'], count=100)

        # Получаем полярность
        # Честно говоря - сам не понял, что это
        polarity = get_polarity(tweets,f1)
        sentiment = np.mean(polarity)

        # Сохраняем данные
        f.write(str(sentiment))
        f.write(","+datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
        f.write("\n")
        f.flush()

        i += 1
    
# Убирает emojis
def strip_emoji(text):
    RE_EMOJI = re.compile('[\U00001000-\U0010ffff]', flags=re.UNICODE)
    return RE_EMOJI.sub(r'', text)

# Полярность
def get_polarity(tweets,f):
    tweet_polarity = []
    for tweet in tweets:
        # Избавление от emojis
        text = strip_emoji(tweet.text)
        # Сохраняем твит
        f.write(text+'\n')
        # Обрабатываем твит
        analysis = TextBlob(text)
        # Получаем полярность
        tweet_polarity.append(analysis.sentiment.polarity)

    return tweet_polarity

main()