from .core import Route, Leg, OrderState
import uuid, time

class AutoBot:
    def __init__(self, risk, breaker, audit):
        self.risk=risk; self.breaker=breaker; self.audit=audit; self.enabled=False
    def arm(self): self.enabled=True; self.audit('AUTOBOT_ARMED','paper/testnet-demo only')
    def disarm(self): self.enabled=False; self.audit('AUTOBOT_DISARMED','manual')
    def evaluate_and_execute(self, op):
        if not self.enabled: return {'status':'BLOCKED','reason':'AUTOBOT_DISARMED'}
        if self.breaker.tripped: return {'status':'BLOCKED','reason':'CIRCUIT_BREAKER'}
        d=self.risk.evaluate(op); self.audit('AUTOBOT_RISK',str(d))
        if d['decision']!='GO': return {'status':'BLOCKED','reason':'RISK_NO_GO','risk':d}
        rid='route-'+uuid.uuid4().hex[:12]
        legs=[Leg(op['buy_venue'],op['symbol'],'BUY',1,op['buy_price']),Leg(op['sell_venue'],op['symbol'],'SELL',1,op['sell_price'])]
        for leg in legs:
            leg.state=OrderState.SENT; leg.state=OrderState.ACK; leg.filled_qty=leg.quantity; leg.avg_price=leg.price; leg.state=OrderState.FILLED
        pnl=round(op['notional_aoa']*op['net_profit_pct']/100,2)
        route=Route(rid,legs,'COMPLETED',pnl_aoa=pnl)
        self.audit('AUTOBOT_ROUTE_COMPLETED',rid)
        return {'status':'COMPLETED','route_id':rid,'pnl_aoa':pnl,'risk':d}
