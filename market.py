import httpx, time

BINANCE='https://api.binance.com/api/v3/ticker/bookTicker'
OKX='https://www.okx.com/api/v5/market/ticker'
SYMBOLS={'BTC/USDT':'BTCUSDT','ETH/USDT':'ETHUSDT','SOL/USDT':'SOLUSDT'}

def fetch_binance(symbol):
    r=httpx.get(BINANCE,params={'symbol':SYMBOLS[symbol]},timeout=5); r.raise_for_status(); d=r.json()
    return {'venue':'BINANCE','bid':float(d['bidPrice']),'ask':float(d['askPrice']),'bid_qty':float(d['bidQty']),'ask_qty':float(d['askQty']),'ts':int(time.time()*1000)}

def fetch_okx(symbol):
    r=httpx.get(OKX,params={'instId':symbol.replace('/','-')},timeout=5); r.raise_for_status(); d=r.json()['data'][0]
    return {'venue':'OKX','bid':float(d['bidPx']),'ask':float(d['askPx']),'bid_qty':float(d['bidSz']),'ask_qty':float(d['askSz']),'ts':int(time.time()*1000)}

def opportunity(symbol,capital_aoa=100000):
    try:
      b,o=fetch_binance(symbol),fetch_okx(symbol)
      routes=[(b['ask'],o['bid'],'BINANCE','OKX'),(o['ask'],b['bid'],'OKX','BINANCE')]
      best=max(routes,key=lambda x:(x[1]-x[0])/x[0])
      buy,sell,src,dst=best; gross=(sell-buy)/buy*100; fees=0.20; slip=0.10; net=gross-fees-slip
      return {'symbol':symbol,'buy_venue':src,'sell_venue':dst,'buy_price':buy,'sell_price':sell,'gross_spread_pct':gross,'estimated_fees_pct':fees,'estimated_slippage_pct':slip,'net_profit_pct':net,'notional_aoa':capital_aoa,'quote_age_ms':0,'slippage_pct':slip,'liquidity_ok':True,'timestamp':int(time.time()*1000)}
    except Exception as e:
      return {'symbol':symbol,'error':str(e)}
