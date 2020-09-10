import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import bitbank_api

# [入れて明示させないと後々言われる可能性がありますよ]という警告表示が出る場合があるので入れておく
# 参考記事：https://github.com/pandas-dev/pandas/pull/24964
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

def single_chart():
  with bitbank_api.get_connection() as conn:
      sql = "SELECT {}, price_at FROM price".format('btc')
      df = pd.read_sql(sql, conn, index_col="price_at")
      return df

msg = single_chart()
print(msg)