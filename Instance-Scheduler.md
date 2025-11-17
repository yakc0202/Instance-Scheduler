# Instance Scheduler
특정 시간에 EC2, RDS, AutoScalingGroup, DynamoDB 등의 AWS 리소스를 스케줄링을 통해 자동으로 시작 및 중지할 수 있도록 해주는 AWS 솔루션
## 주요 기능
- **비용 절감**: 인스턴스를 사용하지 않는 시간에 자동으로 중지하여 요금이 부과되지 않도록 함으로써 운영 비용 크게 절감 가능
- **간편한 배포 및 관리**: AWS CloudFormation 템플릿을 사용하여 필요한 모든 리소스를 자동으로 프로비저닝하므로 손쉽게 솔루션 배포 가능
- **태그 기반 스케줄링**: 특정 태그를 인스턴스에 추가하기만 하면 해당 인스턴스에 미리 정의된 시작/중지 일정이 자동으로 적용됨
- **다중 계정 및 리전 지원**: Hub 계정에서 여러 Spoke 계정의 인스턴스 일정을 관리할 수 있어, 조직 전체의 리소스 관리를 중앙에서 효율적으로 수행 가능
- **유연한 일정 정의**: 특정 시간, 요일, 날짜 등 다양한 조건으로 유연하게 스케줄을 생성하고 사용자 정의 가능
## 작동 방식
![](https://velog.velcdn.com/images/yakc0202/post/d0108192-122f-435e-a526-bc2d047cdbaf/image.png)

- **Amazon EventBridge**: 설정된 일정(예: 매 5분)에 따라 주기적으로 AWS Lambda 함수를 트리거
- **AWS Lambda**: 트리거된 Lambda 함수는 DynamoDB 테이블에서 스케줄 구성 정보를 읽어옴
- **Amazon DynamoDB**: 인스턴스를 언제 시작하고 중지할지에 대한 모든 스케줄 정보가 이 테이블에 저장
---
# 구성
[CloudFormation Template](https://docs.aws.amazon.com/ko_kr/solutions/latest/instance-scheduler-on-aws/aws-cloudformation-templates.html)
## Hub 계정
### 1. CloudFormation 템플릿 다운로드
CloudFormation Template 사이트에서 **instance-scheduler-on-aws.template**를 다운로드 하여, Hub로 사용할 계정의 CloudFormation에서 구성

### 2. CloudFormation 템플릿 구성
스택 생성 > 기존 템플릿 선택 > 템플릿 파일 업로드
![](https://velog.velcdn.com/images/yakc0202/post/ba69b28d-f35e-4a90-9348-1b54f387e162/image.png)
- **Scheduler**
![](https://velog.velcdn.com/images/yakc0202/post/b76fa577-c33d-4084-b797-0ef24372a07a/image.png)

  |종류|설명|
  |---|---|
  |Schedule tag key|Instance Scheduler에서 사용할 tag 키|
  |Scheduling interval|Lambda를 트리거할 EventBridge interval|
  |Default time zone|기본 타임존 설정|
  |Enable Scheduling|Instance Scheduler을 활성화/비활성화, Yes이면 활성화|

- **Services**
![](https://velog.velcdn.com/images/yakc0202/post/d515a12b-6b74-40c3-b42e-ef4c1761b09d/image.png)

  |종류|설명|
  |---|---|
  |Enable EC2 scheduling|EC2 스케줄링을 활성화/비활성화, Enabled이면 활성화|
  |Enable RDS instance scheduling|RDS instance 스케줄링을 활성화/비활성화, Enabled이면 활성화|
  |Enable RDS cluster scheduling|RDS cluster 스케줄링을 활성화/비활성화, Enabled이면 활성화|
  |Enable Neptune cluster scheduling|Netpune cluster 스케줄링을 활성화/비활성화, Enabled이면 활성화|
  |Enable DocumentDB cluster scheduling|DocumentDB cluster 스케줄링을 활성화/비활성화, Enabled이면 활성화|
  |Enable AutoScaling Group scheduling|AutoScaling Group 스케줄링을 활성화/비활성화, Enabled이면 활성화|

- **Tagging**
![](https://velog.velcdn.com/images/yakc0202/post/0642947c-c37e-4080-971c-f8f011745274/image.png)

  |종류|설명|
  |---|---|
  |Start tags|Instance Scheduler가 인스턴스를 작동한 시간 안내 태그, 빈칸으로 놔두면 태그 생성되지 않음|
  |Stop tags|Instance Scheduler가 인스턴스를 멈춘 시간 안내 태그, 빈칸으로 놔두면 태그 생성되지 않음|
  
- **Service-specific**
![](https://velog.velcdn.com/images/yakc0202/post/37ca1669-4f4c-40d6-8f0b-641998724b42/image.png)

- **Account structure**
![](https://velog.velcdn.com/images/yakc0202/post/0e12af04-5bd9-4c42-877f-f417750cc535/image.png)
  
  |종류|설명|
  |---|---|
  |Use AWS Organization|- AWS Organization을 사용할 지 설정, No이면 사용하지 않음<br> - Yes일 경우 AWS 조직 ID 입력, 계정을 일일이 |
  |Namespace|Instance Scheduler 배포를 위한 고유 식별자<br> - 하나의 AWS 계정에 여러 목적의 Instance Scheduler를 배포할 경우, 이름이 혼동되지 않게 구분해주는 역할|
  |Organization ID/remote account IDs|스케줄링을 적용할 대상 계정 명시<br> - `Use AWS Organization`이 Yes인 경우, organization ID<br> - No인 경우, 관리하고자 하는 AWS 계정 ID를 콤마(,)로 구분지어 작성|
  |Region(s)|Instance Scheduler가 관리할 리전 목록<br> - 콤마(,)로 구분지어 여러 리전 설정 가능<br> - 비워둘 경우 Instance Scheduler가 설치된 현재 리전만 관리 대상으로 간주|
  |Enable hub account scheduling|Hub 계정 자체를 스케줄링 대상으로 지정할 지 여부|
  
  
- **Monitoring**
![](https://velog.velcdn.com/images/yakc0202/post/0379d1cd-8633-440b-8f54-0ae09e2fbeab/image.png)

  |종류|설명|
  |---|---|
  |Log retention period(lifecycle)|Instance Scheduler가 생성하는 로그를 CloudWatch Logs에 며칠 동안 보관할지 설정하는 항목|
  |Enable CloudWatch debug Logs|디버그 수준의 로그 활성화 여부를 결정하는 항목|
  |Operational Monitoring|Instance Scheduler의 운영 상태를 한 눈에 볼 수 있는 모니터링 대시보드를 생성할지 여부를 결정하는 항목<br> - Yes이면, 커스텀 지표(시작된 인스턴스 수, 중지된 인스턴스 구 등 운영에 핵심적인 데이터를 수치화하여 기록), CloudWatch 대시보드(커스텀 지표들을 모아 그래프와 차트 형태로 시각화한 대시보드를 자동으로 생성)|
  
- **Other**
![](https://velog.velcdn.com/images/yakc0202/post/94b172dc-dcb5-4d64-b65b-a93b1be5245b/image.png)

  |종류|설명|
  |---|---|
  |SchedulingRequestHandler Memory size (MB)|EC2와 RDS의 스케줄링을 직접 처리하는 핵심 Lambda함수의 메모리 크기|
  |AsgHandler Memory size (MB)|ASG의 스케줄링을 전담하는 Lambda 함수의 메모리 크기|
  |Orchestrator Memory size (MB)|다중 계정, 다중 리전 환경에서 스케줄링 작업을 총괄 지휘하고 조정하는 오케스트레이터 Lambda 함수의 메모리 크기|
  |Protect DynamoDB Tables|Yes로 설정하면 CloudFormation 스택을 실수로 삭제하더라도 DynamoDB 테이블은 삭제되지 않고 보존|
  
## Spoke 계정
### 1. CloudFormation 템플릿 다운로드
CloudFormation Template 사이트에서 **instance-scheduler-on-aws-remote.template**를 다운로드 하여, Spoke로 사용할 계정의 CloudFormation에서 구성 혹은 Hub 계정에서 StackSet를 사용하여 구성

### 2. CloudFormation 템플릿 구성
#### 2-1. Spoke 계정에서 Stack으로 구성
Spoke로 사용할 계정의 CloudFormation에서 Stack으로 구성
![](https://velog.velcdn.com/images/yakc0202/post/6e234fbd-6e04-4bdb-be56-d82b80b26b73/image.png)
#### 2-2. Hub 계정에서 StackSet으로 구성
OU를 통해 권한을 받았다면 `Service-managed permissions`, OU를 통해 권한을 받지 못했거나, OU를 사용하지 않는 상태라면 `Self-service permissions`를 사용
![](https://velog.velcdn.com/images/yakc0202/post/1ecc2d7f-4731-44fd-8dc7-e2f12f10403f/image.png)
- **Account structure & Service-specific**
![](https://velog.velcdn.com/images/yakc0202/post/a9d18bfe-aff3-4b4a-a15c-85ec170b49ca/image.png)

  |종류|설명|
  |---|---|
  |Kms Key Arns for EC2|암호화된 디스크(EBS 볼륨)를 사용하는 EC2 인스턴스를 Instance Scheduler가 정상적으로 시작하는 데에 필요한 암호화 키(KMS Key)에 대한 권한을 부여하는 설정|
  
## Config 설정
DynamoDB에 생성되는 ConfigTable을 사용하여 스케줄과 기간 (Period)를 정의합니다. 각 항목은 type 속성으로 구분되며, 주요 속성은 다음과 같습니다.
- **config**: 스케줄러 전역 설정으로 인스턴스 스케줄러가 관리하는 org와 spoke 계정에 대한 설정이 포함되어 있습니다.
- **schedule**: 인스턴스 스케줄러에 적용할 스케줄러에 대한 설정으로, 실제 기간이 포함된 periods 리스트와 스케줄러 태그, 스케줄러가 수행될 시간대 등을 포함합니다.
- **period**: 시작 시간, 종료 시간, 적용할 요일에 대한 스케줄러의 시간 설정이 포함되어 있습니다.
### 1. **수동으로 설정**
### 2. **custom resource로 설정하는 방법**
custom-resource.yaml 파일을 구성하여 CloudFormation 스택으로 배포
  ```
AWSTemplateFormatVersion: 2010-09-09
Parameters:
  ServiceInstanceScheduleServiceTokenARN:
    Type: String
    Description: (Required) service token arn taken from InstanceScheduler outputs
Metadata:
  'AWS::CloudFormation::Designer': {}
Resources:
  # 1. 평일 09시 - 18시 실행, 평일 18시-09시 및 주말/휴일 24시간 종료
  Schedule1:
    Type: 'Custom::ServiceInstanceSchedule'
    Properties:
      ServiceToken: !Ref ServiceInstanceScheduleServiceTokenARN
      NoStackPrefix: 'True'
      Name: weekday-9-18-schedule
      Description: Runs instances on weekdays from 09:00 to 18:00 KST
      Timezone: Asia/Seoul
      Periods:
      - Description: Run from 09:00 to 18:00 on weekdays
        BeginTime: '09:00'
        EndTime: '18:00'
        WeekDays: mon-fri
  ```
  - `Resources`
    - `Schedule1`: Resource를 구분하는 이름, 임의 지정
    - `Name`: 관리하고자 하는 Instance에 붙은 tag value 값
    - `NoStackPrefix`: `'True'`로 설정하면, 스택 이름을 일정 이름의 접두사로 사용하지 않음
    - `Periods.BeginTime`: 인스턴스의 시작 시간
    - `Periods.EndTime`: 인스턴스의 중지 시간
    - `Periods.WeekDays`: 


![](https://velog.velcdn.com/images/yakc0202/post/fe639607-ae61-49b6-a5e0-fb8320732c4c/image.png)
  - **ServiceInstanceScheduleServiceTokenARN**
  Hub 계정에서 CloudFormation을 구성한 후, 해당 스택의 **Outputs** 탭에서 Value 값 복사 후 붙여넣기
![](https://velog.velcdn.com/images/yakc0202/post/42ca639a-6996-4017-bcef-f441c18c4d24/image.png)

