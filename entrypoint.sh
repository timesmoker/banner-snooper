#!/bin/bash

# 기본값은 delay=true
DELAY=${DELAY:-true}

if [[ "$DELAY" == "true" ]]; then
  SECONDS=$((RANDOM % 1201))
  echo "랜덤 대기: $SECONDS초"
  sleep $SECONDS
else
  echo "딜레이 없이 바로 실행 (DELAY=false)"
fi

# 실제 파이썬 실행
python /app/engine.py
