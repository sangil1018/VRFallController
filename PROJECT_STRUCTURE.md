# VRFallController - 프로젝트 구조

```
VRFallController/
│
├── 📄 main.py                          # FastAPI 메인 서버
├── 📄 config.py                        # 전역 설정
├── 📄 requirements.txt                 # Python 의존성
├── 📄 websocket_server.py              # WebSocket 서버 (레거시)
│
├── 📂 controllers/                     # 컨트롤러 모듈
│   ├── __init__.py
│   ├── simulator_controller.py        # 시뮬레이터 제어
│   ├── experience_controller.py       # 체험 제어
│   └── adb_controller.py              # ADB 디바이스 관리
│
├── 📂 utils/                           # 유틸리티
│   ├── __init__.py
│   └── logger.py                       # 로깅 시스템
│
├── 📂 static/                          # 웹 UI
│   ├── index.html                      # 메인 페이지
│   ├── css/
│   │   └── style.css                   # 다크모드 스타일
│   └── js/
│       └── app.js                      # 프론트엔드 로직
│
├── 📂 unity_client/                    # Unity 연동 스크립트
│   ├── VRControllerClient.cs          # PC 컨트롤러 통신 클라이언트
│   ├── UnityMainThreadDispatcher.cs   # 메인 스레드 디스패처
│   ├── VRSafetyExperienceManager.cs   # Timeline 제어 매니저
│   └── INTEGRATION.md                  # Unity 연동 가이드
│
├── 📂 Doc/                             # 추가 문서 (선택)
│
├── 📄 start.bat                        # 일반 모드 실행
├── 📄 start_test.bat                   # 테스트 모드 실행
├── 📄 setup_venv.bat                   # 가상환경 설정
├── 📄 adb_connect_all.bat              # ADB 자동 연결
│
├── 📘 README.md                        # 프로젝트 README
├── 📘 NETWORK_SETUP.md                 # 네트워크 구성 가이드
├── 📄 LICENSE                          # MIT 라이선스
└── 📄 .gitignore                       # Git 제외 파일
```

## Git으로 추적되는 파일

### 핵심 코드
- ✅ `main.py`, `config.py`
- ✅ `controllers/*.py`
- ✅ `utils/*.py`
- ✅ `static/**/*`

### Unity 연동
- ✅ `unity_client/*.cs`
- ✅ `unity_client/INTEGRATION.md`

### 스크립트
- ✅ `*.bat`

### 문서
- ✅ `README.md`
- ✅ `NETWORK_SETUP.md`
- ✅ `LICENSE`

## Git으로 추적되지 않는 파일 (.gitignore)

### 가상환경
- ❌ `venv/`

### 로그 및 캐시
- ❌ `*.log`
- ❌ `__pycache__/`
- ❌ `*.pyc`

### IDE 설정
- ❌ `.vscode/`
- ❌ `.idea/`

### 임시 파일
- ❌ `*.tmp`, `*.bak`

## GitHub 업로드 전 체크리스트

- [ ] `.gitignore` 파일 생성 완료
- [ ] `LICENSE` 파일 생성 완료
- [ ] `README.md` 최신 상태
- [ ] `requirements.txt` 최신 상태
- [ ] 민감한 정보(API 키 등) 제거 확인
- [ ] 로그 파일 삭제 (`vr_controller.log`)
- [ ] `venv/` 폴더 제외 확인
- [ ] 문서 오타 확인

## GitHub 초기화 및 업로드

```bash
# Git 초기화
git init

# 모든 파일 추가
git add .

# 첫 커밋
git config --global user.email "sangil1018@gmail.com"
git config --global user.name "sangil1018"

git commit -m "Initial commit: VR Fall Simulator Controller"

# GitHub 리포지토리 연결
git remote add origin https://github.com/sangil1018/VRFallController.git

# 푸시
git branch -M main
git push -u origin main
```

## 권장 GitHub 리포지토리 설정

### Description
```
VR Fall Safety Training Simulator Controller - Web-based PC app for controlling Pico 4 VR headsets and physical simulator
```

### Topics (태그)
```
vr, pico4, fastapi, websocket, python, unity, safety-training, simulator-controller
```

### README Badges
```markdown
![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-green)
```
