# 通貨ベアを選択(現在利用不可)
CURRENCY_PAIR = ""

# 利用する取引所を選択（'bf','cc'）
EXCHANGE = ""

########################
### BitFlyerの初期設定 ###
########################
# APIキー
BF_API_KEY = ""
BF_API_SECRET = ""
BF_API_URL = ""
# 取引所のパラメータ
BF_ORDER_MIN_SIZE = 0.001   # BTC数量最小値
BF_ORDER_DIGIT = 8          # BTC数量の桁数
BF_FEE_RATE = 0.15          # 取引手数料のレート(%)
# 取引パラメータ
BF_BUY_UNIT = 0.001         # 購入単位
BF_PROFIT = 5000            # 価格差


#########################
### CoinCheckの初期設定 ###
#########################
# APIキー
CC_API_KEY = ""
CC_API_SECRET = ""
CC_API_URL = ""
# 取引所のパラメータ
CC_ORDER_MIN_SIZE = 0.005   # BTC数量最小値
CC_ORDER_DIGIT = 4          # BTC数量の桁数
CC_FEE_RATE = 0.0           # 取引手数料のレート(%)
# 取引パラメータ
CC_BUY_UNIT = 0.005         # 購入単位
CC_PROFIT = 4000            # 価格差


#############################
### Zaifの初期設定（現在不可）###
#############################
# APIキー
ZF_API_KEY = ""
ZF_API_SECRET = ""
ZF_API_URL = ""
# 取引所のパラメータ
ZF_ORDER_MIN_SIZE = 0.0001  # BTC数量最小値
ZF_ORDER_DIGIT = 4          # BTC数量の桁数
ZF_FEE_RATE = 0.00          # 取引手数料のレート(%)
# 取引パラメータ
ZF_BUY_UNIT = 0.0001        # 購入単位
ZF_PROFIT = 5000            # 価格差


###################
### Herokuの設定 ###
###################
# HerokuデータベースのURI
URI = ""

