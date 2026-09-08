import os, uuid, hashlib, hmac, base64, json, time
from dataclasses import dataclass

@dataclass
class Result:
    ok:bool; venue:str; order_id:str|None; status:str; message:str; raw:dict|None=None

class BaseConnector:
    venue='BASE'
    def health(self): return {'venue':self.venue,'enabled':False,'mode':'paper'}

class BinanceTestnet(BaseConnector):
    venue='BINANCE_TESTNET'
    def __init__(self): self.enabled=os.getenv('BINANCE_TESTNET_ENABLED','false').lower()=='true'; self.base='https://testnet.binance.vision/api'
    def health(self): return {'venue':self.venue,'enabled':self.enabled,'mode':'testnet','base_url':self.base}
    def place_order(self,*args,**kwargs): return Result(False,self.venue,None,'NOT_CONNECTED','Authenticated execution is gated; configure local credentials first.')

class OKXDemo(BaseConnector):
    venue='OKX_DEMO'
    def __init__(self): self.enabled=os.getenv('OKX_DEMO_ENABLED','false').lower()=='true'; self.base=os.getenv('OKX_DEMO_BASE_URL','https://eea.okx.com')
    def health(self): return {'venue':self.venue,'enabled':self.enabled,'mode':'demo','base_url':self.base}
    def place_order(self,*args,**kwargs): return Result(False,self.venue,None,'NOT_CONNECTED','Authenticated execution is gated; configure local credentials first.')
