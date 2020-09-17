import os

try:
    # ローカル環境の場合（configファイルからのimport）
    import config
    # HerokuサーバのURI
    URI = config.URI

    # 取引所を選択
    EXCHANGE = config.EXCHANGE
    #### bitflyer の初期値 ####
    # APIキー
    BF_API_KEY = config.BF_API_KEY
    BF_API_SECRET = config.BF_API_SECRET
    BF_API_URL = config.BF_API_URL
    # 取引所のパラメータ
    BF_ORDER_MIN_SIZE = config.BF_ORDER_MIN_SIZE  # BTC数量最小値
    BF_ORDER_DIGIT = config.BF_ORDER_DIGIT  # BTC数量の桁数
    BF_FEE_RATE = config.BF_FEE_RATE  # 取引手数料のレート(%)
    # 取引パラメータ
    BF_BUY_UNIT = config.BF_BUY_UNIT  # 購入単位
    BF_PROFIT = config.BF_PROFIT  # 価格差

    #### coincheck の初期値 ####
    # APIキー
    CC_API_KEY = config.CC_API_KEY
    CC_API_SECRET = config.CC_API_SECRET
    CC_API_URL = config.CC_API_URL
    # 取引所のパラメータ
    CC_ORDER_MIN_SIZE = config.CC_ORDER_MIN_SIZE  # BTC数量最小値
    CC_ORDER_DIGIT = config.CC_ORDER_DIGIT  # BTC数量の桁数
    CC_FEE_RATE = config.CC_FEE_RATE  # 取引手数料のレート(%)
    # 取引パラメータ
    CC_BUY_UNIT = config.CC_BUY_UNIT  # 購入単位
    CC_PROFIT = config.CC_PROFIT  # 価格差

except:
    # Herokuサーバの場合（環境変数を利用）

    # HerokuサーバのURI
    URI = os.environ["URI"]

    # 取引所を選択
    EXCHANGE = os.environ["EXCHANGE"]

    #### bitflyer の初期値 ####
    # APIキー
    BF_API_KEY = os.environ["BF_API_KEY"]
    BF_API_SECRET = os.environ["BF_API_SECRET"]
    BF_API_URL = os.environ["BF_API_URL"]
    # 取引所のパラメータ
    BF_ORDER_MIN_SIZE = float(os.environ["BF_ORDER_MIN_SIZE"])  # BTC数量最小値
    BF_ORDER_DIGIT = int(os.environ["BF_ORDER_DIGIT"])  # BTC数量の桁数
    BF_FEE_RATE = float(os.environ["BF_FEE_RATE"])  # 取引手数料のレート(%)
    # 取引パラメータ
    BF_BUY_UNIT = float(os.environ["BF_BUY_UNIT"])  # 購入単位
    BF_PROFIT = int(os.environ["BF_PROFIT"])  # 価格差

    #### coincheck の初期値 ####
    # APIキー
    CC_API_KEY = os.environ["CC_API_KEY"]
    CC_API_SECRET = os.environ["CC_API_SECRET"]
    CC_API_URL = os.environ["CC_API_URL"]
    # 取引所のパラメータ
    CC_ORDER_MIN_SIZE = float(os.environ["CC_ORDER_MIN_SIZE"])  # BTC数量最小値
    CC_ORDER_DIGIT = int(os.environ["CC_ORDER_DIGIT"])  # BTC数量の桁数
    CC_FEE_RATE = float(os.environ["CC_FEE_RATE"])  # 取引手数料のレート(%)
    # 取引パラメータ
    CC_BUY_UNIT = float(os.environ["CC_BUY_UNIT"])  # 購入単位
    CC_PROFIT = int(os.environ["CC_PROFIT"])  # 価格差