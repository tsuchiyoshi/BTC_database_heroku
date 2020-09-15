# bitflyer用送信関数
import hashlib
import hmac
import requests
import datetime
import json
import urllib


class BfApi:
    CURRENCY_PAIR = ''
    API_KEY = ''
    API_SECRET = ''
    API_URL = ''
    nonce = int((datetime.datetime.today() - datetime.datetime(2020, 1, 1)).total_seconds()) * 10

    # コンストラクタ
    def __init__(self, key, secret, url, product_code='BTC_JPY'):
        self.API_KEY = key
        self.API_SECRET = secret
        self.API_URL = url
        self.CURRENCY_PAIR = product_code
        return

    # bitflyerのプライベートAPIにリクエストを送信する関数
    def _private_api(self, i_path, i_params=None):
        timestamp = str(datetime.datetime.today())
        headers = {'ACCESS-KEY': self.API_KEY,
                   'ACCESS-TIMESTAMP': timestamp,
                   'Content-Type': 'application/json'}
        s = hmac.new(bytearray(self.API_SECRET.encode('utf-8')), digestmod=hashlib.sha256)
        b = None
        if i_params is None:
            w = timestamp + 'GET' + i_path
            s.update(w.encode('utf-8'))
            headers['ACCESS-SIGN'] = s.hexdigest()
            b = requests.get(self.API_URL + i_path, headers=headers)
        else:
            body = json.dumps(i_params);
            w = timestamp + 'POST' + i_path + body
            s.update(w.encode('utf-8'))
            headers['ACCESS-SIGN'] = s.hexdigest()
            b = requests.post(API_URL + i_path, data=body, headers=headers)
        # 戻り値のチェック
        if b.status_code != 200:
            raise Exception('HTTP ERROR status={0},{1}'.format(b.status_code, b.json()))
        return b

    # 売買を行うAPIの共通部分
    def _trade_api(self, price, amount, side):
        j = self._private_api('/v1/me/sendchildorder', {
            'product_code': self.CURRENCY_PAIR,
            'child_order_type': 'LIMIT',
            'side': side,
            'price': price,
            'size': amount,
            'time_in_force': 'GTC'}).json()
        return j

    # 板情報を得る関数
    def orderbook(self):
        r = requests.get('https://api.bitflyer.jp/v1/board?product_code=BTC_JPY')
        j = r.json()
        return {'bids': [(i['price'], i['size']) for i in j['bids']],
                'asks': [(i['price'], i['size']) for i in j['asks']]}

    # 残高を得る関数
    def balance(self):
        j = self._private_api('/v1/me/getbalance').json()
        jpy = [i for i in j if i['currency_code'] == 'JPY'][0]
        btc = [i for i in j if i['currency_code'] == 'BTC'][0]
        eth = [i for i in j if i['currency_code'] == 'ETH'][0]
        return {'btc': btc['available'],
                'jpy': jpy['available'],
                'eth': eth['available']}

    # 売り注文を実行する関数
    def sell(self, price, amount):
        j = self._trade_api(price, amount, 'SELL')
        return j['child_order_acceptance_id']

    # 買い注文を実行する関数
    def buy(self, price, amount):
        j = self._trade_api(price, amount, 'BUY')
        return j['child_order_acceptance_id']

    # 注文をキャンセルする関数
    def cancel(self, oid):
        self._private_api('/v1/me/cancelchildorder',
                          {'product_code': self.CURRENCY_PAIR,
                           'child_order_acceptance_id': oid})
        return

    # 注文の状態を調べる関数
    def is_active_order(self, oid):
        j = self._private_api('/v1/me/getchildorders?' +
                              urllib.parse.urlencode({'product_code': self.CURRENCY_PAIR})).json()
        t = [i for i in j if i['child_order_acceptance_id'] == oid]

        if len(t) > 0:
            if t[0]['child_order_acceptance_id'] == 'ACTIVE':
                return True
        return False