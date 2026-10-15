import os
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

@app.route("/api/tonconnect/parse", methods=["POST", "GET"])
def parse_tonconnect_endpoint():
    import json
    from urllib.parse import urlparse, parse_qs

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        url = data.get("url", "")
    else:
        url = request.args.get("url", "")

    if not url:
        return jsonify({"success": False, "error": "URL parameter is required"}), 400

    try:
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)

        version = params.get("v", [""])[0]
        client_id = params.get("id", [""])[0]
        trace_id = params.get("trace_id", [""])[0]
        return_url = params.get("ret", [""])[0]
        raw_r = params.get("r", [""])[0]
        ton_address = params.get("ton", [""])[0]

        manifest_url = ""
        items = []
        if raw_r:
            try:
                request_data = json.loads(raw_r)
                manifest_url = request_data.get("manifestUrl", "")
                items = request_data.get("items", [])
            except Exception as e:
                return jsonify({"success": False, "error": f"Failed to parse 'r' parameter payload: {str(e)}"}), 400

        return jsonify({
            "success": True,
            "parsed": {
                "version": version,
                "id": client_id,
                "trace_id": trace_id,
                "return_url": return_url,
                "manifest_url": manifest_url,
                "items": items,
                "ton_address": ton_address,
                "host": parsed_url.netloc,
                "scheme": parsed_url.scheme
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Invalid endpoint URL: {str(e)}"}), 400

@app.route("/api/tonconnect/connect", methods=["POST"])
def connect_tonconnect():
    data = request.get_json(silent=True) or {}
    client_id = data.get("id")
    wallet_address = data.get("wallet_address", "EQD_simulated_wallet_address_12345")
    manifest_url = data.get("manifest_url", "")

    if not client_id:
        return jsonify({"success": False, "error": "Client ID (id) is required"}), 400

    session_id = "tc_session_" + os.urandom(8).hex()

    return jsonify({
        "success": True,
        "message": "TON Connect session established successfully",
        "session_id": session_id,
        "client_id": client_id,
        "wallet_address": wallet_address,
        "manifest_url": manifest_url,
        "status": "connected"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
