import json
import pandas as pd
import requests
from google.cloud import bigquery
from dagster import AssetExecutionContext, MetadataValue, asset, Output, EnvVar
import os
import base64

# Google Cloud Configurations
PROJECT_ID = 'nhl-api-408121'
DATASET_NAME = 'raw_api_data'
bigquery_creds=EnvVar("CREDENTIALS_JSON")

# Initialize clients for BigQuery and Cloud Storage
bigquery_client = bigquery.Client.from_service_account_json(bigquery_creds)

BASE_URL = "https://api-web.nhle.com"

def extract_players(players, position):
    """Extracts player data and returns a list of dictionaries."""
    player_list = []
    for player in players:
        player_data = {
            'id': player.get('id', None),
            'headshot': player.get('headshot', None),
            'firstName': player.get('firstName', {}).get('default', None),
            'lastName': player.get('lastName', {}).get('default', None),
            'sweaterNumber': player.get('sweaterNumber', None),
            'positionCode': player.get('positionCode', None),
            'shootsCatches': player.get('shootsCatches', None),
            'heightInInches': player.get('heightInInches', None),
            'weightInPounds': player.get('weightInPounds', None),
            'birthDate': player.get('birthDate', None),
            'birthCity': player.get('birthCity', {}).get('default', None),
            'birthCountry': player.get('birthCountry', None),
            'teamPosition': position  # forwards, defensemen, or goalies
        }
        player_list.append(player_data)
    return player_list

@asset
def get_all_teams():
    """Returns a list of all teams and their standings."""
    response = requests.get(BASE_URL + "/v1/standings/now")
    teams = response.json()['standings']
    teams_df = pd.DataFrame(teams)
    teams_df.head()
    # Saving to BigQuery
    table_id = f"{PROJECT_ID}.{DATASET_NAME}.current_standings"
    # Define the job configuration
    job_config = bigquery.LoadJobConfig()
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

    job = bigquery_client.load_table_from_dataframe(teams_df, table_id, job_config=job_config)
    job.result()  # Wait for the job to completes
    return teams

@asset
def get_team_roster():
    """Returns a table of all current rosters of all NHL teams."""
    all_teams_roster = []  # List to accumulate all teams' rosters

    for team in get_all_teams():
        team_id = team['teamAbbrev']['default']
        response = requests.get(f"{BASE_URL}/v1/roster/{team_id}/current")
        response_data = response.json()

        # Extract data for each category
        forwards = extract_players(response_data['forwards'], 'forward')
        defensemen = extract_players(response_data['defensemen'], 'defenseman')
        goalies = extract_players(response_data['goalies'], 'goalie')

        # Append to the accumulator list
        all_teams_roster.extend(forwards + defensemen + goalies)

    # Convert the accumulated list into a DataFrame
    roster_df = pd.DataFrame(all_teams_roster)

    # Saving to BigQuery
    table_id = f"{PROJECT_ID}.{DATASET_NAME}.rosters"

    # Define the job configuration
    job_config = bigquery.LoadJobConfig()
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

# Load the DataFrame to BigQuery, replacing the table if it already exists
    job = bigquery_client.load_table_from_dataframe(roster_df, table_id, job_config=job_config)
    job.result()  # Wait for the job to complete

    return roster_df  # Return the complete DataFrame

@asset
def hello():
    """Returns a table of all current rosters of all NHL teams."""
    hello = 'hello world'

    return hello  # Return the complete DataFrame