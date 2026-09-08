class DEXGuard:
    def validate(self, quote):
        checks={
          'wallet_signing': False,
          'quote_fresh': quote.get('quote_age_ms',999999)<=2000,
          'slippage_ok': quote.get('slippage_pct',99)<=1.0,
          'gas_known': quote.get('gas_aoa',None) is not None,
        }
        return {'decision':'GO' if all(checks.values()) else 'NO-GO','checks':checks}
