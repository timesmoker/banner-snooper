# 베이스 이미지 (Playwright 공식)
FROM mcr.microsoft.com/playwright/python:v1.51.0-jammy


# 한글 폰트 + tzdata 설치 (비대화식 모드)
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    locales \
    fonts-nanum fonts-noto-cjk fonts-unfonts-core \
    tzdata && apt-get clean


# 타임존 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 한글 로케일 설정
RUN echo "ko_KR.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen ko_KR.UTF-8

ENV LANG=ko_KR.UTF-8
ENV LANGUAGE=ko_KR:ko
ENV LC_ALL=ko_KR.UTF-8

# requirements.txt 먼저 복사 → 캐시 덜깨짐
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . /app
WORKDIR /app

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# entrypoint 실행 권한
RUN chmod +x /app/entrypoint.sh

# 컨테이너 시작 시 엔트리포인트 실행
ENTRYPOINT ["/app/entrypoint.sh"]
