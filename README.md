# Hyper Pets Backend

Django 기반의 Hyper Pets 백엔드 서버입니다.

## 환경 설정

1. `.env.example` 파일을 복사하여 `.env` 파일을 생성합니다:

```bash
cp .env.example .env
```

2. `.env` 파일을 편집하여 필요한 환경 변수를 설정합니다.

## 개발 환경에서 실행하기

### 로컬에서 직접 실행

1. 가상 환경을 생성하고 활성화합니다:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

2. 필요한 패키지를 설치합니다:

```bash
pip install -r requirements.txt
```

3. 개발 서버를 실행합니다:

```bash
./scripts/run_dev.sh
```

### Docker를 사용하여 개발 환경에서 실행

```bash
./scripts/run_docker.sh dev
```

## 프로덕션 환경에서 실행하기

### Docker를 사용하여 프로덕션 환경에서 실행

```bash
./scripts/run_docker.sh
```

## 데이터베이스 초기화

초기 데이터를 로드하려면:

```bash
./scripts/init_data.sh dev  # 개발 환경
# 또는
./scripts/init_data.sh  # 프로덕션 환경
```

슈퍼유저를 생성하려면:

```bash
./scripts/init_data.sh dev createsuperuser  # 개발 환경
# 또는
./scripts/init_data.sh createsuperuser  # 프로덕션 환경
```

## AWS 배포

1. `.env` 파일에 필요한 AWS 관련 환경 변수를 설정합니다.
2. 프로덕션 모드로 Docker 컨테이너를 실행합니다.
3. AWS EC2 인스턴스에서 실행하는 경우, 보안 그룹 설정에서 필요한 포트(80, 8000)를 열어주세요.

## 환경 분리

이 프로젝트는 개발 환경과 프로덕션 환경이 분리되어 있습니다:

- 개발 환경: `hyper_pets_backend.dev.settings`
- 프로덕션 환경: `hyper_pets_backend.production.settings`

각 환경에 맞는 설정을 사용하여 실행하세요.
