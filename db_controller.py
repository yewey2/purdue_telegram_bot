import os
import boto3
from botocore.exceptions import ClientError

ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')
TABLE_NAME = os.environ.get('TABLE_NAME')

# client = boto3.client(
#     'dynamodb',
#     aws_access_key_id=ACCESS_KEY,
#     aws_secret_access_key=SECRET_KEY,
#     # aws_session_token=SESSION_TOKEN
# )

def create_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )
    try:
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            AttributeDefinitions=[
                {
                    'AttributeName': 'chat_id',
                    'AttributeType': 'N'
                },
                # {
                #     'AttributeName': 'username',
                #     'AttributeType': 'S'
                # },
                # {
                #     'AttributeName': 'password',
                #     'AttributeType': 'S'
                # },
            ],
            KeySchema=[
                {
                    'AttributeName': 'chat_id',
                    'KeyType': 'HASH'  
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        return table
    except ClientError:
        return None
    finally:
        return None

def get_user_data(chat_id=None, dynamodb=None):
    """Getting single entry"""
    if not chat_id:
        return None
    create_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )
    table = dynamodb.Table(TABLE_NAME)
    response = None
    try:
        response = table.get_item(Key={'chat_id': chat_id})['Item']
    except ClientError as e:
        print(e.response['Error']['Message'])
    except KeyError as e:
        print('Key Error! Item not found')
        print(e)
    finally:
        return response

def set_user_data(chat_id=None, username="", password="", dynamodb=None):
    """Updating single entry"""
    if not chat_id:
        return None
    create_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )
    table = dynamodb.Table(TABLE_NAME)
    try:
        response = table.update_item(
            Key={
                'chat_id': chat_id,
            },
            UpdateExpression="set username=:u, password=:p",
            ExpressionAttributeValues={
                ':u': username,
                ':p': password
            },
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    except KeyError as e:
        print('Key Error! Item not found')
        print(e)
    finally:
        return response

if __name__ == '__main__':
    print('Set up DB OK.')