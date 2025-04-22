#!/bin/bash

# .env.GHCR 파일 불러오기
set -a
source /home/timesmoker/.envs/.env.ghcr
set +a

# GHCR 로그인
echo "$GHCR_PAT" | docker login ghcr.io -u "$GHCR_USERNAME" --password-stdin

# 이미지 최신화 (배너 스누퍼만)
docker pull "$GHCR_REPO:armlatest"

# 기존 컨테이너 있으면 중지 + 삭제
docker stop banner-snooper || true
docker rm banner-snooper || true

# 새 컨테이너 실행 (환경변수 주입)
docker run -d \
  --name banner-snooper \
  --env-file /home/timesmoker/.envs/.env.banner-snooper \
  "$GHCR_REPO:armlatest"
