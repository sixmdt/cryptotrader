import pandas as pd
import time

def create_one_interval(order):
    interval = {}
    interval['total_amount']=float(order['amount'])
    interval['total_quantity']=float(order['quantity'])
    interval['min_buy_price']=None
    interval['min_sell_price']=None
    interval['max_buy_price']=0
    interval['max_sell_price']=0
    interval['total_buy_quantity']=0
    interval['total_sell_quantity']=0
    interval['bought_total_amount']=0
    interval['sell_total_amount']=0
    interval['middle_buy_price'] = 0
    interval['middle_sell_price'] = 0
    interval['middle_price'] = float(order['price'])
    
    if order['type']=='buy':
        interval['max_buy_price']=float(order['price'])
        interval['min_buy_price']=float(order['price'])
        interval['total_buy_quantity']=float(order['quantity'])
        interval['bought_total_amount']=float(order['amount'])
        interval['middle_buy_price'] = float(order['price'])
        
    elif order['type']=='sell':
        interval['max_sell_price']=float(order['price'])
        interval['min_sell_price']=float(order['price'])
        interval['total_sell_quantity']=float(order['quantity'])
        interval['sell_total_amount']=float(order['amount'])
        interval['middle_sell_price'] = float(order['price'])
    return interval
    
def upgrade_one_interval(order, interval):
    #     общее число        
    interval['total_quantity'] += float(order['quantity'])
    interval['total_amount'] += float(order['amount'])
    interval['middle_price'] = interval['total_amount'] / interval['total_quantity']
#     минимальная и максимальная цена покупки
    if (order['type']=='buy'):
        if float(order['price'])>interval['max_buy_price']:
            interval['max_buy_price'] = float(order['price'])
        if interval['min_buy_price'] == None:
            interval['min_buy_price'] = float(order['price'])
        elif (float(order['price'])<interval['min_buy_price']):
            interval['min_buy_price'] = float(order['price'])
#             общ стоимость и объем покупки
        interval['bought_total_amount']+=float(order['amount'])
        interval['total_buy_quantity']+=float(order['quantity'])
        interval['middle_buy_price'] = interval['bought_total_amount']/interval['total_buy_quantity']
#             минимальная и максимальная цена продажи
    elif order['type']=='sell':
        if float(order['price']) > interval['max_sell_price']:
            interval['max_sell_price'] = float(order['price'])
        if interval['min_sell_price'] == None:
            interval['min_sell_price'] = float(order['price'])
        elif float(order['price']) <interval['min_sell_price']:
            interval['min_sell_price'] = float(order['price'])
        interval['sell_total_amount'] += float(order['amount'])
        interval['total_sell_quantity'] += float(order['quantity'])
        interval['middle_sell_price'] = interval['sell_total_amount']/interval['total_sell_quantity']
#     перевес 
    if interval['bought_total_amount']>interval['sell_total_amount']:
        interval['pereves_val'] = interval['bought_total_amount']-interval['sell_total_amount']
#         interval['pereves_ps'] = ((interval['bought_total_amount'] - interval['sell_total_amount'])/ interval['sell_total_amount']) * 100 
        interval['flag'] = 1 #флаг перевеса покупки для классификации
    elif interval['sell_total_amount'] > interval['bought_total_amount']:
        interval['pereves_val'] = interval['sell_total_amount'] - interval['bought_total_amount']
#         interval['pereves_ps'] = ((interval['sell_total_amount'] - interval['bought_total_amount'])/interval['bought_total_amount']) * 100
        interval['flag'] = 0 #флаг перевеса продаж для классификации
    #  немного статистики можнео накидать(тип в % как в выводе функции ниже)
    return interval



while True:

	

	trade_data = pd.read_csv('trades_data', sep=',', header=None)
	trade_data.columns = ['amount', 'date', 'price', 'quantity', 'trade_id', 'type']
	main_trades = trade_data.to_dict('record')

	trade_time = {}

	for order in main_trades[::-1]:
    # если пустой, создаём и назначаем минимальное время
    if trade_time == {}:
        trade_time['%s' % (order['date'])] = create_one_interval(order)
        min_key = order['date']
    #иначе добавляем
    else:
        #ищем минимальный ключ
        for i in trade_time.keys():
            if int(i) < min_key:
                min_key = int(i)
        #если время ордера не входит в промежуток, то создаём новый
        if (min_key - int(order['date'])) > 900:
            trade_time['%s' %(order['date'])] = create_one_interval(order)
        #если нет, то обновляем старый
        else:
            trade_time[str(min_key)] = upgrade_one_interval(order,(trade_time[str(min_key)]))

    df = pd.DataFrame.from_dict(trade_time, orient='index')
    df.to_csv('intervals')

    time.sleep(60*60*12)