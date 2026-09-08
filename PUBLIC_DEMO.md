# Public Demo Deployment

ArbDask is configured for a public, read-only/demo deployment by default.

Safety defaults:
- TRADING_MODE=paper
- LIVE_TRADING_ENABLED=false
- PUBLIC_DEMO_MODE=true
- No exchange credentials are required for the public demo.

For Render:
1. Push this repository to GitHub.
2. In Render, create a New Web Service from the repository.
3. Select Docker runtime.
4. Set health check to `/api/health`.
5. Keep the safety environment variables above.
6. Deploy.

Do not add real exchange API keys to a public demo. Testnet/Demo credentials should only be added to a private deployment after authentication and secret-management are configured.
