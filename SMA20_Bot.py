from finviz.screener import Screener
import finviz
import threading
import alpaca_trade_api as tradeapi
skey = "Insert Secret Key"
apiKey = "Insert API Key"
apiEndpoint = "Insert Endpoint"
api = tradeapi.REST(apiKey,skey)
watchList = [
    "TSLA","AMD","NVDA","XLNX","MSFT","NFLX","SPY","AAPL","DIS","FB","NIO","AMZN","TWTR"
]
def isMarketOpen():
    clock = api.get_clock()
    return clock.is_open
def positionExists(symbol,portfolio):
    for position in portfolio:
        if (symbol == position.symbol):
            return True
    return False
def buyStock(sym,amount):
    print("Buying {} shares of {}".format(amount,sym))
    api.submit_order(
        symbol=sym,
        qty=amount,
        side='buy',
        type='market',
        time_in_force='gtc'
    )
def sellStock(sym,amount):
    api.submit_order(
        symbol=sym,
        qty=amount,
        side='sell',
        type='market',
        time_in_force='opg',
    )
def autoTrade():
    while (isMarketOpen()):
        account = api.get_account()
        if account.trading_blocked:
            print('Account is currently restricted from trading.')
            return
        buyingpower = account.buying_power
        #start by opening new positions
        limitPerStock = buyingpower/len(watchList)
        print("Buying Power {}".format(buyingpower))
        print("Limit Per Stock {}".format(limitPerStock))
        portfolio = api.list_positions()
        for i in watchList():
            if (positionExists(i,portfolio)):
                continue
            else:
                data = finviz.get_stock(i)
                sma20 = float(data['SMA20'].replace("%",""))
                if (sma20 < 0):
                    #we buy the stock
                    price = float(data['Price'])
                    quanitity = 0
                    while ((quanitity+1) * price < limitPerStock and (quanitity+1) * price < buyingpower):
                        quanitity += 1
                    if (quanitity == 0):
                        continue
                    buyStock(i,limitPerStock)
        for position in portfolio:
            profit = position.unrealized_pl
            percentChange = (profit/position.cost_basis) * 100
            if (percentChange > 5):
                sellStock(position.symbol,position.qty)       
    print("Market is Closed")
autoTrade()
        
        
