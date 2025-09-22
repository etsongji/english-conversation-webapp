# Google Cloud API 설정 가이드

## 1. Google Cloud Console 설정

### 프로젝트 정보
- **프로젝트 ID**: speechtotext-472900
- **프로젝트 번호**: 1086880976598

### 1.1 Google Cloud Console 접속
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 프로젝트 `speechtotext-472900` 선택

### 1.2 API 활성화
다음 API들을 활성화해야 합니다:

1. **Speech-to-Text API**
   - 콘솔에서 "API 및 서비스" → "라이브러리" 이동
   - "Cloud Speech-to-Text API" 검색 후 활성화

2. **Text-to-Speech API**
   - "Cloud Text-to-Speech API" 검색 후 활성화

### 1.3 서비스 계정 생성
1. "IAM 및 관리자" → "서비스 계정" 이동
2. "서비스 계정 만들기" 클릭
3. 서비스 계정 정보 입력:
   - **이름**: `english-conversation-app`
   - **설명**: `English Conversation Desktop App Service Account`
4. 역할 부여:
   - `Cloud Speech Client`
   - `Cloud Text-to-Speech Client`
5. 완료 후 서비스 계정 생성

### 1.4 JSON 키 파일 다운로드
1. 생성된 서비스 계정 클릭
2. "키" 탭 → "키 추가" → "새 키 만들기"
3. 키 유형: JSON 선택
4. 생성하면 JSON 파일이 자동 다운로드됩니다
5. 이 파일을 `C:\dev\english-conversation-app\credentials\` 폴더에 저장
6. 파일명을 `google-credentials.json`으로 변경

## 2. 환경변수 설정

### 2.1 .env 파일 생성
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용 추가:

```env
# Google Cloud 설정
GOOGLE_APPLICATION_CREDENTIALS=credentials/google-credentials.json
GOOGLE_CLOUD_PROJECT=speechtotext-472900

# OpenAI API 설정 (선택사항)
OPENAI_API_KEY=your-openai-api-key-here

# Ollama 설정 (선택사항)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# 음성 설정
SPEECH_LANGUAGE=en-US
TTS_LANGUAGE=en-US
TTS_VOICE=en-US-Wavenet-D
AUDIO_SAMPLE_RATE=16000
```

### 2.2 디렉토리 구조
```
english-conversation-app/
├── credentials/
│   └── google-credentials.json
├── conversations/
├── main.py
├── config.py
├── google_speech.py
├── ai_tutor.py
├── requirements.txt
├── .env
└── GOOGLE_API_SETUP.md
```

## 3. 설치 및 실행

### 3.1 Python 가상환경 생성 (권장)
```bash
cd C:\dev\english-conversation-app
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3.2 패키지 설치
```bash
pip install -r requirements.txt
```

### 3.3 애플리케이션 실행
```bash
python main.py
```

## 4. 문제 해결

### 4.1 인증 오류
- `google-credentials.json` 파일 경로 확인
- 환경변수 `GOOGLE_APPLICATION_CREDENTIALS` 설정 확인
- 서비스 계정 권한 확인

### 4.2 API 할당량 확인
- Google Cloud Console → "API 및 서비스" → "할당량"에서 사용량 확인
- 무료 티어: 월 60분 Speech-to-Text, 100만 문자 Text-to-Speech

### 4.3 오디오 장치 오류
- PyAudio 설치 확인: `pip install pyaudio`
- Windows의 경우 Visual C++ 빌드 도구 필요할 수 있음
- 마이크 권한 확인

## 5. 보안 주의사항

1. **credentials.json 파일 보안**
   - Git에 커밋하지 마세요
   - `.gitignore`에 `credentials/` 추가
   - 파일 권한을 적절히 설정하세요

2. **API 키 관리**
   - `.env` 파일도 Git에 커밋하지 마세요
   - 환경변수로 관리하는 것을 권장합니다

## 6. 비용 관리

### 무료 티어 한도
- **Speech-to-Text**: 월 60분
- **Text-to-Speech**: 월 100만 문자

### 비용 절약 팁
- 짧은 음성 클립으로 테스트
- 개발 중에는 오프라인 모드(Whisper) 사용
- API 사용량 모니터링 설정