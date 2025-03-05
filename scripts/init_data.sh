#!/bin/bash

# 환경 변수 로드
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

# 개발 환경인지 확인
if [ "$1" = "dev" ]; then
  SETTINGS=hyper_pets_backend.dev.settings
else
  SETTINGS=hyper_pets_backend.production.settings
fi

# 데이터베이스 마이그레이션
python manage.py migrate --settings=$SETTINGS

# 초기 데이터 로드 (fixtures가 있는 경우)
if [ -d fixtures ]; then
  for fixture in fixtures/*.json; do
    if [ -f "$fixture" ]; then
      echo "Loading fixture: $fixture"
      python manage.py loaddata $fixture --settings=$SETTINGS
    fi
  done
fi

# 슈퍼유저 생성 (필요한 경우)
if [ "$2" = "createsuperuser" ]; then
  python manage.py createsuperuser --settings=$SETTINGS
fi
