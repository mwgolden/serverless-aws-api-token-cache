import json
import boto3
import time
import sys
import logging
import requests
import requests.auth

API_CONFIG_TABLE = 'ApiConfig'
API_TOKEN_CACHE_TABLE = 'ApiTokenCache'

def get_configuration(bot_name):
    db = boto3.resource('dynamodb')
    db_table = db.Table(API_CONFIG_TABLE)
    response = db_table.get_item(
        Key={
            'bot_name': bot_name
        }
    )
    return response['Item']['config']

def get_cached_auth_token(bot_name):
    db = boto3.resource('dynamodb')
    db_table = db.Table(API_TOKEN_CACHE_TABLE)
    response = db_table.query(
        Limit=1,
        KeyConditionExpression='bot_name=:botname',
        ExpressionAttributeValues={
            ':botname':bot_name
        },
        ScanIndexForward=False
    )
    return response

def get_client_credentials(client_id, client_secret):
    ssm_client = boto3.client('ssm')
    client_id_param = ssm_client.get_parameter(Name=client_id)
    client_secret_param = ssm_client.get_parameter(Name=client_secret, WithDecryption=True)
    return(client_id_param['Parameter']['Value'], client_secret_param['Parameter']['Value'])

def get_auth_token(bot_name, config) -> dict:
    cached_token = get_cached_auth_token(bot_name=bot_name)
    if cached_token['Count'] == 1:
        response = cached_token['Items'][0]['access_token']
        epoch_time = int(time.time())
        exp_date = cached_token['Items'][0]['expires']
        response['expires_in'] = exp_date - epoch_time
    else:
        clientid, clientsecret = get_client_credentials(
                client_id=config['client_id'],
                client_secret=config['client_secret']
            )
        client_auth = requests.auth.HTTPBasicAuth(clientid, clientsecret)
        data = {"grant_type":config['grant_type'], "scope": config['scope'], "X-Modhash": "xF3123"}
        headers = {"User-Agent": config['user_agent']}
        response = requests.post(config['auth_endpoint'], auth=client_auth, data=data, headers=headers).json()
        cache_token(bot_name=bot_name, data=response)
    return response

def cache_token(bot_name, data):
    print(data)
    if 'expires_in' in data.keys():
        epoch_time = int(time.time())
        ttl_seconds =  data['expires_in']
        expires_on = epoch_time + ttl_seconds
    else:
        expires_on = sys.maxsize
        data['expires_in'] = expires_on
    db = boto3.resource('dynamodb')
    table = db.Table(API_TOKEN_CACHE_TABLE)
    table.put_item(
        Item={
                'bot_name': bot_name,
                'expires': expires_on,
                'access_token': data
        }
    )

def lambda_handler(event, context):
    bot_name = event["bot_name"]
    api_config = get_configuration(bot_name=bot_name)
    response_data = get_auth_token(bot_name=bot_name, config=api_config)
    return {
        "statusCode": 200,
        "body": response_data
    }
