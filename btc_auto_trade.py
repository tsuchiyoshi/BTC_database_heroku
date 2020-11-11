import time
import set_params
from bflib import BfApi
from cclib import CcApi
import sys

# 取引所を選択
select_exchange = set_params.EXCHANGE

#### bitflyer の初期値 ####
if select_exchange == 'bf':
    # APIキー
    API_KEY = set_params.BF_API_KEY
    API_SECRET = set_params.BF_API_SECRET
    API_URL = set_params.BF_API_URL
    # 取引所のパラメータ
    order_mim_size = set_params.BF_ORDER_MIN_SIZE   # BTC数量最小値
    order_digit = set_params.BF_ORDER_DIGIT         # BTC数量の桁数
    fee_rate = set_params.BF_FEE_RATE               # 取引手数料のレート(%)
    # 取引パラメータ
    buy_unit = set_params.BF_BUY_UNIT               # 購入単位
    profit = set_params.BF_PROFIT                   # 価格差

    api = BfApi(API_KEY, API_SECRET, API_URL)

#### coincheck の初期値 ####
elif select_exchange == 'cc':
    # APIキー
    API_KEY = set_params.CC_API_KEY
    API_SECRET = set_params.CC_API_SECRET
    API_URL = set_params.CC_API_URL
    # 取引所のパラメータ
    order_mim_size = set_params.CC_ORDER_MIN_SIZE   # BTC数量最小値
    order_digit = set_params.CC_ORDER_DIGIT         # BTC数量の桁数
    fee_rate = set_params.CC_FEE_RATE               # 取引手数料のレート(%)
    # 取引パラメータ
    buy_unit = set_params.CC_BUY_UNIT               # 購入単位
    profit = set_params.CC_PROFIT                   # 価格差

    api = CcApi(API_KEY, API_SECRET, API_URL)

else:
    print("Log : 取引所の設定が間違っています。['bf','cc']のいずれかから選択して下さい。")
    sys.exit()
###############################
######## 初期設定ここまで #########
###############################

print('Log : Initialize...')
print(f'''==========================
order_mim_size : {order_mim_size} btc
order_digit    : {order_digit}
fee_rate       : {fee_rate} %
buy_unit       : {buy_unit} btc
profit         : {profit} jpy
exchange       : {select_exchange}
==========================''')
print('Log : Trade start')

while True:
    # 板情報の取得
    ob = api.orderbook()
    # 購入予定価格を決定(bidの先頭)
    buy_price = ob['bids'][0][0]
    # 購入数量を計算。購入数量 = 数量 * (1+fee*2)-BTC残高
    balance = api.balance()
    buy_amount = round(buy_unit*(1+0.01*fee_rate*2) - balance['btc'], order_digit)

    #### BTC購入フェーズ ####
    print('Log : ##### BTC Buy phase #####')
    if (buy_amount > 0) and (balance['btc'] < order_mim_size):
        # BTC残高が不十分なら注文の最小値を考慮して追加購入
        buy_amount = max(order_mim_size, buy_amount)
        # 単位の整形(zaifでは丁度整数単位の時、intでないと発注エラーを起こす。zaif以外はあってもなくても)
        if buy_amount == int(buy_amount):
            buy_amount = int(buy_amount)

        # JPY残高の確認
        if balance['jpy'] < buy_amount*buy_price:
            print('Log : Insufficient JPY balance')
            break

        # 注文。BTCの場合priceを整数にする。
        print('Log : Buy order {0} yen/btc x {1} btc = {2} yen'.format(int(buy_price),buy_amount,int(buy_price)*buy_amount))
        oid = api.buy(int(buy_price), buy_amount)
        print('Log : Buy oid={0}'.format(oid))

        # 注文がサーバーで処理されるまで少し待つ
        time.sleep(10)
        # さらに最大50秒間注文が約定するのを待つ
        for i in range(0,10):
            if api.is_active_order(oid) == False:
                oid = None
                break
            print('Log : Buy Wait...')
            time.sleep(5)

        # 注文が残っていたらキャンセルする
        if oid != None:
            api.cancel(oid)
            print('Log : Buy order canceled! oid={0}'.format(oid))
            time.sleep(5)
        else:
            print('Log : Buy completed! oid={0}'.format(oid))

    else:
        # 売却するBTCがすでにあるなら何もしない
        print('Log : Sufficient BTC balance')

    #### BTC売却フェーズ　####
    print('Log : ##### BTC Sell phase #####')
    # BTC残高を調べる
    balance = api.balance()
    # 売却数量はBTC残高*(1-fee)
    sell_amount = round(balance['btc']*(1-0.01*fee_rate), order_digit)

    if sell_amount < order_mim_size:
        # 部分的な約定等で最小売却単位に届かないならもう一度購入に戻る
        print('Log : Insufficient BTC balance')
        continue
    else:
        # 単位の整形
        if sell_amount == int(sell_amount):
            sell_amount = int(sell_amount)
        print('Log : Sell order {0} yen/btc x {1} btc = {2} yen'.format(int(buy_price + profit), sell_amount, int(buy_price + profit)*sell_amount))

        # 利益をのせて注文。BTCの場合はpriceを整数にする
        oid = api.sell(int(buy_price + profit), sell_amount)
        print('Log : Sell oid={0}'.format(oid))
        # 注文がサーバで処理されるまで少し待つ
        time.sleep(10)
        # 注文が成立するまで（永遠に）待つ
        while api.is_active_order(oid):
            print('Log : Sell wait...')
            time.sleep(5)
        print('Log : Sell completed! oid={0}'.format(oid))

        # 売却時からある程度価格が下がるまで待機(最大10分)する
        for i in range(240):
            # 板情報の取得
            ob = api.orderbook()
            # 現在価格を取得(bidの先頭)
            current_price = ob['bids'][0][0]
            if (buy_price + 0.5 * profit) > current_price:
                break
            time.sleep(5)
            print('Log : Trade standby... now {0} yen/btc'.format(current_price))