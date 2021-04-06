import os
import json
import fastapi
from typing import List,Optional,Set,Dict
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uvicorn
import zulu
import random
from datetime import datetime
"""
For a given username this API should be able to return all information needed for the calculation of the metric for 
every user
"""

app = FastAPI()
######
# STEPS
# TODO FIRST  : SORT BY DATE DEPENDING ON TIME FRAME SELECTED (Monthly,Weekly,Daily)

# TODO SECOND : EXTRACT ONLY COMMIT INFORMATION ABOUT INDIVIDUAL CONTRIBUTOR IN THEIR
#  NUMBER OF COMMITS WITHIN THE TIME FRAME, AMOUNT ADDITION, PULL REQUESTS CREATED, PULL REQUESTS REVIEWED AND ACCEPTED ,
#  ISSUES CREATED

# TODO THIRD  : UPDATE THIS INFORMATION USING A WEBHOOK CREATED ON THE GITHUB REPO ###
# TODO FOURTH : UPDATE DATABASE FROM THE API (THIS CAN BE ANOTHER SERVICE)
#

#######
CONTRIBUTOR_COMMITS_API_URI = "https://api.github.com/repos/RasaHQ/rasa/commits"
CONTRIBUTOR_PULL_REQUESTS_API_URI = "https://api.github.com/repos/RasaHQ/rasa/pulls"
CONTRIBUTOR_ISSUES_API_URI ="https://api.github.com/repos/RasaHQ/rasa/issues"
COLLABORATOR_API_URI = "https://api.github.com/repos/RasaHQ/rasa/contributors"


# TODO: Change code to not include contributor name in every decorated parameter call
# Contributor Attributes
class ContributorAttr(BaseModel):
    contributor_name: str
    time_frame: str   # "monthly","weekly","daily"

@app.post("/contributor/commits")
async def get_contributer_commit_count(contributor:ContributorAttr,time_frame:str):
    """
    Gets number of commits made by contributor

    return struct
    ==============

    ## SHOULD BE POSSIBLE TO RETURN BY EACH TIME FRAME (WEEK,DAY,MONTH)
    contributor_name:{
    "commits":20,
    "additions": 325
    }

    """
    # time_frame       = contributor.time_frame
    #TODO FILTER BY TIME RANGE
    # GET TOTAL NUMBER OF ADDITIONS BY QUERYING FOR THE SPECIFIC COMMIT
    # (https://docs.github.com/en/rest/reference/repos#get-a-commit)

##Sort by commits per day , commits per week

    # commits_per_day = {}
    # prev_date  = 0
    # temp_num_commit = 0
    since = None
    present_time = zulu.now().isoformat().split(".")[0]
    if time_frame == "year":
        since = f"{int(present_time.split('-')[0])-1}-{present_time.split('-')[1]}-{present_time.split('-')[2]}"
    elif time_frame == "month":
        since = f"{present_time.split('-')[0]}-{int(present_time.split('-')[1])-1}-{present_time.split('-')[2]}"
    elif time_frame == "day":
        since = f"{present_time.split('-')[0]}-{present_time.split('-')[1]}-{int(present_time.split('-')[2].split('T')[0])-1}T{present_time.split('-')[2].split('T')[1]}"
    print(since)
    contributor_name = contributor.contributor_name
    url = f"{CONTRIBUTOR_COMMITS_API_URI}?author={contributor_name}&since={since}"
    raw_contributor_commits =  requests.request("GET",url).json()



    # for commit_idx in range(len(raw_contributor_commits)):
    #     current_commit = raw_contributor_commits[commit_idx]
    #
    #     commit_time_stamp = current_commit["commit"]["committer"]["date"]
    #     # commit_message = current_commit["commit"]["message"] : OPTIONAL
    #     commit_date = str(zulu.parse(commit_time_stamp).datetime.date())
    #     if commit_date != prev_date:
    #         temp_num_commit = 1
    #         commits_per_day[commit_date] = temp_num_commit
    #     else:
    #         temp_num_commit += 1
    #         commits_per_day[commit_date] = temp_num_commit
    #     prev_date = commit_date

    return raw_contributor_commits


@app.post("/{contributor_name}/pull-requests")
async def get_contributor_pull_requests(contributor_name:str,created:bool,reviewed:bool):
    """" Return Pull Requests from contributor """
    #TODO : ADD RETURN FORMAT
    return "reponse:200"

@app.post("/{contributor_name}/issue")
async def get_contributor_issues(contributor_name:str,created:bool,resolved:bool):
    """" Return issues created by contributer and issues resolved """
    #TODO : ADD RETURN FORMAT

    return "response:200"

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8001)
