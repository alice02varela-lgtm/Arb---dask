from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def test_health():
 r=c.get('/api/health'); assert r.status_code==200; assert r.json()['live_trading_enabled'] is False
def test_autobot_gate():
 c.post('/api/autobot/disarm'); r=c.post('/api/autobot/run',json={'net_profit_pct':2,'notional_aoa':1000,'slippage_pct':0,'quote_age_ms':0,'liquidity_ok':True}); assert r.json()['status']=='BLOCKED'
def test_dex_guard_never_signs():
 r=c.post('/api/dex/risk',json={'quote_age_ms':100,'slippage_pct':0.2,'gas_aoa':100}); assert r.json()['decision']=='NO-GO'; assert r.json()['checks']['wallet_signing'] is False
