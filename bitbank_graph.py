import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import bitbank_api
import sys

# [入れて明示させないと後々言われる可能性がありますよ]という警告表示が出る場合があるので入れておく
# 参考記事：https://github.com/pandas-dev/pandas/pull/24964
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

def single_chart():
  with bitbank_api.get_connection() as conn:
      # DBから価格の取得
      sql = "SELECT {0}, price_at FROM price".format(coin1)
      df = pd.read_sql(sql, conn, index_col="price_at")
      # グラフの描画
      fig, ax = plt.subplots()
      ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))
      ax.plot(df.index, df.values)
      plt.show()

def double_chart():
  with bitbank_api.get_connection() as conn:
      # DBから価格の取得
      sql = "SELECT {0}, {1}, price_at FROM price".format(coin1,coin2)
      df = pd.read_sql(sql, conn, index_col="price_at")

      # グラフの描画
      fig, ax1 = plt.subplots()
      ax2 = ax1.twinx() # ax1とx軸を共有するax2を新規作成
      fig.subplots_adjust(left=0.13,right=0.85)
      ax1.plot(df.index, df[coin1], color="blue", label=coin1)
      ax2.plot(df.index, df[coin2], color="orange", label=coin2)
      ax1.set_ylabel(coin1)
      ax2.set_ylabel(coin2)

      # グラフの凡礼を一つにまとめる
      ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))
      handler1, label1 = ax1.get_legend_handles_labels()
      handler2, label2 = ax2.get_legend_handles_labels()
      ax2.legend(handler1 + handler2, label1 + label2)

      plt.show()

def triple_chart():
   with bitbank_api.get_connection() as conn:
       # DBから価格の取得
       sql = "SELECT btc, eth, mona, price_at FROM price"
       df = pd.read_sql(sql, conn, index_col="price_at")

       # 相関係数算出のために対数変化率を計算
       logdiff_df = df.apply(lambda x: np.log(x)).diff()
       print("相関係数:")
       print(logdiff_df.corr())
       # 正規化する
       ndf = df.apply(lambda x: (x - x.mean()) / x.std(), axis=0)
       fig, ax = plt.subplots()
       ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))
       ax.plot(ndf.index, ndf.values)
       plt.legend(ndf.columns.values)  # ndfのcolumn名をそのまま凡例に

       plt.show()

coin_list = ["btc", "eth", "mona"]

def main():
    error_msg1="指定した通貨名は正しくありません。[btc, eth, mona]から選択して下さい。"
    args = sys.argv

    # 引数なし⇒グラフ3つ
    if len(args) == 1:
        msg = triple_chart()
        return msg

    # 引数1つ⇒グラフ1つ
    elif len(args) == 2:
        msg = single_chart(args[1])
        return msg

    # 引数2つ⇒グラフ2つ
    elif len(args) == 3:
        msg = double_chart(args[1], args[2])
        return msg

    # 引数3つ以上⇒エラー
    else:
        return "引数の指定は最大2つまでです。3つのグラフを表示したい場合、引数は必要ありません。"

msg = main()

if msg:
    print(msg)