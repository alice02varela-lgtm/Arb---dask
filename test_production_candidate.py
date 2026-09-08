from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_safety_defaults():
    r=client.get('/api/config/safety'); assert r.status_code==200
    data=r.json(); assert data['live_trading_enabled'] is False; assert data['withdrawals_enabled'] is False

def test_health_version():
    r=client.get('/api/health'); assert r.status_code==200
    assert r.json()['version']=='3.2-production-candidate'

def test_connectors_are_gated_by_default():
    data=client.get('/api/connectors').json()
    assert data['BINANCE_TESTNET']['enabled'] is False
    assert data['OKX_DEMO']['enabled'] is False
