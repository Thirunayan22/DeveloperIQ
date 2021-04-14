import ast
import boto3
import requests
import threading
import json
import decimal
import argparse
import time
from time import sleep
TABLE_NAME = "DeveloperIQ"
PRIMARY_KEY_COLUMN_NAME = "contributor_login"
columns = ["contribution_stats"]


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o)
        if isinstance(o, set):  #<---resolving sets as lists
            return list(o)
        return super(DecimalEncoder, self).default(o)

class DBActions:

    def __init__(self,organization,repository):
        self.organization =  organization
        self.repository   = repository
        self.get_contributors_url = f"http://127.0.0.1:8001/contributors?organization={organization}&repo={repository}"


    def update_cache_db(self,contributor_login:str):

        """
        Compare contributor data from github api and DB, look for changes and if there are any changes update DB with
        live changes in DB
        """


        db = boto3.resource("dynamodb")
        table = db.Table(TABLE_NAME)

        # TODO COMAPARE BOTH ARRAYS
        LIVE_CONTRIBUTOR_SNAPSHOT_URL = f"http://localhost:8001/contributor/snapshot?repo={self.repository}&organization={self.organization}&contributor={contributor_login}"

        try:
            contributor_github_data = requests.request("GET",LIVE_CONTRIBUTOR_SNAPSHOT_URL).json()
            contributor_db_data  = table.get_item(Key={
                PRIMARY_KEY_COLUMN_NAME:contributor_login
            })
            contributor_db_data = ast.literal_eval((json.dumps(contributor_db_data,cls=DecimalEncoder)))

            print("=================== CONTRIBUTOR GITHUB DATA ========================")
            print(contributor_github_data)

            print("==================== CONTRIBUTOR DB DATA ==========================")
            if 'Item' in contributor_db_data:
                print(contributor_db_data['Item'])
            else:
                print("CONTRIBUTOR NOT PRESENT IN DATABASE")

            if 'Item' in contributor_db_data:
                if contributor_db_data['Item'] == contributor_github_data:
                    print(f"NO CHANGE FOR USER {contributor_login}")
                    return contributor_db_data['ResponseMetadata']['HTTPStatusCode']
                else:
                    print("\nCHANGE PRESENT...INITIATING DB UPDATE......\n")
                    push_contributor_response = self.push_contributor_data_db(table,contributor_login,payload=contributor_github_data['contribution_stats'])
                    return push_contributor_response
            else:
                print("CONTRIBUTOR NOT PRESENT IN CACHING DATABASE\n")
                print("UPDATING DB\n")
                push_contributor_response = self.push_contributor_data_db(table,contributor_login,payload=contributor_github_data['contribution_stats'])
                return push_contributor_response

        except Exception as e:
            print("EXCEPTION OCCURED : ",e)


    def push_contributor_data_db(self,table,contributor_login,payload):
        response = table.put_item(
            Item = {
                PRIMARY_KEY_COLUMN_NAME:contributor_login,
                columns[0]:payload
            }
        )

        return  response['ResponseMetadata']['HTTPStatusCode']

    def update_all_contributors(self,delay):
        while True:

            contributors = requests.request("GET",self.get_contributors_url).json()
            print("CONTRIBUTORS : ",contributors)
            for contributor in contributors:
                try:
                    contributor_login = contributor['login']
                    print("INDEXING CONTRIBUTOR : " , contributor_login)
                    response = self.update_cache_db(contributor_login)
                except Exception as e:
                    print("EXCEPTION OCCURED WHEN UPDATING ALL CONTRIBUTORS : ",e)
                    print("CONTRIBUTOR DATA",contributor)
                    continue
                sleep(delay)
            sleep(secs=432000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Take in input")
    parser.add_argument('--org',type=str,required=True)
    parser.add_argument('--repo',type=str,required=True)
    parser.add_argument('--delay',type=int,required=False)
    parser.add_argument('--login',type=str,required=False)

    args = parser.parse_args()

    organization = args.org
    repository   = args.repo
    contributor_login = args.login
    delay  = int(args.delay)

    db_actions = DBActions(organization,repository)
    response = db_actions.update_all_contributors(delay)
    # response = db_actions.update_cache_db(contributor_login)
    print(f"\n RESPONSE : {response}")

# TODO ADD NGROK TUNNEL IF THERE IS NO OTHER FIX FOR THE API THRESHOLD LIMIT
# TODO ADD CODE TO CHECK DATABASE FOR IF THE USER EXISTS IN THE DATABASE AND THEN ADD FIRST METRICS OF NEW USERS
# TODO THEN ADD UPDATES TO METRICS OF OLD USERS
