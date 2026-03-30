# Instance Scheduler 에러 알람 아키텍처
![](https://github.com/user-attachments/assets/4b4146ab-b7bd-4097-8ada-5631c162e30d)
# Instance Scheduler 에러 알람 설명
## through SpaceOne
1. Instance Scheduler가 ERROR라는 단어를 포함한 로그를 기록한다.
   - 임의로 발생시키기 어려운 부분이 있어서, 테스트는 Role에서 policy를 제거하고 진행
2. CloudWatch logs의 Subscription Filter를 적용
  - 패턴 필터링을 `ERROR`으로 설정
3. `ERROR`라는 단어가 포함된 로그가 생성되면 연결된 Lambda로 로그 전송
4. Lambda에서 SpaceOne에서 확인할 수 있게 CloudWatch Alarm 포맷으로 변환 후 SpaceOne으로 전송
5. SpaceOne에서 Microsoft Teams로 데이터 전송

## direct to Teams
1. Instance Scheduler가 ERROR라는 단어를 포함한 로그를 기록한다.
   - 임의로 발생시키기 어려운 부분이 있어서, 테스트는 Role에서 policy를 제거하고 진행
2. CloudWatch logs의 Subscription Filter를 적용
  - 패턴 필터링을 `ERROR`으로 설정
3. `ERROR`라는 단어가 포함된 로그가 생성되면 연결된 Lambda로 로그 전송
4. Lambda에서 Teams의 Webhook 포맷에 맞게 변환 후 Teams Webhook으로 전송
---
# 공휴일 Instance Scheduler 구성
## Instance-Scheduler-Holiday-Create-EVB
- 매 월 1일 실행되어 공휴일 당일에 실행할 EventBridge 일정 생성용 Lambda
- OracleDB에서 공휴일 정보를 획득하여 그에 맞춰 EventBridge 일정 생성
- Lambda의 환경 변수에 넣을 값
  - DB_DSN: Oracle DB의 DSN
  - DB_USER: Oracle DB에 연결할 username
  - DB_PASSWORD: Oracle DB에 연결할 password
  - EVENTBRIDGE_ROLE_ARN: EventBridge에 연결할 Role ARN 지정
  - DYNAMO_LAMBDA_ARN: 생성된 EventBridge에서 트리거할 Lambda 함수 ARN 지정

## Instance-Scheduler-Holiday-Modify-DynamoDB
- 공휴일 당일에 DynamoDB에 저장된 인스턴스를 컨트롤하는 tag의 value에서 일정을 삭제하여 기존 일정대로 동작하지 못하도록 함
- 공휴일이 끝나면 일정을 원복하여 Instance Scheduler을 정상으로 되돌림
- Lambda의 환경 변수에 넣을 값
  - ORIGIN_SCHEDULE: 원래 사용중이던 일정
  - TABLE_NAME: Instance Scheduler의 Config Table의 이름