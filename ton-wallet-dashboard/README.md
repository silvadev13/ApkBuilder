# Simple TON Wallet Dashboard

This uses TON Connect UI for the wallet connection.

## Deploy
1. Upload these files to an HTTPS web host.
2. Replace `YOUR-DOMAIN.example` in `tonconnect-manifest.json` with the real HTTPS domain.
3. Add a 180x180 PNG named `icon-180.png`.
4. Open the deployed site and tap **Connect Wallet**.
5. Select Tonkeeper and approve the connection in the wallet.

No seed phrase or private key is requested by this dashboard.

The dashboard currently displays the connected address. A TON blockchain/indexer API can be added next for live balance and transaction history.
