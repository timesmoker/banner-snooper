# 베이스 이미지
FROM python:3.10-slim

# 기본 패키지 + 한글 로케일 + 한글 폰트 + tzdata 설치
RUN apt-get update && apt-get install -y \
    locales \
    fonts-nanum fonts-noto-cjk fonts-unfonts-core \
    tzdata \
    wget unzip curl gnupg2 \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 \
    libxss1 libappindicator3-1 libasound2 \
    libatk-bridge2.0-0 libgtk-3-0 \
    libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 xdg-utils \
    && apt-get clean

# 한글 로케일 생성
RUN echo "ko_KR.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen ko_KR.UTF-8

# 환경변수 설정
ENV LANG=ko_KR.UTF-8
ENV LANGUAGE=ko_KR:ko
ENV LC_ALL=ko_KR.UTF-8

# 시간대 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 크롬 설치
RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o chrome.deb && \
    apt-get install -y ./chrome.deb && \
    rm chrome.deb

# 작업 디렉토리 설정 및 복사
WORKDIR /app
COPY . /app

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# entrypoint 실행 권한 부여
RUN chmod +x /app/entrypoint.sh

# 컨테이너 시작시 실행될 엔트리포인트
ENTRYPOINT ["/app/entrypoint.sh"]
