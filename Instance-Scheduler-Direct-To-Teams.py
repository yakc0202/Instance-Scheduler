# Instance Scheduler log에서 ERROR가 발생할 경우 CloudWatch logs의 Lambda 구독 필터 생성 -> Lambda, Lambda -> Teams 로 알람 전송

import json
import urllib3
import base64
import gzip
import re
import os

from io import BytesIO
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

http = urllib3.PoolManager()
teams_url = os.environ['teams'] # Lambda의 환경 변수에 TEAMS의 Webhook URL을 넣어두고 꺼내쓰기

def card(title:str, time:str, text:str, facts:dict):
    return {
        "type" "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-cards.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            {
                                "type": "TextBlock",
                                "text": title,
                                "size": "Large",
                                "weight": "Bolder",
                                "wrap": True
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "stretch"
                                    },
                                    {
                                        "type": "Column",
                                        "width": "auto",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "Text": time,
                                                "isSubtile": True,
                                                "size": "Small",
                                                "horixontalAlighnment": "Right"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "TextBlock",
                                "text": text,
                                "wrap": True
                            },
                            {
                                "type": "FactSet",
                                "facts": [{"title":k, "value":str(v)} for k,v in facts.items()]
                            }
                        }
                    ]
                }
            }
        ]
    }

def lambda_handler(event, context):
    logs = json.loads(gzip.GzipFile(fileobj=BytesIO(base64.b64decode(event['awslogs']['data'], validate=True))).read())

    resources = []
    for i in range(len(logs['logEvents'])):
        if logs['logStream'].split('-')[1] == 'ec2':
            resources.append(re.search(r"(i-[0-9a-fA-F]+)", logs['logEvents'][i]['message']).group(1))
        elif logs['logStream'].split('-')[1] == 'rds':
            resources.append(re.search(r"RDS:[^:]+:([^,]+)", logs['logEvents'][i]['message']).group(1))
    
    title = logs['subscriptionFilters'][0]
    text = "Instance Scheduler doesn't work."
    time = datetime.fromtimestamp(logs['logEvents'][0]['timestamp']/1000, tz=ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%dT%H:%M:%S KST")
    facts = {
        "Status": "TRIGGERED",
        "Urgency": "HIGH",
        "Region": "ap-northeast-2",
        "Account": logs['logStream'].split('-')[2],
        "Resources": ', '.join(resources)
    }

    payload = card(title, text, time, facts)

    response = http.request(
        'POST',
        teams_url,
        body=json.dumps(payload).encode('utf-8')
        headers={'Content-Type': 'application/json'}
    )

    return {
        'statusCode':  response.status,
        'body': resources.data.decode('utf-8')
    }
