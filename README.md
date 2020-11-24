# vishnu
bitflyer-lightning（btcfxjpy）用のビットコイン自動売買botです。  

**免責事項**：  
当botの利用により損失や被害が生じた場合、作者は一切の責任を負うことはできません。  
投資は自己責任でお願いします。　　

---
[ライセンス](https://github.com/yuta-komura/vishnu/blob/main/LICENSE)

---    
### パフォーマンス
**initial parameter**：  
asset 1,000,000  

**backtest result**：  
2019-10-06 15:47:00 〜 2020-10-19 22:03:00  
profit 2,532,065  
pf 2.47  
wp 64 %  
trading cnt 99  

profit flow  
<a href="https://imgur.com/CbpHpBq"><img src="https://i.imgur.com/CbpHpBq.png" title="source: imgur.com" /></a>  

entry timing  
▲ BUY ▼ SELL  
<a href="https://imgur.com/GB9GBWT"><img src="https://i.imgur.com/GB9GBWT.png" title="source: imgur.com" /></a>

---  
### 環境  
ubuntu20.04 / mysql / python

---  
### インストール  
**mysql**：  
db.sql参照  
必要なデータベースとテーブルを作成後、  
lib/config.pyに設定してください。
```python:config.py
class DATABASE(Enum):
    class TRADINGBOT(Enum):
        HOST = 'localhost'
        USER = 'user'
        PASSWORD = 'password'
        DATABASE = 'tradingbot'
```

**pythonライブラリ**：  
venv同梱です。プログラム起動時に自動でvenvがアクティベートされます。  

**bitflyer apikey**：  
1．bitflyer-lightningのサイドバーから"API"を選択  
<a href="https://imgur.com/afZrmWf"><img src="https://i.imgur.com/afZrmWf.png" title="source: imgur.com" /></a>  
2．"新しいAPIキーを追加"を選択しapikeyを作成  
<a href="https://imgur.com/x56kiBy"><img src="https://i.imgur.com/x56kiBy.png" title="source: imgur.com" /></a>  
3．lib/config.pyに設定してください。
```python:config.py
class Bitflyer(Enum):
    class Api(Enum):
        KEY = "fcksdjcji9swefeixcJKj1"
        SECRET = "sdjkalsxc90wdwkksldfdscmcldsa"
```

**mpg123インストール**：  
このシステムでは、loggerのwarningまたはerror出力時に  
音声が流れるようになっております。  
```bash
sudo apt update -y
sudo apt install -y mpg123
```

**レバレッジ**：  
bitflyerでは4倍を設定してください。  
このシステムは、レバレッジ1倍分のポジションサイズをとります。  
ポジションサイズの変更は**lib/bitflyer.py**のコンストラクタで設定してください。  
```python:bitflyer.py
    def __init__(self, api_key, api_secret):
        self.api = pybitflyer.API(api_key=api_key, api_secret=api_secret)
        self.PRODUCT_CODE = "FX_BTC_JPY"
        self.LEVERAGE = 1
        self.DATABASE = "tradingbot"
```
---  
### 起動方法  
下記2点のシェルスクリプトを実行してください。（別画面で）  

**get_realtime_data.sh**：  
websocketプロトコルを利用しRealtime APIと通信。  
tickerと約定履歴（ローソク足作成用）を取得します。  
```bash
sh vishnu/main/get_realtime_data.sh
```
**execute.sh**：  
メインスクリプト用  
```bash
sh vishnu/main/execute.sh 
```
---  
### main process  
<a href="https://imgur.com/D9MlxAZ"><img src="https://i.imgur.com/D9MlxAZ.png" title="source: imgur.com" /></a>