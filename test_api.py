from fastapi.testclient import TestClient
from app.main import app

def test_health():
 r=TestClient(app).get('/api/health'); assert r.status_code==200; assert r.json()['live_trading_enabled'] is False

def test_risk_endpoint():
 r=TestClient(app).post('/api/risk/check',json={'net_profit_pct':1,'notional_aoa':100000,'slippage_pct':.1,'quote_age_ms':100,'liquidity_ok':True}); assert r.json()['decision']=='GO'
