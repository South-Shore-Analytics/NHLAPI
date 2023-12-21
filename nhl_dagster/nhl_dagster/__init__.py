from dagster import Definitions, load_assets_from_modules
import os
import json 
import base64
from . import assets

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
)