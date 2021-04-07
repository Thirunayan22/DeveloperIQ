import os
import json
import fastapi
from typing import List, Optional, Set, Dict
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uvicorn
import zulu
import random
import datetime
import dateutil
import dateutil.relativedelta

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
CONTRIBUTOR_ISSUES_API_URI = "https://api.github.com/repos/RasaHQ/rasa/issues"
COLLABORATOR_API_URI = "https://api.github.com/repos/RasaHQ/rasa/contributors"


# TODO: Change code to not include contributor name in every decorated parameter call
# Contributor Attributes
class ContributorAttr(BaseModel):
    contributor_login: str
    time_frame: str  # "monthly","weekly","daily"


@app.post("/contributor/snapshot")
def get_contributer_commit_count(contributor: ContributorAttr, time_frame: str):
    """
    Gets number of commits made by contributor

    return struct
    ==============

    ## SHOULD BE POSSIBLE TO RETURN BY EACH TIME FRAME (WEEK,DAY,MONTH)

    @:returns
   DICT:{"commits":20,
    "total_contribution": 325}
    """
    since = None
    commit_info = {}
    if time_frame == "year":
        since = str(zulu.parse(datetime.datetime.now() - dateutil.relativedelta.relativedelta(years=1))).split('.')[0]
    elif time_frame == "month":
        since = str(zulu.parse(datetime.datetime.now() - dateutil.relativedelta.relativedelta(months=1))).split('.')[0]
    elif time_frame == "day":
        since = str(zulu.parse(datetime.datetime.now() - dateutil.relativedelta.relativedelta(days=1))).split('.')[0]
    elif time_frame == "week":
        since = str(zulu.parse(datetime.datetime.now() - dateutil.relativedelta.relativedelta(weeks=1))).split('.')[0]

    contributor_login = contributor.contributor_login
    url = f"{CONTRIBUTOR_COMMITS_API_URI}?author={contributor_login}&since={since}"
    print(since)
    raw_contributor_commits = requests.request("GET", url).json()
    print(raw_contributor_commits)
    commit_info["contributor_login"] = contributor_login
    commit_info["contributor_username"] = raw_contributor_commits[0]["commit"]["author"]["name"]
    commit_info["num_commits"] = len(raw_contributor_commits)
    commit_info["time_frame"] = time_frame
    commit_info["commit_additions"] = 0
    commit_info["commit_deletions"] = 0

    for commit_idx in range(len(raw_contributor_commits)):
        curr_commit = raw_contributor_commits[commit_idx]
        commit_ref = curr_commit["sha"]
        commit_request_url = f"{CONTRIBUTOR_COMMITS_API_URI}/{commit_ref}"
        commit_info_request = requests.request("GET",commit_request_url).json()
        print(commit_info_request)
        commit_additions = commit_info_request["stats"]["additions"]
        commit_deletions = commit_info_request["stats"]["deletions"]

        commit_info["commit_additions"] += commit_additions
        commit_info["commit_deletions"] += commit_deletions

    return commit_info


@app.post("/{contributor_login}/pull-requests")
async def get_contributor_pull_requests(contributor_name: str, created: bool, reviewed: bool):
    """" Return Pull Requests from contributor """
    # TODO : ADD RETURN FORMAT
    return "reponse:200"


@app.post("/{contributor_login}/issue")
async def get_contributor_issues(contributor_name: str, created: bool, resolved: bool):
    """" Return issues created by contributer and issues resolved """
    # TODO : ADD RETURN FORMAT

    return "response:200"


if __name__ == "__main__":
    uvicorn.run("github_data_api:app", host="127.0.0.1", port=8001, reload=True)
