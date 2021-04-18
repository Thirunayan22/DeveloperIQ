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
USER_NAME = "Thirunayan22"
with open("../github-access-token.txt", 'r') as token_file:
    token = token_file.readline()

@app.get("/contributor/snapshot")
def get_contributer_commit_count(repo:str,organization:str,contributor:str):

    """
    Gets number of commits made by contributor

    return struct
    ==============

    ## SHOULD BE POSSIBLE TO RETURN BY EACH TIME FRAME (WEEK,DAY,MONTH)

    @:returns
   DICT:{"commits":20,
    "total_contribution": 325}

    DICT:{
    pull_requests_created : 12,
    issues_created : 13,
    issues_commented_on : 13
    }
    """

    CONTRIBUTOR_ISSUES_COMMENTS_URI = f"https://api.github.com/repos/{organization}/{repo}/issues/comments"
    CONTRIBUTOR_ISSUES_URI = f"https://api.github.com/repos/{organization}/{repo}/issues"
    CONTRIBUTOR_STATS_URI = f"https://api.github.com/repos/{organization}/{repo}/stats/contributors"


    contributor_login = contributor
    contributor_commit_stats = requests.request("GET", CONTRIBUTOR_STATS_URI,auth=('')).json()
    weekly_commit_contribution = {}
    monthly_commit_contribution = {}
    yearly_commit_contribution = {}
    print("CONTRIBUTOR COMMIT STATS : ",len(contributor_commit_stats))
    for commit_statistic in contributor_commit_stats:
        print(commit_statistic)
        if commit_statistic["author"]["login"]  == contributor_login:
            weekly_commit_contribution = commit_statistic["weeks"][-1]
            monthly_commit_contribution = calculate_commit_contribution(commit_statistic["weeks"][-4:])
            yearly_commit_contribution = calculate_commit_contribution(commit_statistic["weeks"][-52:])
            break

    year_since  = str(zulu.parse(datetime.datetime.now() - dateutil.relativedelta.relativedelta(years=1))).split('.')[0]
    week_since  = str(zulu.parse(datetime.datetime.now() - dateutil.relativedelta.relativedelta(weeks=1))).split('.')[0]
    month_since = str(zulu.parse(datetime.datetime.now() - dateutil.relativedelta.relativedelta(weeks=1))).split('.')[0]

    print("WEEK  : " ,week_since)
    print("YEAR  : ",year_since)
    print("MONTH : ",month_since)
    contributor_issue_stats_url_year  = f"{CONTRIBUTOR_ISSUES_URI}?creator={contributor_login}&since={year_since}"
    contributor_issue_stats_url_week  = f"{CONTRIBUTOR_ISSUES_URI}?creator={contributor_login}&since={week_since}"
    contributor_issue_stats_url_month = f"{CONTRIBUTOR_ISSUES_URI}?creator={contributor_login}&since={month_since}"

    num_issues_created_year  = len(requests.request("GET",contributor_issue_stats_url_year,auth=(USER_NAME,token)).json())
    num_issues_created_week  = len(requests.request("GET",contributor_issue_stats_url_week,auth=(USER_NAME,token)).json())
    num_issues_created_month = len(requests.request("GET",contributor_issue_stats_url_month,auth=(USER_NAME,token)).json())

    contributor_comments_url_year = f"{CONTRIBUTOR_ISSUES_COMMENTS_URI}?since={year_since}"
    contributor_comments_url_month = f"{CONTRIBUTOR_ISSUES_COMMENTS_URI}?since={month_since}"
    contributor_comments_url_week = f"{CONTRIBUTOR_ISSUES_COMMENTS_URI}?since={week_since}"

    num_comments_year = len([comment for comment in requests.request("GET",contributor_comments_url_year,auth=(USER_NAME,token)).json() if comment["user"]["login"]==contributor_login])
    num_comments_month = len([comment for comment in requests.request("GET",contributor_comments_url_month,auth=(USER_NAME,token)).json() if comment["user"]["login"]==contributor_login])
    num_comments_week = len([comment for comment in requests.request("GET",contributor_comments_url_week,auth=(USER_NAME,token)).json() if comment["user"]["login"]==contributor_login])
    #DEBUG
    print("DEBUG COMMENTS")
    print(comment for comment in requests.request("GET",contributor_comments_url_week,auth=(USER_NAME,token)).json())
    individual_contributor_metric_stats = {
        "contributor_login" : contributor_login,
        "contribution_stats":{
            "week":{
                "commit_additions":weekly_commit_contribution["a"],
                "commit_deletions":weekly_commit_contribution["d"],
                "num_commits" : weekly_commit_contribution["c"],
                "issues_created": num_issues_created_week,
                "issues_comment_interactions": num_comments_week
            },

            "month":{
                "commit_additions": monthly_commit_contribution["additions"],
                "commit_deletions": monthly_commit_contribution["deletions"],
                "num_commits": monthly_commit_contribution["number_of_commits"],
                "issues_created": num_issues_created_month,
                "issues_comment_interactions": num_comments_month
            },

            "year":{
                "commit_additons": yearly_commit_contribution["additions"],
                "commit_deletions":yearly_commit_contribution["deletions"],
                "num_commits" : yearly_commit_contribution["number_of_commits"],
                "issues_created":num_issues_created_year,
                "issues_comment_interactions":num_comments_year
            }

        }
    }

    return  individual_contributor_metric_stats

@app.get('/contributors')
def get_all_contributors(organization:str,repo:str):


    repository_contributors_url = f"https://api.github.com/repos/{organization}/{repo}/contributors"
    contributors = requests.request("GET",repository_contributors_url,auth=(USER_NAME,token))
    print(contributors)
    return contributors.json()


def calculate_commit_contribution(contribution_lst:List):
    total_additions = 0
    total_deletions = 0
    total_commits   = 0

    for contribution_idx in range(len(contribution_lst)+1):
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


if __name__ == "__main__":
    uvicorn.run("github_data_api:app", host="127.0.0.1", port=8001, reload=True)
