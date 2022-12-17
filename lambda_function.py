import boto3
import os

import json

from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch
from elasticsearch import RequestsHttpConnection
from elasticsearch import helpers

HOST = os.environ.get('ES_HOST')
INDEX = os.environ.get('ES_INDEX')
S3_BUCKET = os.environ.get('S3_BUCKET')

def get_es():

    session = boto3.Session()
    creds = session.get_credentials().get_frozen_credentials()
    credentials = session.get_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key
    session_token = credentials.token

    awsauth = AWSRequestsAuth(
        aws_access_key=access_key,
        aws_secret_access_key=secret_key,
        aws_token=session_token,
        aws_host=HOST,
        aws_region=session.region_name,
        aws_service='es'
    )

    return Elasticsearch(
        hosts=[{'host': HOST, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

def pushBatch(actions):
    elasticsearch = get_es()
    print('Pushing batch of: ' + str(len(actions)) + ' to ES')
    (success, failed) = helpers.bulk(elasticsearch, actions, stats_only=True)
    print('Batch successfully pushed to elasticsearch')


def lambda_handler(event, context):

    records = event['Records']
    actions = []
    ignoredRecordCount = 0
    s3 = boto3.client('s3')
    for record in records:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj['Body'].read()
        body = json.loads(body.decode('utf-8'))
        data = body.get('data')
        for item in data:
            actions.append(
                {
                    '_index': INDEX,
                    '_id': item['id'],
                    '_source': item,
                    '_op_type': 'index'
                }
            )
        else:
            ignoredRecordCount += 1
            print(record)
        if len(actions) == 50:
            pushBatch(actions)
            actions = []

    if len(actions) > 0:
        pushBatch(actions)
    print('Invalid Event records ignored: ' + str(ignoredRecordCount))
