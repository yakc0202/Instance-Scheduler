# Instance Scheduler 에러 알람 아키텍처

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
