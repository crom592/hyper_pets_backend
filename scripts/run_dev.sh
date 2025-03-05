#!/bin/bash

# 개발 환경에서 애플리케이션 실행
export DJANGO_SETTINGS_MODULE=hyper_pets_backend.dev.settings
export DEBUG=True

# 데이터베이스 마이그레이션
python manage.py migrate

# 개발 서버 실행
python manage.py runserver 0.0.0.0:8000
