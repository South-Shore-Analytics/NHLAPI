from dagster import Definitions, load_assets_from_modules
import os
import json 
import base64
from . import assets

def safe_b64decode(s):
    # Add necessary padding
    padding = 4 - len(s) % 4
    if padding < 4:
        s += "=" * padding
    return base64.b64decode(s)

AUTH_FILE = "/tmp/gcp_creds.json"

# Retrieve the environment variable
encoded_credentials = os.getenv("CREDENTIALS_JSON")

if encoded_credentials:
    decoded_credentials = safe_b64decode(encoded_credentials)
    with open(AUTH_FILE, "w") as f:
        json.dump(json.loads(decoded_credentials), f)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = AUTH_FILE
else:
    print("No CREDENTIALS_JSON environment variable found.")

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
)