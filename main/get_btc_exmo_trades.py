import urllib, http.client
import time
import json
import hmac, hashlib
import pandas as pd

API_KEY ='K-3038939b9a19156293f232b73e6d2392c9799078'
API_SECRET = 'S-c25c5229f8be56020bcd495c8adac52e02ff0c4a'

CURRENCY_1 = 'BTC'
CURRENCY_2 = 'USD'
CURRENCY_1_MIN_QUANTITY = 0.001

ORDER_LIFE_TIME = 3 # минуты
STOCK_FEE = 0.002 # комиссия == 0.2%
AVG_PRICE_PERIOD = 90 # за какой период брать ср цену(минуты)
CAN_SPEND = 5 # сколько тратить CUR_2 при каждой покупке CUR_1
BLOCK_SPEND = 30  # ограничение CUR_2 на покупку
PROFIT_MARKUP = 0.001 # прибыль в 1%
DEBUG = True # инфа отладки
STOCK_TIME_OFFSET = 0 # если время биржи расходится с нашим

# обращение к api
API_URL = 'api.exmo.me'
API_VERSION = 'v1'
CURRENT_PAIR = CURRENCY_1 + '_' + CURRENCY_2

class ExmoAPI:
    def __init__(self, API_KEY, API_SECRET, API_URL = 'api.exmo.me', API_VERSION = 'v1'):
        self.API_URL = API_URL
        self.API_VERSION = API_VERSION
        self.API_KEY = API_KEY
        self.API_SECRET = bytes(API_SECRET, encoding='utf-8')        
    def sha512(self, data):
        H = hmac.new(key = self.API_SECRET, digestmod = hashlib.sha512)
        H.update(data.encode('utf-8'))
        return H.hexdigest()
    def api_query(self, api_method, params = {}):
        params['nonce'] = int(round(time.time() * 1000))
        params =  urllib.parse.urlencode(params)
        sign = self.sha512(params)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Key": self.API_KEY,
            "Sign": sign
        }   
        conn = http.client.HTTPSConnection(self.API_URL, timeout=60)
        conn.request("POST", "/" + self.API_VERSION + "/" + api_method, params, headers)
        response = conn.getresponse().read()
        conn.close()
        
        try:
            obj = json.loads(response.decode('utf-8'))
            if 'error' in obj and obj['error']:
                print(obj['error'])
                raise sys.exit()
            return obj
        except json.decoder.JSONDecodeError:
            print('Error while parsing response:', response)
            raise sys.exit()

api = ExmoAPI(API_KEY, API_SECRET)

def get_trades(l):
    trades = api.api_query('trades',
        {'pair':str(CURRENCY_1)+'_'+str(CURRENCY_2), 'limit':l}).items()
    trades_ = []
    for i in trades:
        trades_.append(i)
        
    trades = trades_[0][1]
    
    '''
    for i in range(0, len(trades)):
        t_d = time.ctime(trades[i].get('date')).split(' ')[1::]
        trades[i]['date'] = '|'.join(t_d)
    '''
    
    return trades[::-1] # traeds по времени 0 - старое, -1 - последнее новое


#метод объединения основного пакета с новым 
def unite_pacs():
    rotate_array = []
    for i in range(1, len(mid_pac)):
        if main_trades[-1].get('date') < mid_pac[-i].get('date'):
            rotate_array.append(mid_pac[-i]) 

    for a in rotate_array[::-1]:
        main_trades.append(a)

    del rotate_array



#получаем основной пакет 10к записей 
main_trades = get_trades(100000) 

while True:
	time.sleep(120)
	mid_pac = get_trades(50)
	print('Получил новые трейды!')
	if mid_pac.index(main_trades[-1]) < 49:
		unite_pacs()
		print(len(main_trades))
		df = pd.DataFrame(main_trades)
		df.to_csv('trades_data', sep=',')