from dagster import Definitions, load_assets_from_modules

from . import assets

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
)

import os
import json 
import base64

AUTH_FILE = "/tmp/gcp_creds.json"
with open(AUTH_FILE, "w") as f:
    json.dump(json.loads(base64.b64decode(os.getenv("CREDENTIALS_JSON"))), f)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = AUTH_FILE