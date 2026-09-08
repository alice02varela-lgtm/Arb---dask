# ArbDask v3.2 — Production Candidate

ArbDask is a crypto-arbitrage control plane with Paper Trading, Binance Spot Testnet and OKX Demo connectors.

## Safety defaults
- `TRADING_MODE=paper`
- `LIVE_TRADING_ENABLED=false` (hard-gated in this candidate)
- No withdrawals
- API credentials are read only from local environment variables; never from the frontend.
- Emergency Stop and Circuit Breaker are enabled.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Open `http://localhost:8000`.

## Test
```bash
pytest -q
```

## Test environments
Binance Spot Testnet is API-only and uses virtual assets. OKX Demo Trading is simulated and uses virtual balances. Configure your own test credentials locally when you are ready; do not paste keys into chat.

## Important
This package is a production candidate, not a claim that live-money trading is safe or ready. Before live use, perform authenticated Testnet/Demo E2E tests, security review, exchange filter validation, failure-injection tests, reconciliation tests and deployment hardening.
