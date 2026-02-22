from flask import Flask, request, jsonify
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()
SNYK_SECRET = os.getenv("SNYK_WEBHOOK_SECRET")

def is_valid_signature(payload_bytes, signature_header):
    """validate HMAC signature from the webhook sender"""
    if not SNYK_SECRET or not signature_header:
        return False

    expected = "sha256="+hmac.new(
    SNYK_SECRET.encode(),
    payload_bytes,
    hashlib.sha256
    ).hexdigest()
    # print("expected:",expected)
    return hmac.compare_digest(expected, signature_header)

def parse_snyk_issues(data):
    """Extract key fields from Snyk-style payload into a simple list of dicts"""
    issues = []

    for issue in data.get("newIssues", []):
        issue_data = issue.get("issueData",{})

        simplified = {
            "id": issue_data.get("id","Unknown"),
            "title": issue_data.get("title","Unknown"),
            "severity": issue_data.get("severity","Unknown"),
            "packget": issue.get("pkgName","Unknown"),
            "versions": ",".join(issue.get("pkgVersions","Unknown")),
            "url": issue.get("issueUrl","Unknown"),
        }
        issues.append(simplified)

    return issues

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return {"status":"ok"},200

@app.route("/webhook", methods=["POST"])
def webhook():
    payload_bytes = request.get_data()
    # TEMP during development
    # print(payload_bytes)
    # signature = request.headers.get("X-Hub-Signature","")

    # if not is_valid_signature(payload_bytes, signature):
    #     return jsonify({"error":"Invalid signature"}), 401

    data = request.get_json()
    parsed_issue = parse_snyk_issues(data)

    print("Parsed issue:", parsed_issue)
    return jsonify({"issues": parsed_issue}), 200

if __name__ == "__main__":
    app.run(port=5000)
