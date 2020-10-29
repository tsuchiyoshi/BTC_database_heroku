# BTC_database_with_heroku
## システム概要について
仮想通貨取引所のAPIを利用し、価格を取得しDBに格納したり自動取引を行ったりするHeroku上のアプリです。<br>
詳細は以下をご参考ください。<br>
https://docs.google.com/presentation/d/1-8wJeXehxp8zDAVGuM2IYXIll8zbkincWJGZuJNrLE0/edit?usp=sharing

## 個々のファイルについて
- Heroku 用の設定ファイル
    - runtime.txt
        <br>　実行環境のpythonのバージョンを指定するためのファイル（python-3.7.3）
    - requirements.txt
        <br>　Herokuにインストールが必要なpython用ライブラリを指定するためのファイル
    - Procfile
        <br>　btc_auto_trade.py をHeroku上で Worker として常時実行させるためのファイル
    - sample.env
        <br>　Heroku へ環境変数を設定する".env"ファイルのサンプル

- 価格データベース格納用実行ファイル
    - bitbank_api.py
        <br>　bitbankのAPIを利用して BTC,ETH,MONA の対JPY価格を取得し、Herokuに構築したDBへ価格を格納するためのファイル
    - bitbank_graph.py
        <br>　DBに格納された仮想通貨の価格をグラフとして表示させるためのファイル

- 自動取引用実行ファイル
    - btc_auto_trade.py
        <br>　Coincheck,BitFlyer等の取引所APIを利用し、特定のルールのもと各取引所でBTC・JPYを自動取引する実行ファイル
    - cclib.py, bflib.py
        <br>　取引所ごとに仕様が異なるAPIの主要機能(価格情報・板情報・口座残高取得、売買発注・キャンセル等)を、btc_auto_trade.pyで取引所に依らず使えるよう、共通の形の関数にまとめ直した簡易的なライブラリ
- その他
    - sample_config.py
        <br>　ローカルでファイルを動作させる場合に ".env" ファイルの代わりになる "congig.py" ファイルのサンプル
    - set_params.py
        <br>　Heokuの環境変数またはローカルの設定ファイル(config)を読み込むためのファイル
    - Readme.md
        <br>　本ファイル

- 開発中
    - get_btc_historicaldata.py
        <br>CoinAPIからCoincheckのヒストリカル価格データを取得し、csvにしてGoogleDriveに保存するプログラム