# 📚 영어회화 연습 앱 설치 및 설정 가이드

## 🎯 개요
이 앱은 Google Cloud API와 OpenAI를 사용한 고품질 영어회화 연습 데스크톱 애플리케이션입니다.

## 🔧 시스템 요구사항
- **Windows 10/11** 또는 **macOS 10.14+** 또는 **Ubuntu 18.04+**
- **Python 3.8+** 
- **인터넷 연결** (API 사용을 위해)
- **마이크와 스피커** (음성 기능용)

## 📋 설치 단계

### 1. 프로젝트 다운로드
```bash
git clone <repository-url>
cd english-conversation-app
```

### 2. Python 가상환경 생성 (권장)
```bash
# Windows
python -m venv venv
venv\\Scripts\\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치

#### 기본 패키지 설치
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Windows에서 PyAudio 설치 오류 시
```bash
# 방법 1: 미리 컴파일된 wheel 사용
pip install https://download.lfd.uci.edu/pythonlibs/archived/PyAudio-0.2.11-cp39-cp39-win_amd64.whl

# 방법 2: conda 사용 (Anaconda 설치된 경우)
conda install pyaudio

# 방법 3: Visual Studio Build Tools 설치 후 재시도
```

#### macOS에서 PyAudio 설치 오류 시
```bash
# Homebrew로 portaudio 설치
brew install portaudio
pip install pyaudio
```

### 4. Google Cloud API 설정

#### 4.1 Google Cloud Console 설정
1. [Google Cloud Console](https://console.cloud.google.com)에 접속
2. 프로젝트 `speechtotext-472900` 선택
3. 다음 API 활성화:
   - Cloud Speech-to-Text API
   - Cloud Text-to-Speech API

#### 4.2 서비스 계정 생성
1. IAM 및 관리자 → 서비스 계정
2. "서비스 계정 만들기" 클릭
3. 이름: `english-conversation-app`
4. 역할 부여:
   - Cloud Speech Client
   - Cloud Text-to-Speech Client
5. JSON 키 파일 다운로드

#### 4.3 인증 파일 설정
1. 다운로드한 JSON 파일을 `credentials/google-credentials.json`으로 저장
2. 파일 경로가 올바른지 확인

### 5. 환경변수 설정

#### .env 파일 수정
```env
# Google Cloud 설정
GOOGLE_APPLICATION_CREDENTIALS=credentials/google-credentials.json
GOOGLE_CLOUD_PROJECT=speechtotext-472900

# OpenAI API 설정
OPENAI_API_KEY=your-openai-api-key-here

# AI 제공자 선택
AI_PROVIDER=openai

# 음성 설정
SPEECH_LANGUAGE=en-US
TTS_LANGUAGE=en-US
TTS_VOICE=en-US-Wavenet-D
```

#### OpenAI API 키 설정
1. [OpenAI Platform](https://platform.openai.com/api-keys)에서 API 키 생성
2. `.env` 파일의 `OPENAI_API_KEY`에 입력

## 🚀 애플리케이션 실행

### 설정 검증
```bash
# 설정 검증
python config.py

# 개별 모듈 테스트
python google_speech.py
python ai_tutor.py
```

### 앱 실행
```bash
python main.py
```

## 🎮 사용법

### 기본 기능
1. **🎤 음성 대화**: "Start Recording" 버튼으로 음성 녹음
2. **💬 텍스트 채팅**: 하단 입력창에서 텍스트로 대화
3. **🎯 주제 선택**: 왼쪽 패널에서 대화 주제 선택
4. **💾 대화 저장**: "Save Chat" 버튼으로 대화 내용 저장

### 고급 기능
- **AI 제공자 변경**: OpenAI ↔ Ollama 전환 가능
- **오프라인 모드**: Whisper를 사용한 로컬 음성인식
- **음성 속도 조절**: TTS 속도 조절 슬라이더
- **대화 기록 관리**: JSON 형식으로 대화 저장/불러오기

## 🔧 문제 해결

### 자주 발생하는 오류

#### 1. Google API 인증 오류
```
google.auth.exceptions.DefaultCredentialsError
```
**해결방법**:
- `credentials/google-credentials.json` 파일 경로 확인
- Google Cloud Console에서 API 활성화 확인
- 서비스 계정 권한 확인

#### 2. PyAudio 설치 오류
```
ERROR: Microsoft Visual C++ 14.0 is required
```
**해결방법**:
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019) 설치
- 또는 미리 컴파일된 wheel 파일 사용

#### 3. OpenAI API 오류
```
openai.error.AuthenticationError
```
**해결방법**:
- API 키 확인
- OpenAI 계정 크레딧 확인
- `.env` 파일의 `OPENAI_API_KEY` 설정 확인

#### 4. 마이크 접근 권한 오류
**Windows**: 
- 설정 → 개인정보 → 마이크 → 앱이 마이크에 액세스하도록 허용

**macOS**: 
- 시스템 환경설정 → 보안 및 개인 정보 보호 → 마이크

#### 5. 음성이 인식되지 않는 경우
- 마이크 볼륨 확인
- 주변 소음 줄이기
- 명확하게 발음하기
- Audio Level 막대에서 입력 확인

### 로그 확인
```bash
# 로그 파일 확인
cat app.log

# 실시간 로그 보기 (Linux/macOS)
tail -f app.log
```

## ⚙️ 설정 옵션

### 음성 설정
```env
# 언어 설정
SPEECH_LANGUAGE=en-US    # 음성인식 언어
TTS_LANGUAGE=en-US       # TTS 언어
TTS_VOICE=en-US-Wavenet-D # TTS 음성

# 오디오 설정
AUDIO_SAMPLE_RATE=16000
VOICE_ACTIVATION_THRESHOLD=0.01
MAX_RECORDING_TIME=30
```

### AI 설정
```env
# OpenAI 설정
OPENAI_MODEL=gpt-3.5-turbo
AI_PROVIDER=openai

# Ollama 설정 (로컬 AI)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### UI 설정
```env
# 윈도우 크기
WINDOW_WIDTH=800
WINDOW_HEIGHT=600

# 테마
THEME=light  # light 또는 dark
```

## 💰 비용 관리

### Google Cloud API 무료 할당량
- **Speech-to-Text**: 월 60분
- **Text-to-Speech**: 월 100만 문자

### OpenAI API 비용
- **GPT-3.5-turbo**: $0.002 per 1K tokens
- 일반적인 대화: 약 100-200 토큰 per 메시지

### 비용 절약 팁
1. **개발 시**: 오프라인 모드 (Whisper) 사용
2. **짧은 연습**: 긴 문장보다 짧은 문장으로 연습
3. **모니터링**: Google Cloud Console에서 사용량 확인

## 🆘 지원 및 도움

### 로그 레벨 설정
```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

### 문제 신고
1. 로그 파일 (`app.log`) 확인
2. 에러 메시지와 함께 이슈 신고
3. 운영체제 및 Python 버전 명시

### 추가 리소스
- [Google Cloud Speech-to-Text 문서](https://cloud.google.com/speech-to-text/docs)
- [OpenAI API 문서](https://platform.openai.com/docs)
- [Whisper 모델 정보](https://github.com/openai/whisper)

## 🔄 업데이트

### 패키지 업데이트
```bash
pip install --upgrade -r requirements.txt
```

### 설정 백업
중요한 설정 파일들을 주기적으로 백업하세요:
- `.env` 파일
- `credentials/` 폴더
- `conversations/` 폴더 (선택사항)

---

**즐거운 영어 학습 되세요! 🎉**