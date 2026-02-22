import hmac
import hashlib, json
from dotenv import load_dotenv
import os

load_dotenv()
secret = os.getenv("SNYK_WEBHOOK_SECRET")
filename = "payload.json"

with open(filename, "r", encoding="utf-8") as f:
    data = json.load(f)    

body_str = json.dumps(data, separators=(",", ":"))  # minified
body = body_str.encode("utf-8")
print("SCRIPT body bytes:", body)

digest=hmac.new(
    secret.encode(),
    body,
    hashlib.sha256
).hexdigest()

signature = "sha256=" + digest
print("Signature header value:")
print(signature)