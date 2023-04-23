import requests
import boto3
import json

API_CONFIG_TABLE = 'ApiConfig'


def get_api_token(bot):
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName='get_api_access_token',
        InvocationType='RequestResponse',
        Payload=json.dumps(bot)
    )
    data = json.load(response['Payload'])
    api_token = data['body']['access_token']
    return api_token


def get_configuration(bot_name):
    db = boto3.resource('dynamodb')
    db_table = db.Table(API_CONFIG_TABLE)
    response = db_table.get_item(
        Key={
            'bot_name': bot_name
        }
    )
    return response['Item']['config']


def query_api(api_endpoint, http_method, headers):
    if http_method == 'GET':
        response = requests.get(api_endpoint, headers=headers)
        return response


def lambda_handler(event, context):
    api_endpoint = event['endpoint']
    bot_name = event['bot_name']
    config = get_configuration(bot_name)
    needs_auth = config['requires_authentication']
    http_method = config['http_method']
    if not needs_auth:
        headers = {"User-Agent": f"{config['user_agent']}"}
        response = query_api(api_endpoint, http_method, headers)
    else:
        api_token = get_api_token({'bot_name': bot_name})
        headers = {
            "Authorization": f"Bearer {api_token}",
            "User-Agent": f"{config['user_agent']}"
        }
        response = query_api(api_endpoint, http_method, headers)
    return {
        "statusCode": response.status_code,
        "body": response.json()
    }
