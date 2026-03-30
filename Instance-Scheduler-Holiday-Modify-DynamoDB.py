import json
import os
import boto3

dynamo = boto3.resource('dynamodb')
table = dynamo.Table(os.environ['TABLE_NAME'])

def modify_schedule(action, tag_value):
    try:
        # 기존 스케줄 제거
        if action == 'disable':
            table.update_item(
                Key = {'type': 'TAG_VALUE', 'name': 'tag_value'},
                UpdateExpression = 'SET periods = :holiday',
                ExpressionAttributeValues = {
                    ':holiday': {'holiday-period'}
                }
            )
            print(f'{tag_value} 스케줄을 비활성화 했습니다.')

        # 기존 스케줄 복원
        elif action == 'enable':
            table.update_item(
                Key = {'type': 'TAG_VALUE', 'name': tag_value},
                UpdateExpression = 'SET periods = :origin',
                ExpressionAttributeValues = {
                    ':origin': {os.environ['ORIGIN_SCHEDULE']}
                }
            )
            print(f'{tag_value} 스케줄을 복구했습니다.')
        return {'status_code': 200, 'body': json.dumps(f'{tag_value} 작업이 완료되었습니다.')}

    except Exception as e:
        print(f'오류가 발생했습니다.: {str(e)}')

def lambda_handler(event, context):
    action = event.get('action')
    tag_value = event.get('tag_value')

    print(f'요청한 작업: {action}, 스케줄 이름: {tag_value}')

    modify_schedule(action, tag_value)