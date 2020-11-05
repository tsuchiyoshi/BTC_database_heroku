# coincheck用送信関数
import hashlib
import hmac
import requests
import datetime
import json
import set_params

class CcApi:
    CURRENCY_PAIR = ''
    API_KEY = ''
    API_SECRET = ''
    API_URL = ''
    nonce = int((datetime.datetime.today()-datetime.datetime(2020,1,1)).total_seconds())*10

    # コンストラクタ
    def __init__(self, key, secret, url):
        self.API_KEY = key
        self.API_SECRET = secret
        self.API_URL = url
        return

    # coincheckのプライベートAPIにリクエストを送信する関数
    def _private_api(self, i_path, i_nonce, i_params=None, i_method='get'):
        headers = {'ACCESS-KEY': self.API_KEY,
                   'ACCESS-NONCE': str(i_nonce),
                   'Content-Type': 'application/json'}
        s = hmac.new(bytearray(self.API_SECRET.encode('utf-8')),digestmod=hashlib.sha256)
        c = None
        if i_params is None:
            w = str(i_nonce) + self.API_URL + i_path
            s.update(w.encode('utf-8'))
            headers['ACCESS-SIGNATURE'] = s.hexdigest()
            if i_method == 'delete':
                c = requests.delete(self.API_URL + i_path, headers=headers)
            else:
                c = requests.get(self.API_URL + i_path, headers=headers)
        else:
            body = json.dumps(i_params);
            print(body)
            w = str(i_nonce) + self.API_URL + i_path + body
            print(w)
            s.update(w.encode('utf-8'))
            print('s:',s)
            headers['ACCESS-SIGNATURE'] = s.hexdigest()
            c = requests.post(self.API_URL + i_path, params=body, headers=headers)
        # 戻り値のチェック
        if c.status_code != 200:
            raise Exception('HTTP ERROR status={0},{1}'.format(c.status_code, c.text))
        j = c.json()
        if j['success'] != True:
            raise Exception('API ERROR json={0}'.format(j))
        return j

    # 売買を行うAPIの共通部分
    def _trade_api(self, price, amount, order_type):
        self.nonce = self.nonce +1
        j = self._private_api('/api/exchange/orders',
                              self.nonce,
                              {'rate': price,
                               'amount': amount,
                               'order_type': order_type,
                               'pair': 'btc_jpy'})
        return j

    def _market_trade_api(self, amount, order_type):
        self.nonce = self.nonce +1
        if order_type == 'market_buy':
            j = self._private_api('/api/exchange/orders',
                                  self.nonce,
                                  {'market_buy_amount': amount,
                                   'order_type': order_type,
                                   'pair': 'btc_jpy'})
        elif order_type == 'market_sell':
            j = self._private_api('/api/exchange/orders',
                                  self.nonce,
                                  {'amount': amount,
                                   'order_type': order_type,
                                   'pair': 'btc_jpy'})
        return j

    # 板情報を得る関数
    def orderbook(self):
        c = requests.get('https://coincheck.com/api/order_books')
        if c.status_code != 200:
            raise Exception("HTTP ERROR status={0},{1}".format(c.status_code, c.text()))
        j = c.json()
        return {'asks':[(float(i[0]),float(i[1])) for i in j['asks']],
                'bids':[(float(i[0]),float(i[1])) for i in j['bids']] }

    # 残高を得る関数
    def balance(self):
        self.nonce = self.nonce +1
        c = self._private_api('/api/accounts/balance',self.nonce)
        return {'btc':float(c['btc']),
                'jpy':float(c['jpy'])}

    # 売り注文を実行する関数
    # 指値注文
    def sell(self, price, amount):
        j = self._trade_api(price, amount, 'sell')
        return j['id']
    # 成行注文
    def market_sell(self, btc_amount):
        j = self._market_trade_api(btc_amount, 'market_sell')
        return j['id']

    # 買い注文を実行する関数
    # 指値注文
    def buy(self, price, amount):
        j = self._trade_api(price, amount, 'buy')
        return j['id']
    # 成行注文
    def market_buy(self, jpy_amount):
        j = self._market_trade_api(jpy_amount, 'market_buy')
        return j['id']


    # 注文をキャンセルする関数
    def cancel(self, oid):
        self.nonce = self.nonce +1
        return self._private_api('/api/exchange/orders/' + str(oid),
                                 self.nonce,
                                 i_method = 'delete')

    # 注文の状態を調べる関数
    def is_active_order(self, oid):
        self.nonce = self.nonce +1
        j = self._private_api('/api/exchange/orders/opens',self.nonce)
        w = [i['id'] for i in j['orders']]
        return oid in w

    # 指定した取引ID以後の取引履歴を取得する関数（Noneの場合は最新の取引を取得）
    def get_transactions(self, tid=None, only_data=True):
        self.nonce = self.nonce +1
        if tid == None:
            j = self._private_api('/api/exchange/orders/transactions_pagination?limit=25',self.nonce)
        else:
            j = self._private_api(f'/api/exchange/orders/transactions_pagination?limit=25&starting_after={tid}',
                                  self.nonce)
        if only_data == True:
            j = j['data']

        return j

    # 全期間の取引履歴を取得する関数
    def get_all_transactions(self):
        j = self.get_transactions(only_data=False)
        j_list = []
        while True:
            if len(j['data']) > 0:
                j_list.extend(j['data'])
                next_tid = j['data'][len(j['data']) - 1]['id']
                while True:
                    try:
                        j = self.get_transactions(tid=next_tid,only_data=False)
                        if j['success'] == False:
                            time.sleep(1)
                            continue
                        break
                    except:
                        time.sleep(1)
                        continue
                continue
            else:
                break
        return j_list





import pprint

API_KEY = set_params.CC_API_KEY
API_SECRET = set_params.CC_API_SECRET
API_URL = set_params.CC_API_URL
api = CcApi(API_KEY, API_SECRET, API_URL)

pagination = {'pagination':{'ending_before': None,
               'limit': 1,
               'order': 'desc',
               'starting_after': None}}

j = api.get_all_transactions()
pprint.pprint(j)
print(len(j))

# requests.get()