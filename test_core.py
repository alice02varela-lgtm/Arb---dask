from app.core import RiskEngine, CircuitBreaker, Leg, OrderState

def test_risk_go():
 r=RiskEngine(); x=r.evaluate({'net_profit_pct':1,'notional_aoa':100000,'slippage_pct':.1,'quote_age_ms':100,'liquidity_ok':True}); assert x['decision']=='GO'

def test_risk_no_go():
 r=RiskEngine(); x=r.evaluate({'net_profit_pct':.2,'notional_aoa':100000,'slippage_pct':.1,'quote_age_ms':100,'liquidity_ok':True}); assert x['decision']=='NO-GO'

def test_breaker():
 b=CircuitBreaker(2); b.failure(); assert not b.tripped; b.failure(); assert b.tripped

def test_order_state_enum(): assert OrderState.FILLED.value=='FILLED'
