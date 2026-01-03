# VRFallController

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-green)

**VR Fall Safety Training Simulator Controller** - Web-based PC application for controlling Pico 4 VR headsets and physical fall simulator

---

## 📋 프로젝트 개요

VR 추락 안전 체험 시뮬레이터를 제어하기 위한 웹 기반 컨트롤러입니다. 이 시스템은 다음을 통합 제어합니다:

- **3대의 Pico 4 VR 헤드셋** - Unity VR 콘텐츠 실행
- **물리적 추락 시뮬레이터** - 실제 낙하 체험 장비
- **웹 컨트롤 인터페이스** - PC에서 모든 장비를 통합 제어

### 주요 기능

- ✅ **통합 제어** - 3대의 VR 헤드셋과 시뮬레이터를 하나의 인터페이스에서 제어
- ✅ **실시간 모니터링** - WebSocket 기반 실시간 상태 확인
- ✅ **ADB 통합** - Pico 4 디바이스 원격 관리 (설치/실행/재부팅)
- ✅ **다크모드 UI** - 현대적이고 직관적인 웹 인터페이스
- ✅ **자동/수동 모드** - Unity Timeline 기반 자동 동기화 또는 수동 제어
- ✅ **테스트 모드** - 시뮬레이터 연결 없이 개발 및 테스트 가능

---

## 🚀 빠른 시작

### 1. 필수 요구사항

- **Python 3.8 이상**
- **ADB (Android Debug Bridge)** - [다운로드](https://developer.android.com/studio/releases/platform-tools)
- **Windows 10/11** (권장)
- **공유기/라우터** - 모든 장비를 같은 네트워크에 연결

### 2. 설치

```bash
# 1. 저장소 클론
git clone https://github.com/sangil1018/VRFallController.git
cd VRFallController

# 2. 가상환경 설정 및 의존성 설치
setup_venv.bat

# 3. ADB 환경 변수 설정 (필요시)
# 시스템 속성 > 환경 변수 > Path에 추가
# 예: C:\platform-tools
```

### 3. 네트워크 설정

> [!IMPORTANT]
> 모든 장비(PC, Pico 4 디바이스, 시뮬레이터)가 **같은 로컬 네트워크**에 연결되어 있어야 합니다.

자세한 네트워크 설정 가이드는 **[NETWORK_SETUP.md](NETWORK_SETUP.md)**를 참조하세요.

**권장 IP 구성:**
- PC: `192.168.1.100`
- Pico 4 #1: `192.168.1.101`
- Pico 4 #2: `192.168.1.102`
- Pico 4 #3: `192.168.1.103`
- 시뮬레이터: `192.168.1.200`

### 4. 실행

#### 일반 모드 (실제 운영)
```bash
start.bat
```

#### 테스트 모드 (시뮬레이터 없이 개발)
```bash
start_test.bat
```

웹 브라우저에서 **http://localhost:8000** 접속

---

## 📂 프로젝트 구조

```
VRFallController/
│
├── 📄 main.py                      # FastAPI 메인 서버
├── 📄 config.py                    # 전역 설정
├── 📄 requirements.txt             # Python 의존성
│
├── 📂 controllers/                 # 컨트롤러 모듈
│   ├── simulator_controller.py    # 시뮬레이터 제어
│   ├── experience_controller.py   # 체험 제어
│   └── adb_controller.py          # ADB 디바이스 관리
│
├── 📂 utils/                       # 유틸리티
│   └── logger.py                   # 로깅 시스템
│
├── 📂 static/                      # 웹 UI
│   ├── index.html                  # 메인 페이지
│   ├── css/style.css              # 스타일시트
│   └── js/app.js                  # 프론트엔드 로직
│
├── 📂 unity_client/                # Unity 연동 스크립트
│   ├── VRControllerClient.cs      # 통신 클라이언트
│   ├── UnityMainThreadDispatcher.cs
│   ├── VRSafetyExperienceManager.cs
│   └── INTEGRATION.md             # Unity 연동 가이드
│
├── 📄 start.bat                    # 일반 모드 실행
├── 📄 start_test.bat              # 테스트 모드 실행
├── 📄 setup_venv.bat              # 가상환경 설정
├── 📄 adb_connect_all.bat         # ADB 자동 연결
│
├── 📘 NETWORK_SETUP.md            # 네트워크 구성 가이드
├── 📘 PROJECT_STRUCTURE.md        # 프로젝트 상세 구조
└── 📘 README.md                   # 이 문서
```

자세한 구조는 **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**를 참조하세요.

---

## 🎮 사용 방법

### 웹 인터페이스

1. **디바이스 관리**
   - 🔄 스캔: Pico 4 디바이스 검색
   - 📱 디바이스 카드: 각 디바이스 상태 표시

2. **체험 제어**
   - ▶️ 시작: 모든 디바이스에서 체험 시작
   - ⏸️ 일시정지/재개: 체험 일시정지 및 재개
   - ⏹️ 종료: 체험 종료 및 초기화

3. **시뮬레이터 제어**
   - 🔌 연결: 시뮬레이터 연결
   - ⬆️ 엘리베이터: 상승 신호 전송
   - ⬇️ 추락: 낙하 신호 전송

### ADB 자동 연결

```bash
# 모든 Pico 4 디바이스 한번에 연결
adb_connect_all.bat

# 연결 확인
adb devices
```

### Unity 연동

Unity 프로젝트에서 PC 컨트롤러와 통신하려면:

1. `unity_client/` 폴더의 C# 스크립트를 Unity 프로젝트에 추가
2. `VRSafetyExperienceManager` 컴포넌트를 Timeline 오브젝트에 추가
3. 자세한 설정은 **[unity_client/INTEGRATION.md](unity_client/INTEGRATION.md)** 참조

---

## ⚙️ 설정

### config.py

```python
# 서버 설정
SERVER_HOST = "0.0.0.0"        # 모든 네트워크 인터페이스
SERVER_PORT = 8000             # 웹 인터페이스 포트
UNITY_CLIENT_PORT = 9100       # Unity 통신 포트

# 시뮬레이터 설정
SIMULATOR_HOST = "192.168.1.200"
SIMULATOR_PORT = 9000

# 디바이스 설정
PICO_DEVICES = [
    "192.168.1.101",
    "192.168.1.102",
    "192.168.1.103"
]

# 테스트 모드
TEST_MODE = False              # True로 설정하면 시뮬레이터 없이 테스트
```

---

## 🔧 문제 해결

### Pico 4 디바이스가 검색되지 않음

1. **ADB 연결 확인**
   ```bash
   adb devices
   ```
   
2. **고정 IP 재설정** (Pico 4 설정에서)
   - Wi-Fi 네트워크 → 고급 옵션 → 고정 IP

3. **방화벽 확인**
   - Windows Defender 방화벽에서 포트 8000, 9100 허용

### 시뮬레이터 연결 실패

1. **IP 주소 확인**
   ```bash
   ping 192.168.1.200
   ```

2. **config.py 수정**
   - `SIMULATOR_HOST`, `SIMULATOR_PORT` 값 확인

3. **프로토콜 구현**
   - 시뮬레이터 제조사 매뉴얼 참조
   - `controllers/simulator_controller.py` 수정 필요

더 자세한 문제 해결은 **[NETWORK_SETUP.md#문제-해결](NETWORK_SETUP.md#문제-해결)**을 참조하세요.

---

## 📡 API 엔드포인트

### 디바이스 관리
- `POST /api/devices/scan` - 디바이스 스캔
- `POST /api/devices/install` - APK 설치
- `POST /api/devices/launch` - 앱 실행
- `POST /api/devices/stop` - 앱 종료
- `POST /api/devices/reboot` - 재부팅

### 체험 제어
- `POST /api/experience/start` - 체험 시작
- `POST /api/experience/pause` - 일시정지
- `POST /api/experience/resume` - 재개
- `POST /api/experience/stop` - 종료
- `POST /api/experience/mode` - 제어 모드 설정 (auto/manual)

### 시뮬레이터 제어
- `POST /api/simulator/connect` - 연결
- `POST /api/simulator/disconnect` - 연결 해제
- `POST /api/simulator/scan` - 스캔
- `POST /api/simulator/elevator_up` - 엘리베이터 상승
- `POST /api/simulator/fall` - 추락 신호

### WebSocket
- `WS /ws` - 실시간 상태 업데이트

---

## 🧪 개발

### 가상환경 활성화

```bash
venv\Scripts\activate
```

### 의존성 추가

```bash
pip install 패키지명
pip freeze > requirements.txt
```

### 테스트 모드 실행

`config.py`에서 `TEST_MODE = True` 설정 또는:

```bash
start_test.bat
```

---

## 📝 라이선스

이 프로젝트는 **MIT 라이선스** 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🤝 기여

이슈 및 풀 리퀘스트는 언제든지 환영합니다!

---

## 📧 문의

- **개발자**: sangil1018
- **Email**: sangil1018@gmail.com
- **GitHub**: [https://github.com/sangil1018/VRFallController](https://github.com/sangil1018/VRFallController)

---

## 🏷️ Topics

`vr` `pico4` `fastapi` `websocket` `python` `unity` `safety-training` `simulator-controller` `adb` `fall-simulator`
