#!/bin/bash

# 환경 변수 로드
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

# 개발 환경으로 실행
if [ "$1" = "dev" ]; then
  echo "Running in development mode..."
  export DJANGO_SETTINGS_MODULE=hyper_pets_backend.dev.settings
  export DEBUG=True
  docker-compose up --build
# 프로덕션 환경으로 실행
else
  echo "Running in production mode..."
  export DJANGO_SETTINGS_MODULE=hyper_pets_backend.production.settings
  export DEBUG=False
  docker-compose up -d --build
fi
