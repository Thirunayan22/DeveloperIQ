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

CONTIRBUTOR_ISSUES_COMMENTS_URI = "https://api.github.com/repos/RasaHQ/rasa/issuescomments"
COLLABORATOR_API_URI = "https://api.github.com/repos/RasaHQ/rasa/contributors"
CONTIRBUTOR_STATS_URI = "https://api.github.com/repos/RasaHQ/rasa/stats/contributors"



@app.get("/contributor/snapshot")
def get_contributer_commit_count(contributor_login:str):
    """
    Gets number of commits made by contributor

    return struct
    ==============

    ## SHOULD BE POSSIBLE TO RETURN BY EACH TIME FRAME (WEEK,DAY,MONTH)

    @:returns
   DICT:{"commits":20,
    "total_contribution": 325}
    """

    contributor_stats = {}
    contributor_commit_stats = requests.request("GET", CONTIRBUTOR_STATS_URI).json()
    print("CONTRIBUTOR COMMIT STATS : ",len(contributor_commit_stats))
    for commit_statistic in contributor_commit_stats:
        if commit_statistic["author"]["login"]  == contributor_login:
            print("commit_statistic : ",commit_statistic)
            contributor_id = commit_statistic["author"]["id"]
            weekly_commit_contribution = commit_statistic["weeks"][-1]
            monthly_commit_contribution = calculate_commit_contribution(commit_statistic["weeks"][-7:])
            yearly_commit_contribution = calculate_commit_contribution(commit_statistic["weeks"][-52:])

            contributor_stats = {
                contributor_login:{
                "contributor_id":contributor_id,
                "weekly_contribution":{
                                        "additions":weekly_commit_contribution["a"],
                                        "deletions":weekly_commit_contribution["d"],
                                        "number_of_commits":weekly_commit_contribution["c"]
                                        },
                "monthly_contribution":monthly_commit_contribution,
                "yearly_contribution":yearly_commit_contribution

            }
            }
            break



## TODO : GET REPOSITORY ISSUES
    contributor_issue_stats =   requests.get()
## TODO : GET REPOSITORY COMMENTS

    return contributor_stats


def calculate_commit_contribution(contribution_lst:List):
    total_additions = 0
    total_deletions = 0
    total_commits   = 0
    for contribution_idx in range(len(contribution_lst)):
            if contribution_idx != 0:
                total_additions += contribution_lst[contribution_idx-1]["a"]
                total_deletions += contribution_lst[contribution_idx-1]["d"]
                total_commits   += contribution_lst[contribution_idx-1]["c"]
    total_contribution = {
                    "additions":total_additions,
                    "deletions":total_deletions,
                    "number_of_commits":total_commits
    }
    return total_contribution



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
