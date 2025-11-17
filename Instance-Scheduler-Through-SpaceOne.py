# Instance Scheduler log에서 ERROR가 발생할 경우 CloudWatch logs의 Lambda 구독 필터 생성 -> Lambda, Lambda -> SpaceOne, SpaceOne -> Teams 로 알람 전송

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
    time = datetime.fromtimestamp(logs['logEvents'][0]['timestamp']/1000, tz=ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"0000"
    accountId = logs['losStream'].split('-')[2]

    parsed_message = {
        "AlarmName": title,
        "AlarmDescription": None,
        "AWSAccountId": accountId,
        "AlarmConfigurationUpdatedTimestamp": time,
        "NewStateValue": "ALARM",
        "NewStateReason": text,
        "StateChangeTime": time,
        "Region": "Asia Pacific (Seoul)",
        "AlarmArn": "arn:aws:cloudwatch:ap-northeast-2:ACCOUNT_ID:alarm:"+title,
        "OldStateValue": "OK",
        "Trigger": {
            "Period": 60,
            "EvaluationPeriods": 1,
            "ComparisonOperator": "GreaterThenOrEqualToThreshold",
            "ThresholdMetricId": "ad1",
            "TreatMissingData": "missing",
            "EvaluateLowSampleCountPercentile": "",
            "Metrics": [
                {
                    "Id": "m1",
                    "MetricStat": {
                        "Metric": {
                            "Dimensions": [
                                {
                                    "value": ', '.join(resources),
                                    "name": "Resources"
                                }
                            ],
                            "MetricName": "Instance-Scheduler-State",
                            "Namespace": "Instance-Scheduler"
                        },
                        "Period": 60,
                        "State": "Maximum"
                    },
                    "ReturnData": True,
                    "AccountId": accountId
                }
            ]
        }
    }

    payload = {
        "Message": json.dumps(parsed_message)
    }

    headers = {'Content-Type': 'application/json'}

    response = http.request(
        'POST',
        webhook_url,
        body=json.dumps(payload),
        headers=headers
    )

    return {
        'statusCode': response.status,
        'body': response.data.decode('utf-8')
    }