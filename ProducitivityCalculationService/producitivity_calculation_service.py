"""
This service would perform the calculation for the productivity metric for every developer and rank the developers
based on the score and would return the results to the client
"""
import logging
from typing import List,Dict,Optional,Set
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import requests
import boto3
from boto3.dynamodb.conditions import Key


app = FastAPI()

table_name = "DeveloperIQ"
primary_key_column_name = "contributor_login"
columns = ["contribution_stats"]
client  = boto3.client('dynamodb')
DB = boto3.resource('dynamodb')
table = DB.Table(table_name)



@app.get("/contributor-productivity")
def get_contributor_productivitiy_calculation(contributor_login:str):
    contributor_metrics_raw_response = table.get_item(
        Key={
            primary_key_column_name:contributor_login
        }
    )

    return contributor_metrics_raw_response['Item']


if __name__ == "__main__":
    uvicorn.run("producitivity_calculation_service:app",host="127.0.0.1",port=8002,reload=True)