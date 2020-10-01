import datetime
import time
import pytz
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

# アルゴリズム個別の設定
# 前提条件：このアルゴリズムはHeroku上で毎時50分ごろ実行される
entry_min = 0       # エントリーする時刻(分)の設定
duration = 28       # 決済する時間(X分後)の設定(50分以内)
loss_cut_rate = 3.0 # 損切りを行うレート(%)
strategy = "Hourly Anomaly"

###############################
######## 初期設定ここまで ########
###############################

print('Log : Initialize...')
print(f'''==========================
order_mim_size : {order_mim_size} btc
order_digit    : {order_digit}
fee_rate       : {fee_rate} %
buy_unit       : {buy_unit} btc
loss_cut_rate  : {loss_cut_rate} %
strategy       : {strategy}
exchange       : {select_exchange}
==========================''')
# BTC残高を調べる
balance = api.balance()
# エントリー時の残高(後の結果集計に利用)
entry_jpy = balance['jpy']
entry_btc = balance['btc']
print(f'Log : Current balance {entry_jpy}yen / {entry_btc}btc')
print('Log : Auto-Trade start')


# 5分前価格の取得
entry_min_minus_5 = (entry_min + 55) % 60
lag = 1 - int((entry_min + 55)/60)

while True:
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    minute = now.minute
    hour = now.hour
    if minute < entry_min_minus_5:
        print(f"Log : get BTC/JPY({format(hour,'02')}:{format(entry_min_minus_5,'02')}) standby.../now {format(hour,'02')}:{format(minute,'02')}")
        time.sleep(20)
        pass
    else:
        # 板情報の更新、取得
        ob = api.orderbook()
        # 価格の取得(bidの先頭)
        price_entry_m5 = ob['bids'][0][0]
        print(f"Log : BTC({format(hour,'02')}:{format(minute,'02')}) is {price_entry_m5} yen")
        print(f"Log : get BTC/JPY({format(hour + lag, '02')}:{format(entry_min,'02')}) standby.../now {format(hour, '02')}:{format(minute, '02')}")
        break

# 200秒停止
time.sleep(240)

# 0分前価格の取得
while True:
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    minute = now.minute
    hour = now.hour
    if minute != entry_min:
        print(f"Log : get BTC/JPY({format(hour + lag,'02')}:{format(entry_min,'02')}) standby... / now {format(hour,'02')}:{format(minute,'02')}")
        time.sleep(20)
        pass
    else:
        # 板情報の更新、取得
        ob = api.orderbook()
        # 価格の取得(bidの先頭)
        price_entry = ob['bids'][0][0]
        print(f"Log : BTC({format(hour,'02')}:{format(minute,'02')}) is {price_entry} yen")
        break



#### BTCの売買フェーズ ####
# 5分間ROCの計算
roc = (price_entry - price_entry_m5) / price_entry_m5
print(f"Log : ROC is {roc}")

if roc < 0:
    print("Log : Strategy LONG")

    #### BTC購入フェーズ ####
    print('Log : ##### BTC Buy phase #####')
    buy_success_flug = 0

    # BTC購入に最大３回トライする
    for i in range(3):
        # 板情報の取得
        ob = api.orderbook()
        # 購入予定価格を決定(bidの先頭)
        buy_price = ob['bids'][0][0]
        # 購入数量を計算(持っている円資産で買えるだけ買う)。購入数量 = 数量 * (1+fee*2)-BTC残高
        buy_amount = round(balance['jpy'] / (buy_price * buy_unit * (1 + 0.01 * fee_rate)), order_digit)

        if buy_amount - order_mim_size > 0:
            # 単位の整形(zaifでは丁度整数単位の時、intでないと発注エラーを起こす。zaif以外はあってもなくても)
            if buy_amount == int(buy_amount):
                buy_amount = int(buy_amount)

            # JPY残高の確認
            if balance['jpy'] < buy_amount * buy_price:
                print('Log : Insufficient JPY balance')
                break
            # 注文。BTCの場合priceを整数にする。
            print('Log : Buy order {0} yen/btc x {1} btc = {2} yen'.format(int(buy_price), buy_amount,
                                                                           int(buy_price) * buy_amount))
            oid = api.buy(int(buy_price), buy_amount)
            print('Log : Buy oid={0}'.format(oid))

            # 注文がサーバーで処理されるまで少し待つ
            time.sleep(10)
            # さらに最大50秒間注文が約定するのを待つ
            for i in range(0, 10):
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
                buy_success_flug = 1
                break
        else:
            # JPYが最低売買単位購入に必要な額に満たない場合は何もしない
            print('Log : Insufficient JPY balance')
            break

    # BTC購入が成功した場合のフロー
    if buy_success_flug == 1:
        # 損切り価格での売り発注
        loss_cut_price = int(buy_price * (1-0.01*loss_cut_rate))
        # 注文。BTCの場合priceを整数にする。
        print('Log : Loss-cut order {0} yen/btc x {1} btc = {2} yen'.format(int(loss_cut_price), buy_amount,
                                                                       int(loss_cut_price) * buy_amount))
        oid_loss = api.buy(int(buy_price), buy_amount)
        print('Log : Loss-cut Sell oid={0}'.format(oid_loss))

        # 決済時間(duration)まで待機
        print(f'wait {duration} min ...')
        time.sleep(duration * 60)

        #### 決済フェーズ ####
        print('Log : ##### BTC Sell phase #####')
        # ロスカットが発生していない場合。BTCを成行売で決済し、残っているロスカット注文をキャンセルする。
        if api.is_active_order(loss_oid) == False:
            api.cancel(loss_oid)
            print('Log : Loss-Cut order cancel oid={0}'.format(loss_oid))
            # 注文がサーバーで処理されるまで少し待つ
            time.sleep(5)
            # 注文が成立するまで（永遠に）待つ
            while api.is_active_order(loss_oid):
                print('Log : Cancel wait...')
                time.sleep(5)
            print('Cancel completed! oid={0}'.format(oid))

            # 成行売り注文
            print('Log : Market-Sell order {1} btc'.format(buy_amount))
            oid = api.market_sell(buy_amount)
            # 注文がサーバーで処理されるまで少し待つ
            time.sleep(5)
            # 注文が成立するまで（永遠に）待つ
            while api.is_active_order(oid):
                print('Log : Sell wait...')
                time.sleep(5)
            print('Sell completed! oid={0}'.format(oid))

        else:
            print('Log : Loss-Cut has occurred!')
    else:
        print("Log : BTC Buy failed.")


elif roc > 0:
    print("Log : Strategy SHORT")

    #### BTC売却フェーズ　####
    print('Log : ##### BTC Sell phase #####')
    sell_success_flug = 0

    # BTC売却に最大３回トライする
    for i in range(3):
        # 板情報の取得
        ob = api.orderbook()
        # 売却予定価格を決定(bidの先頭)
        sell_price = ob['bids'][0][0]
        # 売却数量はBTC残高*(1-fee)
        sell_amount = round(balance['btc']*(1-0.01*fee_rate), order_digit)

        if sell_amount < order_mim_size:
            # 部分的な約定等で最小売却単位に届かないなら終了する
            print('Log : Insufficient BTC balance')
            print('Log : Stop trading.')
            sys.exit()
        else:
            # 単位の整形
            if sell_amount == int(sell_amount):
                sell_amount = int(sell_amount)
            print('Log : Sell order {0} yen/btc x {1} btc = {2} yen'.format(int(sell_price), sell_amount, int(sell_price)*sell_amount))

            # 利益をのせて注文。BTCの場合はpriceを整数にする
            oid = api.sell(int(sell_price), sell_amount)
            print('Log : Sell oid={0}'.format(oid))
            # 注文がサーバーで処理されるまで少し待つ
            time.sleep(5)
            # さらに最大50秒間注文が約定するのを待つ
            for i in range(0, 10):
                if api.is_active_order(oid) == False:
                    oid = None
                    break
                print('Log : Sell Wait...')
                time.sleep(5)

        # 注文が残っていたらキャンセルする
        if oid != None:
            api.cancel(oid)
            print('Log : Sell order canceled! oid={0}'.format(oid))
            time.sleep(5)
        else:
            print('Log : Sell completed! oid={0}'.format(oid))
            sell_success_flug = 1
            break

    # BTC売却が成功した場合のフロー
    if sell_success_flug == 1:
        # 損切り価格での売り発注
        loss_cut_price = int(sell_price * (1 + 0.01 * loss_cut_rate))
        loss_cut_amount = round((sell_price * sell_amount)/loss_cut_price, order_digit)
        loss_cut_amount = max(order_mim_size,loss_cut_amount)
        # 注文。BTCの場合priceを整数にする。
        print('Log : Loss-cut order {0} yen/btc x {1} btc = {2} yen'.format(int(loss_cut_price), loss_cut_amount,
                                                                            int(loss_cut_price) * loss_cut_amount))
        oid_loss = api.buy(int(loss_cut_price), loss_cut_amount)
        print('Log : Loss-cut Buy oid={0}'.format(oid_loss))

        # 決済時間(duration)まで待機
        print(f'wait {duration} min ...')
        time.sleep(duration * 60)

        #### 決済フェーズ ####
        print('Log : ##### BTC Buy phase #####')
        # ロスカットが発生していない場合。残っているロスカット注文をキャンセルし、BTCを成行買いで決済する。
        if api.is_active_order(loss_oid) == False:
            api.cancel(loss_oid)
            print('Log : Loss-Cut order cancel oid={0}'.format(loss_oid))
            # 注文がサーバーで処理されるまで少し待つ
            time.sleep(5)
            # 注文が成立するまで（永遠に）待つ
            while api.is_active_order(loss_oid):
                print('Log : Cancel wait...')
                time.sleep(5)
            print('Cancel completed! oid={0}'.format(oid))

            # 成行買い注文
            buy_amount_jpy = int(sell_price*sell_amount)
            print(f'Log : Market-Buy order {buy_amount_jpy}yen')
            oid = api.market_buy(buy_amount_jpy)
            # 注文がサーバーで処理されるまで少し待つ
            time.sleep(5)
            # 注文が成立するまで（永遠に）待つ
            while api.is_active_order(oid):
                print('Log : Market-Buy wait...')
                time.sleep(5)
            print('Market-Buy completed! oid={0}'.format(oid))

        else:
            print('Log : Loss-Cut has occurred!')
    else:
        print("Log : BTC sell failed.")
else:
    print("Log : ROC Error")

#### 最終的な損益の計算 ####
# 残高の更新
current_balance = api.balance()
current_jpy = current_balance['jpy']
current_btc = current_balance['btc']
print(
    f"Log : Result => {current_jpy}yen({current_jpy - entry_jpy}yen) / {current_btc}btc({current_btc - entry_btc}btc)")
print('Log : Stop trading.')
sys.exit()