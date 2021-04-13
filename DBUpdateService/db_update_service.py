import ast
import boto3
import requests
import threading
import json
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o)
        if isinstance(o, set):  #<---resolving sets as lists
            return list(o)
        return super(DecimalEncoder, self).default(o)



def update_cache_db(repo:str,organization:str):

    """
    Compare contributor data from github api and DB, look for changes and if there are any changes update DB with
    live changes in DB
    """
    TABLE_NAME = "DeveloperIQ"
    PRIMARY_KEY_COLUMN_NAME = "contributor_login"
    REPO_CONTRIBUTORS_URL = f"https://api.github.com/repos/{organization}/{repo}/contributors"

    db = boto3.resource("dynamodb")
    table = db.Table(TABLE_NAME)

    contributors = requests.request("GET",REPO_CONTRIBUTORS_URL).json()
    for contributor in contributors:
        contributor_login = contributor["login"]
        LIVE_CONTRIBUTOR_SNAPSHOT_URL = f"http://localhost:8001/contributor/snapshot?repo={repo}&organization={organization}&contributor={contributor_login}"

        try:
            contributor_github_data = requests.request("GET",LIVE_CONTRIBUTOR_SNAPSHOT_URL).json()
            contributor_db_data  = table.get_item(Key={
                PRIMARY_KEY_COLUMN_NAME:contributor_login
            })
        except Exception as e:
            print("EXCEPTION OCCURED : ",e)



