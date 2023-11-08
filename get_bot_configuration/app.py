import json
import boto3
import sys
import logging

API_CONFIG_TABLE = 'ApiConfig'


def get_configuration(bot_name):
    db = boto3.resource('dynamodb')
    db_table = db.Table(API_CONFIG_TABLE)
    response = db_table.get_item(
        Key={
            'bot_name': bot_name
        }
    )
    return response['Item']['config']


def lambda_handler(event, context):
    bot_name = event["bot_name"]
    api_config = get_configuration(bot_name=bot_name)
    return {
        "statusCode": 200,
        "body": api_config
    }
