import berserk
import os
from datetime import datetime
from datetime import date
import json
import boto3

retVal = {
    "statusCode": 200,
    "body": "NO GAMES FOUND"
}

def lambda_handler(event, context):
    token = os.environ['LICHESS_PERSONAL_ACCESS_TOKEN']
    table_name = os.environ['LICHESS_TABLE_NAME']
    player = os.environ['PLAYER_TO_MONITOR']
    phone_number = os.environ['PHONE_NUMBER']
    json_region = os.environ['AWS_REGION']
    session = berserk.TokenSession(token)
    lichess_client = berserk.Client(session)
    dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
    today = date.today()
    year = today.year
    month = today.month
    day = today.day
    start = berserk.utils.to_millis(datetime(year,month,day))
    games = lichess_client.games.export_by_player(player, since=start, max=100)
    my_games = list(games)
    if len(my_games) == 0:
        return retVal
    print(my_games[0])
    game = my_games[0]
    most_recent_id = game['id']
    print(table_name)
    response = dynamodb_client.get_item(
        TableName=table_name,
        Key={
            'id': {
                'S': 'last_game'
            }
        }
    )
    print(response)
    if 'Item' not in response or most_recent_id != response['Item']['game_id']['S']:
        print('alert')
        response = dynamodb_client.put_item(
            TableName=table_name,
            Item={
                'id': {'S': 'last_game'},
                'game_id': {'S': most_recent_id}
            }
        )
        sns_client = boto3.client('sns', region_name='us-east-1')
        print(phone_number)
        message = f'{player} started a new game on Lichess!'
        print(player)
        response = sns_client.publish(PhoneNumber=phone_number, Message=message)
        print(response)
        return retVal
    else:
        print('no alert')
    retVal['body'] = json.dumps({'region': json_region})
    return retVal
