import os
import urllib.request
import json
from flask import Flask, send_from_directory, jsonify, request

app = Flask(__name__, static_folder="public")

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

@app.route("/")
def index():
    return send_from_directory(PUBLIC_DIR, "index.html")

@app.route("/sw.js")
def service_worker():
    response = send_from_directory(PUBLIC_DIR, "sw.js")
    response.headers["Content-Type"] = "application/javascript"
    response.headers["Service-Worker-Allowed"] = "/"
    return response

@app.route("/manifest.json")
def manifest():
    response = send_from_directory(PUBLIC_DIR, "manifest.json")
    response.headers["Content-Type"] = "application/manifest+json"
    return response

@app.route("/tonconnect-manifest.json")
def tonconnect_manifest():
    response = send_from_directory(PUBLIC_DIR, "tonconnect-manifest.json")
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(PUBLIC_DIR, filename)

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "app": "BorderP45"}), 200

@app.route("/api/transfer/ton", methods=["POST"])
def transfer_ton():
    data = request.get_json(silent=True) or {}
    recipient = data.get("recipient")
    amount = data.get("amount")
    comment = data.get("comment", "")

    if not recipient or not amount:
        return jsonify({"success": False, "error": "Recipient and amount are required"}), 400

    return jsonify({
        "success": True,
        "message": "TON transfer simulated successfully",
        "tx_hash": "ton_sim_tx_" + os.urandom(8).hex(),
        "recipient": recipient,
        "amount": amount,
        "comment": comment
    }), 200

@app.route("/api/transfer/jetton", methods=["POST"])
def transfer_jetton():
    data = request.get_json(silent=True) or {}
    jetton_master = data.get("jetton_master")
    recipient = data.get("recipient")
    amount = data.get("amount")
    comment = data.get("comment", "")

    if not recipient or not amount or not jetton_master:
        return jsonify({"success": False, "error": "Jetton master, recipient, and amount are required"}), 400

    return jsonify({
        "success": True,
        "message": "Jetton transfer simulated successfully",
        "tx_hash": "jetton_sim_tx_" + os.urandom(8).hex(),
        "jetton_master": jetton_master,
        "recipient": recipient,
        "amount": amount,
        "comment": comment
    }), 200

@app.route("/api/ton/account/<address>", methods=["GET"])
def get_ton_account(address):
    # Try querying TonAPI if TONAPI_KEY is available or fallback to local data/simulation
    tonapi_key = os.getenv("TONAPI_KEY")
    if tonapi_key:
        try:
            req = urllib.request.Request(
                f"https://tonapi.io/v2/accounts/{address}",
                headers={"Authorization": f"Bearer {tonapi_key}"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                balance_nano = int(data.get("balance", 0))
                return jsonify({
                    "success": True,
                    "address": address,
                    "balance": f"{balance_nano / 1e9:.4f}",
                    "raw_balance": str(balance_nano),
                    "status": data.get("status", "active")
                }), 200
        except Exception:
            pass

    return jsonify({
        "success": True,
        "address": address,
        "balance": "12.4500",
        "raw_balance": "12450000000",
        "status": "active"
    }), 200

@app.route("/api/ton/transactions/<address>", methods=["GET"])
def get_ton_transactions(address):
    tonapi_key = os.getenv("TONAPI_KEY")
    if tonapi_key:
        try:
            req = urllib.request.Request(
                f"https://tonapi.io/v2/blockchain/accounts/{address}/transactions?limit=10",
                headers={"Authorization": f"Bearer {tonapi_key}"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                txs = []
                for tx in data.get("transactions", []):
                    txs.append({
                        "hash": tx.get("hash"),
                        "type": "transaction",
                        "utime": tx.get("utime")
                    })
                return jsonify({
                    "success": True,
                    "address": address,
                    "transactions": txs
                }), 200
        except Exception:
            pass

    return jsonify({
        "success": True,
        "address": address,
        "transactions": [
            {
                "hash": "tx_sim_9876543210abcdef",
                "type": "received",
                "amount": "+5.0 TON",
                "sender": "EQBvW8Z5huBkMJYxFfLFrNuA-a0g6mZ2c-0123456789abcd",
                "timestamp": "2026-10-01 14:20:00"
            },
            {
                "hash": "tx_sim_1234567890fedcba",
                "type": "sent",
                "amount": "-1.2 TON",
                "recipient": "EQC1234567890abcdef1234567890abcdef1234567890",
                "timestamp": "2026-09-29 09:15:00"
            }
        ]
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
