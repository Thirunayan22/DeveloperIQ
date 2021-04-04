import os
import json
import fastapi
from typing import List,Optional,Set,Dict
from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

# TODO: Change code to not include contributor name in every decorated parameter call
class ContributorInfo(BaseModel):
    contributor_name: str
    pull_requests: str
    time_frame: str


@app.post("/{contributer_name}/commits")
async def get_contributer_commits(time_frame:str,contributor_name:str,additions:bool,deletions:bool):
    """"Gets number of commits made by contributor"""
    pass


@app.post("/{contributor_name}/pull-requests")
async def get_contributor_pull_requests(contributor_name:str,created:bool,reviewed:bool):
    """" Return Pull Requests from contributor """

@app.post("/{contributor_name}/issue")
async def get_contributor_issues(contributor_name:str,created:bool,resolved:bool):
    """" Return issues created by contributer and issues resolved """

