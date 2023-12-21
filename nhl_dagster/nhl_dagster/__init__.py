from dagster import Definitions, load_assets_from_modules, asset, define_asset_job, ScheduleDefinition
import os
import json 
import base64
from . import assets

all_assets = load_assets_from_modules([assets])
all_assets_job = define_asset_job(name="all_assets_job",selection=all_assets)
basic_schedule = ScheduleDefinition(job=all_assets_job, cron_schedule="0 7 * * *", execution_timezone="US/Central")

defs = Definitions(
    assets=all_assets,
    jobs=[all_assets_job],
    schedules=[basic_schedule]
)