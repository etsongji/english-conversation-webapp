# 🚀 Railway 배포 가이드

English Conversation App을 Railway에 배포하는 방법을 설명합니다.

## 📋 사전 준비

1. **Railway 계정 생성**: [railway.app](https://railway.app)에서 계정 만들기
2. **OpenAI API 키**: [platform.openai.com](https://platform.openai.com)에서 API 키 발급
3. **Git 리포지토리**: GitHub, GitLab 등에 코드 업로드

## 🔧 배포 단계

### 1. Railway 프로젝트 생성

```bash
# Railway CLI 설치 (선택사항)
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 생성
railway init
```

### 2. 환경 변수 설정

Railway 대시보드에서 다음 환경 변수들을 설정하세요:

#### **필수 환경 변수:**
```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_super_secret_key_here
PORT=5000
RAILWAY_ENVIRONMENT=production
```

#### **선택적 환경 변수:**
```env
OPENAI_MODEL=gpt-3.5-turbo
SPEECH_LANGUAGE=en-US
TTS_LANGUAGE=en-US
THEME=light
```

### 3. Git 리포지토리 연결

1. Railway 대시보드에서 "Deploy from GitHub repo" 선택
2. 해당 리포지토리 선택
3. 자동 배포 설정

### 4. 배포 확인

배포 완료 후:
- Railway에서 제공하는 URL로 접속
- `/health` 엔드포인트에서 상태 확인
- AI 서비스 연결 상태 확인

## 🔒 보안 설정

### Secret Key 생성
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 환경 변수 보안
- 민감한 정보는 Railway 환경 변수에서만 설정
- `.env` 파일은 절대 Git에 커밋하지 않기
- `.gitignore`에 `.env` 추가

## 📊 모니터링

Railway 대시보드에서 확인할 수 있는 정보:
- 애플리케이션 로그
- 메모리 및 CPU 사용량
- 배포 히스토리
- 환경 변수 관리

## 🚨 문제 해결

### 자주 발생하는 문제:

1. **AI 서비스 연결 실패**
   - OpenAI API 키 확인
   - 계정 크레딧 잔액 확인

2. **포트 문제**
   - `PORT` 환경 변수가 Railway에서 제공하는 값과 일치하는지 확인

3. **정적 파일 서빙**
   - Flask가 templates/static 폴더를 올바르게 찾는지 확인

4. **메모리 부족**
   - Railway 플랜 업그레이드 고려
   - 불필요한 라이브러리 제거

## 🔄 업데이트 배포

코드 변경 후:
1. Git에 커밋 및 푸시
2. Railway에서 자동 재배포
3. 배포 로그 확인

## 📝 추가 설정

### Custom Domain (선택사항)
Railway 대시보드에서 커스텀 도메인 설정 가능

### 데이터베이스 연결 (필요시)
Railway에서 PostgreSQL, Redis 등 추가 서비스 연결 가능

## 💡 팁

- **무료 플랜 한계**: 월 500시간 실행 시간
- **로그 모니터링**: Railway CLI로 실시간 로그 확인 가능
- **백업**: 주기적으로 대화 데이터 다운로드
- **성능 최적화**: 필요에 따라 캐싱 구현

## 📞 지원

문제 발생시:
1. Railway 공식 문서 확인
2. GitHub Issues에 버그 리포트
3. Railway Discord 커뮤니티 참여