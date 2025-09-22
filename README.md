# 🎤 English Conversation Practice App

고품질 영어회화 연습을 위한 데스크톱 애플리케이션입니다. Google Cloud API와 OpenAI를 활용하여 실시간 음성인식, AI 대화, 그리고 자연스러운 음성 출력을 제공합니다.

## ✨ 주요 기능

### 🎯 핵심 기능
- **🎤 실시간 음성인식**: Google Cloud Speech-to-Text API
- **🤖 AI 영어 튜터**: OpenAI GPT 또는 Ollama 지원
- **🔊 자연스러운 음성 출력**: Google Cloud Text-to-Speech API
- **📊 실시간 음성 레벨 표시**: 녹음 상태 시각화
- **💾 대화 기록 관리**: 세션 저장/불러오기

### 🚀 고급 기능
- **오프라인 모드**: Whisper 모델 지원
- **다양한 대화 주제**: 일상생활, 여행, 음식, 취미 등
- **실시간 통계**: 메시지 수, 토큰 사용량, 세션 시간
- **사용자 친화적 GUI**: 직관적인 tkinter 인터페이스
- **멀티 AI 제공자**: OpenAI ↔ Ollama 전환 가능

## 🖥️ 스크린샷 및 UI

```
┌─────────────────────────────────────────────────────────────────┐
│ 🎤 English Conversation Practice                               │
├─────────────────┬─────────────────────────┬─────────────────────┤
│ 🎛️ Controls     │ 💬 Conversation         │ 📊 Information      │
│                 │                         │                     │
│ 🎤 Start Record │ [대화 내용 표시 영역]     │ 🔧 Service Status:  │
│ Audio Level:    │                         │ Speech: ✅ Ready    │
│ ████████░░░     │ [You]: Hello!           │ AI: ✅ OpenAI       │
│                 │ [AI]: Hi there! How     │                     │
│ Topic:          │ are you doing today?    │ 📈 Session Stats:   │
│ ○ Daily Life    │                         │ Messages: 4         │
│ ● Travel        │ Type your message:      │ Duration: 2:15      │
│ ○ Food          │ [입력창]          [Send]│ Tokens: 145         │
│                 │                         │                     │
│ 🎯 Start Topic  │ Current transcription:  │ ⚙️ Settings:        │
│ 🔄 Clear Chat   │ "I want to practice..." │ ● OpenAI ○ Ollama   │
│ 💾 Save Chat    │                         │ ☐ Offline Mode     │
│ 📁 Load Chat    │                         │ Speech Speed: ████  │
└─────────────────┴─────────────────────────┴─────────────────────┘
│ Status: Recording audio... 🎤                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 빠른 시작

### 1. 설치
```bash
git clone <repository-url>
cd english-conversation-app
pip install -r requirements.txt
```

### 2. Google API 설정
1. [Google Cloud Console](https://console.cloud.google.com)에서 프로젝트 `speechtotext-472900` 설정
2. Speech-to-Text 및 Text-to-Speech API 활성화
3. 서비스 계정 생성 및 JSON 키 다운로드
4. `credentials/google-credentials.json`에 저장

### 3. 환경변수 설정
`.env` 파일에 API 키 설정:
```env
OPENAI_API_KEY=your-openai-api-key
GOOGLE_APPLICATION_CREDENTIALS=credentials/google-credentials.json
```

### 4. 실행
```bash
python main.py
```

자세한 설정 방법은 [SETUP_GUIDE.md](SETUP_GUIDE.md)를 참조하세요.

## 📁 프로젝트 구조

```
english-conversation-app/
├── 📄 main.py                 # 메인 GUI 애플리케이션
├── ⚙️ config.py               # 설정 관리
├── 🎤 google_speech.py        # Google API 음성 처리
├── 🤖 ai_tutor.py             # AI 대화 모듈
├── 📋 requirements.txt        # Python 패키지 목록
├── 🔐 .env                    # 환경변수 (사용자 생성)
├── 📚 SETUP_GUIDE.md          # 상세 설정 가이드
├── 📚 GOOGLE_API_SETUP.md     # Google API 설정 가이드
├── 🔒 .gitignore              # Git 무시 파일
├── 📁 credentials/            # API 인증 파일
│   └── 🔑 google-credentials.json
└── 📁 conversations/          # 대화 기록 저장
    └── 💬 conversation_*.json
```

## 🎮 사용법

### 음성 대화
1. **🎤 Start Recording** 버튼 클릭
2. 영어로 말하기
3. **🛑 Stop Recording** 버튼으로 종료
4. AI가 자동으로 응답

### 텍스트 대화
1. 하단 입력창에 영어 메시지 입력
2. **Enter** 키 또는 **Send** 버튼 클릭
3. AI 튜터가 즉시 응답

### 주제별 대화
1. 왼쪽 패널에서 관심 주제 선택
2. **🎯 Start Topic** 버튼 클릭
3. AI가 해당 주제로 대화 시작

## 🔧 기술 스택

### 🐍 Backend
- **Python 3.8+**: 메인 프로그래밍 언어
- **Google Cloud Speech-to-Text**: 고품질 음성인식
- **Google Cloud Text-to-Speech**: 자연스러운 음성 합성
- **OpenAI GPT**: 지능형 영어 튜터
- **Whisper**: 오프라인 음성인식 (백업)

### 🖥️ Frontend
- **tkinter**: Python 기본 GUI 라이브러리
- **ttk**: 현대적인 위젯 스타일
- **scrolledtext**: 대화 기록 표시

### 🔊 Audio
- **PyAudio**: 실시간 오디오 입출력
- **numpy**: 오디오 신호 처리
- **wave**: WAV 파일 처리

## ⚙️ 설정 옵션

### 음성 설정
```python
SPEECH_LANGUAGE = "en-US"        # 음성인식 언어
TTS_VOICE = "en-US-Wavenet-D"    # TTS 음성 선택
AUDIO_SAMPLE_RATE = 16000        # 샘플링 레이트
```

### AI 설정
```python
AI_PROVIDER = "openai"           # openai 또는 ollama
OPENAI_MODEL = "gpt-3.5-turbo"   # GPT 모델 선택
OFFLINE_MODE = False             # Whisper 오프라인 모드
```

### UI 설정
```python
WINDOW_WIDTH = 800               # 창 너비
WINDOW_HEIGHT = 600              # 창 높이
THEME = "light"                  # light 또는 dark
```

## 📊 API 사용량 및 비용

### 무료 할당량 (월간)
- **Google Speech-to-Text**: 60분
- **Google Text-to-Speech**: 100만 문자
- **OpenAI GPT-3.5**: 사용량에 따라 과금

### 예상 비용 (시간당)
- **일반적인 대화**: $0.10 ~ $0.30
- **집중 연습**: $0.50 ~ $1.00
- **오프라인 모드**: 무료 (로컬 처리)

## 🔒 보안 및 개인정보

### 데이터 처리
- **음성 데이터**: Google Cloud API로 전송 (HTTPS 암호화)
- **텍스트 데이터**: OpenAI API로 전송 (HTTPS 암호화)
- **대화 기록**: 로컬 저장 (JSON 형식)

### 개인정보 보호
- API 키는 환경변수로 관리
- 대화 기록은 사용자 컴퓨터에만 저장
- 네트워크 전송 시 암호화 적용

## 🤝 기여하기

### 버그 신고
1. GitHub Issues에 버그 상세 설명
2. 에러 로그 (`app.log`) 첨부
3. 운영체제 및 Python 버전 명시

### 기능 제안
1. 기능 제안을 GitHub Issues에 작성
2. 사용 사례와 예상 이점 설명
3. 구현 아이디어가 있다면 함께 제안

### 코드 기여
1. Fork 후 feature branch 생성
2. 코드 작성 및 테스트
3. Pull Request 생성

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🆘 지원

### 문제 해결
1. [SETUP_GUIDE.md](SETUP_GUIDE.md) 확인
2. 로그 파일 (`app.log`) 검토
3. GitHub Issues에 문제 신고

### 연락처
- **이슈 신고**: GitHub Issues
- **이메일**: [contact-email]
- **문서**: [wiki-link]

---

**Happy English Learning! 🎉📚**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Speech%20APIs-yellow.svg)](https://cloud.google.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-green.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)