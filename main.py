import os, sqlite3, time, uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from .market import opportunity
from .core import RiskEngine, CircuitBreaker, Leg, Route, OrderState
from .connectors import BinanceTestnet, OKXDemo
from .orchestrator import AutoBot
from .dex import DEXGuard

app=FastAPI(title='ArbDask v3.0 Release Candidate')
risk=RiskEngine(float(os.getenv('MIN_NET_PROFIT_PCT','0.50')),float(os.getenv('MAX_TRADE_NOTIONAL_AOA','500000')),float(os.getenv('MAX_SLIPPAGE_PCT','0.50')),float(os.getenv('MAX_QUOTE_AGE_MS','1500')))
breaker=CircuitBreaker(); routes={}; stopped=False
connectors={'BINANCE_TESTNET':BinanceTestnet(),'OKX_DEMO':OKXDemo()}
DB=os.getenv('ARBDASK_DB','arb_dask.db')

def db():
 c=sqlite3.connect(DB); c.execute('create table if not exists audit(id integer primary key,ts integer,event text,detail text)'); c.execute('create table if not exists executions(route_id text primary key,ts integer,status text,pnl_aoa real)'); c.commit(); return c

def audit(event,detail):
 c=db(); c.execute('insert into audit(ts,event,detail) values(?,?,?)',(int(time.time()*1000),event,detail)); c.commit(); c.close()

autobot=AutoBot(risk,breaker,audit)
dex_guard=DEXGuard()

@app.get('/api/health')
def health(): return {'status':'ok','version':'3.2-production-candidate','trading_mode':os.getenv('TRADING_MODE','paper'),'live_trading_enabled':False,'emergency_stop':stopped,'circuit_breaker':breaker.tripped}

@app.get('/api/config/safety')
def safety_config():
 return {'trading_mode':os.getenv('TRADING_MODE','paper'),'live_trading_enabled':False,'withdrawals_enabled':False,'emergency_stop':stopped,'circuit_breaker':breaker.tripped}

@app.get('/api/connectors')
def connector_status(): return {k:v.health() for k,v in connectors.items()}

@app.get('/api/autobot')
def autobot_status(): return {'enabled':autobot.enabled,'live_trading_enabled':False,'mode':os.getenv('TRADING_MODE','paper')}

@app.post('/api/autobot/arm')
def autobot_arm(): autobot.arm(); return {'status':'ARMED','mode':os.getenv('TRADING_MODE','paper'),'live_trading_enabled':False}

@app.post('/api/autobot/disarm')
def autobot_disarm(): autobot.disarm(); return {'status':'DISARMED'}

@app.post('/api/autobot/run')
def autobot_run(op:dict): return autobot.evaluate_and_execute(op)

@app.post('/api/dex/risk')
def dex_risk(quote:dict): return dex_guard.validate(quote)

@app.get('/api/opportunities')
def opportunities():
 return [opportunity(s) for s in ('BTC/USDT','ETH/USDT','SOL/USDT')]

@app.post('/api/risk/check')
def risk_check(op:dict): return risk.evaluate(op)

@app.post('/api/paper/execute')
def paper_execute(op:dict):
 global stopped
 if stopped or breaker.tripped: raise HTTPException(409,'Emergency stop/circuit breaker active')
 decision=risk.evaluate(op)
 audit('RISK_DECISION',str(decision))
 if decision['decision']!='GO': raise HTTPException(422,{'decision':decision})
 rid='route-'+uuid.uuid4().hex[:12]
 legs=[Leg(op['buy_venue'],op['symbol'],'BUY',1,op['buy_price']),Leg(op['sell_venue'],op['symbol'],'SELL',1,op['sell_price'])]
 for l in legs: l.state=OrderState.SENT; l.state=OrderState.ACK; l.filled_qty=l.quantity; l.avg_price=l.price; l.state=OrderState.FILLED
 pnl=op['notional_aoa']*op['net_profit_pct']/100
 route=Route(rid,legs,status='COMPLETED',pnl_aoa=pnl); routes[rid]=route
 c=db(); c.execute('insert or replace into executions(route_id,ts,status,pnl_aoa) values(?,?,?,?)',(rid,int(time.time()*1000),route.status,pnl)); c.commit(); c.close()
 audit('PAPER_EXECUTION',rid)
 return {'route_id':rid,'status':route.status,'pnl_aoa':round(pnl,2),'legs':[l.state for l in legs]}

@app.post('/api/emergency-stop')
def emergency_stop():
 global stopped; stopped=True; breaker.tripped=True; audit('EMERGENCY_STOP','manual'); return {'status':'STOPPED'}

@app.post('/api/emergency-reset')
def emergency_reset():
 global stopped; stopped=False; breaker.reset(); audit('EMERGENCY_RESET','manual'); return {'status':'ARMED','live_trading_enabled':False}

@app.get('/api/executions')
def executions():
 c=db(); rows=c.execute('select route_id,status,pnl_aoa from executions order by ts desc limit 200').fetchall(); c.close(); return [{'route_id':a,'status':b,'pnl_aoa':c} for a,b,c in rows]

@app.get('/',response_class=HTMLResponse)
def dashboard():
 return '''<!doctype html><html lang="pt"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ArbDask</title><style>body{margin:0;background:#0b0d10;color:#eee;font-family:Arial,sans-serif}aside{position:fixed;width:220px;height:100vh;background:#11151a;padding:24px;box-sizing:border-box}main{margin-left:220px;padding:30px}.brand{font-size:26px;font-weight:800;color:#d9ad4b}.muted{color:#8c96a3}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.card{background:#14191f;border:1px solid #252c35;border-radius:14px;padding:18px}.value{font-size:25px;font-weight:700;margin-top:8px}.row{display:flex;gap:16px;margin-top:18px}.row .card{flex:1}button{background:#d9ad4b;border:0;padding:12px 18px;border-radius:9px;font-weight:700;cursor:pointer}.danger{background:#b53b3b;color:white}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:12px;border-bottom:1px solid #252c35}</style></head><body><aside><div class="brand">ArbDask</div><p class="muted">CRYPTO ARBITRAGE OS</p><p>Overview</p><p>Oportunidades</p><p>Execuções</p><p>Arbitragem CEX</p><p>Arbitragem DEX</p><p>Gestão de risco</p><p>Carteiras</p><p>Configurações</p></aside><main><h1>Dashboard</h1><div class="grid"><div class="card">Modo<div class="value" id="mode">—</div></div><div class="card">Sistema<div class="value" id="status">—</div></div><div class="card">Circuit Breaker<div class="value" id="breaker">—</div></div><div class="card">Moeda<div class="value">Kz / AOA</div></div></div><div class="row"><div class="card"><h2>Oportunidades</h2><table id="ops"><tr><th>Par</th><th>Rota</th><th>Spread líquido</th><th>Decisão</th></tr></table></div><div class="card"><h2>Controlo</h2><p>Trading real: <b>DESATIVADO</b></p><button class="danger" onclick="stop()">EMERGENCY STOP</button><button onclick="reset()">Rearmar</button></div></div></main><script>async function load(){let h=await (await fetch('/api/health')).json();mode.textContent=h.trading_mode;status.textContent=h.status.toUpperCase();breaker.textContent=h.circuit_breaker?'TRIPPED':'ARMED';let ops=await (await fetch('/api/opportunities')).json();let t=document.getElementById('ops');ops.forEach(o=>{if(o.error)return;let tr=t.insertRow();tr.innerHTML=`<td>${o.symbol}</td><td>${o.buy_venue} → ${o.sell_venue}</td><td>${o.net_profit_pct.toFixed(2)}%</td><td>${o.net_profit_pct>=0.5?'GO':'NO-GO'}</td>`})}async function stop(){await fetch('/api/emergency-stop',{method:'POST'});load()}async function reset(){await fetch('/api/emergency-reset',{method:'POST'});load()}load();</script></body></html>'''
