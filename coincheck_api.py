import requests
from pprint import pprint
from decimal import Decimal
import psycopg2
import os

# btc_jpy,eth_jpy,mona_jpyの順番で価格を取得する
urls = ["https://public.bitbank.cc/btc_jpy/ticker", \
        "https://public.bitbank.cc/eth_btc/ticker", \
        "https://public.bitbank.cc/mona_jpy/ticker"]
results = []

for url in urls:
    try:
        r = requests.get(url, timeout=5)
        r = r.json()
        results.append(r)
    except:
        print('Error!')
        results = False
        break

# pprint(results)

if results:
    btc = results[0]["data"]["last"]
    eth = results[1]["data"]["last"]
    mona = results[2]["data"]["last"]
    # ethを円換算に変換
    eth = Decimal(btc) * Decimal(eth)


# print(btc,eth,mona)

# Herokuアプリ内のデータベースに接続
def get_connection():
    try:
        # ローカル環境の場合（configファイルからのimport）
        import config
        uri = config.URI
    except:
        # Herokuサーバの場合（環境変数を利用）
        uri = os.environ["URI"]

    return psycopg2.connect(uri)


# 10分おきに価格を取得する
if __name__ == '__main__':
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO price (btc, eth, mona, price_at) VALUES (%s, %s, %s, now())", (btc, eth, mona))
            conn.commit()