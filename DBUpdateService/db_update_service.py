import ast
import boto3
import requests
import json
import decimal
import argparse
from time import sleep

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
        self.TABLE_NAME = "DeveloperIQ"
        self.PRIMARY_KEY_COLUMN_NAME = "contributor_login"
        self.columns = ["contributor_stats"]
        self.db = boto3.resource("dynamodb")
        self.table = self.db.Table(self.TABLE_NAME)

    def update_cache_db(self,contributor_login:str):

        """
        Compare contributor data from github api and DB, look for changes and if there are any changes update DB with
        live changes in DB
        """



        LIVE_CONTRIBUTOR_SNAPSHOT_URL = f"http://localhost:8001/contributor/snapshot?repo={self.repository}&organization={self.organization}&contributor={contributor_login}"

        try:
            contributor_github_data = requests.request("GET",LIVE_CONTRIBUTOR_SNAPSHOT_URL).json()
            contributor_db_data  = self.table.get_item(Key={
                self.PRIMARY_KEY_COLUMN_NAME:contributor_login
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
                    push_contributor_response = self.push_contributor_data_db(self.table,contributor_login,payload=contributor_github_data['contribution_stats'])
                    return push_contributor_response
            else:
                print("CONTRIBUTOR NOT PRESENT IN CACHING DATABASE\n")
                print("UPDATING DB\n")
                push_contributor_response = self.push_contributor_data_db(self.table,contributor_login,payload=contributor_github_data['contribution_stats'])
                return push_contributor_response

        except Exception as e:
            print("EXCEPTION OCCURED : ",e)


    def push_contributor_data_db(self,table,contributor_login,payload):
        response = table.put_item(
            Item = {
                self.PRIMARY_KEY_COLUMN_NAME:contributor_login,
                self.columns[0]:payload
            }
        )

        return  response['ResponseMetadata']['HTTPStatusCode']

    def get_contributor_data_db(self,contributor_login):
        response = self.table.get_item(
            Key = {
                self.PRIMARY_KEY_COLUMN_NAME:contributor_login
            }
        )

        return response

    def get_all_contributor_data(self):
        response = self.table.scan()
        return response

    def update_all_contributors(self,delay):
        while True:

            contributors = requests.request("GET",self.get_contributors_url).json()
            contributors_db = [db_contributor_name["contributor_login"] for db_contributor_name in self.get_all_contributor_data()["Items"]]
            print(contributors)
            uncached_contributors = [contributor["login"] for contributor in contributors if contributor["login"] not in contributors_db ]
            cached_contributors = [contributor["login"] for contributor in contributors if contributor["login"] in contributors_db]

            print(f"UNCACHED CONTRIBUTORS : {uncached_contributors}")
            print(f"CACHED CONTRIBUTORS : {cached_contributors}")


            print("UPDATING NEW CONTRIBUTORS TO DB...\n")
            for uncached_contributor in uncached_contributors:
                print(f"INDEXING CONTRIBUTOR : {uncached_contributor}")
                try:
                    uncached_update = self.update_cache_db(uncached_contributor)
                    sleep(delay)
                    print(uncached_update)
                except Exception as e:
                    print("EXCEPTION OCCURED WHEN UPDATING NEW CONTRIBUTOR : " ,uncached_contributor)
                    print("RAW EXCEPTION : ",e)
                    with open("error_logs_v2.txt","w+") as log:
                        log.writelines(f"EXCEPTION {e}")

                    continue


            sleep(3600)
            print("UPDATING EXISTING CONRIBUTOR DATA TO DB...")
            for cached_contributor in cached_contributors:
                try:
                   cached_update = self.update_cache_db(cached_contributor)
                   sleep(delay)

                except Exception as e:
                    print(f"EXCEPTION OCCURED WHEN UPDATING EXSITING CONTRIBUTOR : {cached_contributor}")
                    print("RAW EXCEPTION : ",e)
                    continue
            sleep(secs=432000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Take in input")
    parser.add_argument('--org',type=str,required=True)
    parser.add_argument('--repo',type=str,required=True)
    parser.add_argument('--delay',type=int,default=10,required=False)

    args = parser.parse_args()

    organization = args.org
    repository   = args.repo
    delay  = int(args.delay)

    db_actions = DBActions(organization,repository)
    response = db_actions.update_all_contributors(delay)
    print(f"\n RESPONSE : {response}")

# TODO ADD NGROK TUNNEL IF THERE IS NO OTHER FIX FOR THE API THRESHOLD LIMIT
# TODO ADD CODE TO CHECK DATABASE FOR IF THE USER EXISTS IN THE DATABASE AND THEN ADD FIRST METRICS OF NEW USERS
# TODO THEN ADD UPDATES TO METRICS OF OLD USERS
