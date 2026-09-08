from dataclasses import dataclass, field
from enum import Enum
import time, uuid

class OrderState(str, Enum):
    CREATED='CREATED'; SENT='SENT'; ACK='ACK'; PARTIAL='PARTIAL'; FILLED='FILLED'; FAILED='FAILED'; STOPPED='STOPPED'; REVIEW='REVIEW'

@dataclass
class Leg:
    venue:str; symbol:str; side:str; quantity:float; price:float
    client_order_id:str=field(default_factory=lambda:'arb-'+uuid.uuid4().hex[:20])
    state:OrderState=OrderState.CREATED; filled_qty:float=0; avg_price:float=0

@dataclass
class Route:
    route_id:str; legs:list[Leg]; created_at:float=field(default_factory=time.time)
    status:str='RUNNING'; pnl_aoa:float=0; reason:str=''

class CircuitBreaker:
    def __init__(self,max_failures=3): self.max_failures=max_failures; self.failures=0; self.tripped=False
    def failure(self):
        self.failures+=1
        if self.failures>=self.max_failures:self.tripped=True
    def reset(self): self.failures=0; self.tripped=False

class RiskEngine:
    def __init__(self,min_profit=0.5,max_notional=500000,max_slippage=0.5,max_age_ms=1500):
        self.min_profit=min_profit; self.max_notional=max_notional; self.max_slippage=max_slippage; self.max_age_ms=max_age_ms
    def evaluate(self,op):
        checks={
          'net_profit': op['net_profit_pct']>=self.min_profit,
          'notional': op['notional_aoa']<=self.max_notional,
          'slippage': op.get('slippage_pct',0)<=self.max_slippage,
          'quote_age': op.get('quote_age_ms',0)<=self.max_age_ms,
          'liquidity': op.get('liquidity_ok',True),
        }
        return {'decision':'GO' if all(checks.values()) else 'NO-GO','checks':checks}
