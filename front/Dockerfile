# 파이썬 3.9 버전의 가벼운 이미지 사용
FROM python:3.9-slim

# 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 패키지 설치를 위해 requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프론트엔드 소스 코드 복사
COPY app.py .

# Streamlit 기본 포트 개방
EXPOSE 8501

# 컨테이너 실행 시 Streamlit 구동 (CORS 및 포트 설정 포함)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]