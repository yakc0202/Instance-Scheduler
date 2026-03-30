import oracledb
import os
from datetime import datetime, timezone, timedelta
import boto3
import json

try:
    oracledb.init_oracle_client(lib_dir='/opb/lib')
except Exception as e:
    print(f'Client Init Error: {e}')

scheduler = boto3.client('scheduler')

# 이미 만들어진 EventBridge 일정이 없을때 일정을 만들고,
# 이미 만들어진 EventBridge 일정이 있을때 오류를 뱉지 않는 함수 추가
def create_event_schedule(date_str, schedule_time, state):
    try:
        scheduler.create_schedule(
            Name = f"holiday-{date_str}-{state}",
            ScheduleExpression = f"at({date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T{schedule_time}:00)",
            ScheduleExpressionTimeZone = "Asia/Seoul",
            FlexibleTimeWindow = {"Mode": "OFF"},
            ActionAfterCompletion = "DELETE",
            Target = {
                "Arn": os.environ["DYNAMO_LAMBDA_ARN"],
                "RoleArn": os.environ["EVENTBRIDGE_ROLE_ARN"],
                "Input": json.dumps({"action": state, "tag_value": "Holidays"}),
                "RetryPolicy": {'MaximumRetryAttempts': 0}
            },
        )
        print(f"Schedule created successfully.")

    except Exception as e:
        pass

def lambda_handler(event, context):
    month = datetime.now(timezone(timedelta(hours=9))).strftime("%Y%m")

    try:
        conn = oracledb.connect(
            user = os.environ['DB_USER']
            password = os.environ["DB_PASSWORD"]
            dsn = os.environ["DB_DSN"]
        )

        cursor = conn.cursor()

        # 이번달 데이터 조회
        cursor.execute("SECRET!!!", YM=month)

        holidays = cursor.fetchall()

        for h in holidays:
            date_str = h[0]

        
            # 주말 제외
            if datetime.strptime(date_str, "%Y%m%d").weekday() >= 5:
                continue
            
            # EventBridge 일정 만들기 - 00:00용 일정
            create_event_schedule(date_str, schedule_time="00:00", state="disable")

            # EventBridge 일정 만들기 - 23:59용 일정
            create_event_schedule(date_str, schedule_time="23:59", state="enable")

    except Exception as e:
        print("실패", e)
    
    # OracleDB 연결 끊기
    finally:
        cursor.close()
        conn.close()