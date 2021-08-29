# stock_lottery

**目的**: 隨時掌握最新的股票申購資訊，用Line即時通知自己，為自己賺取更高的勝率(期望值)

備註:申購類似現實的樂透，觀察申購價與該支股票目前價差，預設撥券日當天能得到的獲利，買進樂透，如果抽中，即可獲得價差獎勵。

**注意**
不是保證獲利，還是需要觀察價差以及公司成長性，去做取捨，投資有賺有賠，詳情請閱讀公開說明書。

## Step 1 : 複製該project到期望儲存的地方

```
git clone https://github.com/jaesm14774/stock_lottery.git
```

## Step 2 : 更改stock_lottery_notify中的Line token成你設定的line token(可以推播最新通知到line 群駔)

```
token='<your token>' #更改your token 成已設定line群組token
```

## Step 3 : python執行stock_lottery_notify.py檔，產生past(歷史資料)，以及new(最新資料)，會推播new資料

```
python stock_lottery_notify.py
```

可以排程持續執行，會更新資料到past(history的資料)，和推播最新申購消息到設定的Line群組

結果:

![](https://i.imgur.com/fg880jG.png)
