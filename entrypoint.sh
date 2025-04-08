#!/bin/bash

# 기본값은 delay=true
DELAY=${DELAY:-true}

if [[ "$DELAY" == "true" ]]; then
  SECONDS=$((RANDOM % 1200))
  echo "랜덤 대기: $SECONDS초"
  sleep $SECONDS
else
  echo "딜레이 없이 바로 실행 (DELAY=false)"
fi

echo "engine.py 실행 시도"
python /app/engine.py || echo "engine.py 실행 실패"
