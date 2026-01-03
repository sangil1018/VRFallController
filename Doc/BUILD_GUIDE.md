# 🔧 EXE 빌드 가이드

VRFallController를 독립 실행 가능한 exe 파일로 빌드하는 방법입니다.

---

## 📋 요구사항

- **Python 3.8 이상** (가상환경 설정 완료)
- **PyInstaller** (자동으로 설치됨)
- **모든 프로젝트 의존성** (requirements.txt)

---

## 🚀 빌드 방법

### 방법 1: 자동 빌드 (권장)

```bash
# 빌드 스크립트 실행
build_exe.bat
```

이 스크립트는 다음을 자동으로 수행합니다:
1. ✅ 가상환경 활성화
2. ✅ PyInstaller 설치 (필요시)
3. ✅ 이전 빌드 정리
4. ✅ exe 파일 생성

### 방법 2: 수동 빌드

```bash
# 1. 가상환경 활성화
venv\Scripts\activate

# 2. PyInstaller 설치
pip install pyinstaller

# 3. 빌드 실행
pyinstaller VRFallController.spec
```

---

## 📦 빌드 결과

빌드가 성공하면 다음 구조로 파일이 생성됩니다:

```
VRFallController/
├── dist/
│   └── VRFallController/          # 배포 폴더
│       ├── VRFallController.exe   # 실행 파일 ⭐
│       ├── static/                 # 웹 UI
│       ├── controllers/            # 컨트롤러
│       ├── utils/                  # 유틸리티
│       ├── config.py               # 설정
│       └── [기타 DLL 및 의존성]
└── build/                          # 빌드 임시 파일 (무시 가능)
```

---

## 🎯 실행 방법

### 개발 환경에서 테스트

```bash
# dist 폴더로 이동
cd dist\VRFallController

# 실행 파일 실행
VRFallController.exe
```

> ✨ **자동 브라우저 실행**: exe 파일을 실행하면 자동으로 기본 브라우저에서 **http://localhost:8000**이 열립니다!

수동으로 브라우저를 열어야 하는 경우: **http://localhost:8000** 접속

### 배포

1. **`dist\VRFallController` 폴더 전체**를 복사하여 배포
2. 대상 PC에서 `VRFallController.exe` 실행
3. 브라우저가 자동으로 열립니다 ✅
4. Python 설치 필요 없음 ✅

---

## ⚙️ 빌드 설정 수정

### VRFallController.spec

PyInstaller 빌드 설정 파일입니다. 다음을 수정할 수 있습니다:

#### 1. 콘솔 창 표시/숨김

```python
exe = EXE(
    # ...
    console=True,  # True: 콘솔 표시, False: 콘솔 숨김
    # ...
)
```

- **`console=True`** (기본값): 로그를 볼 수 있어 디버깅 용이
- **`console=False`**: 백그라운드 실행 (프로덕션용)

#### 2. 아이콘 추가

```python
exe = EXE(
    # ...
    icon='icon.ico',  # 아이콘 파일 경로
    # ...
)
```

#### 3. 단일 파일로 빌드

현재는 폴더 형태로 빌드됩니다. 단일 exe 파일로 빌드하려면:

```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,      # 추가
    a.zipfiles,      # 추가
    a.datas,         # 추가
    [],
    exclude_binaries=False,  # True → False로 변경
    name='VRFallController',
    # ...
)

# COLLECT 블록 제거
```

> ⚠️ **주의**: 단일 exe 빌드는 크기가 크고 실행 속도가 느릴 수 있습니다.

---

## 🔍 문제 해결

### 빌드 실패

#### 1. "PyInstaller를 찾을 수 없습니다"

```bash
# 가상환경 활성화 후
pip install pyinstaller
```

#### 2. "모듈을 찾을 수 없습니다"

`VRFallController.spec`의 `hiddenimports`에 누락된 모듈 추가:

```python
hiddenimports=[
    'uvicorn.logging',
    'fastapi',
    # 추가 모듈...
],
```

#### 3. "static 폴더가 누락되었습니다"

`datas` 설정 확인:

```python
datas=[
    ('static', 'static'),
    # ...
],
```

### 실행 오류

#### 1. "config.py를 찾을 수 없습니다"

```bash
# 빌드 전에 config.py가 있는지 확인
dir config.py
```

#### 2. "포트가 이미 사용 중입니다"

다른 인스턴스가 실행 중인지 확인:

```bash
netstat -ano | findstr :8000
```

프로세스 종료:

```bash
taskkill /PID [프로세스_ID] /F
```

---

## 📊 빌드 크기 최적화

### 1. 불필요한 의존성 제거

```bash
# 최소한의 의존성만 설치
pip install -r requirements.txt --no-deps
```

### 2. UPX 압축 활성화

`VRFallController.spec`에서 이미 활성화되어 있습니다:

```python
upx=True,  # 실행 파일 압축
```

### 3. 제외 패키지 추가

```python
excludes=[
    'tkinter',
    'matplotlib',
    'PIL',
    # 사용하지 않는 패키지...
],
```

---

## 🎨 아이콘 생성 (선택사항)

### 온라인 변환 도구 사용

1. **PNG 이미지 준비** (512x512 권장)
2. **[ConvertICO](https://convertio.co/kr/png-ico/)** 등에서 `.ico` 변환
3. 프로젝트 루트에 `icon.ico` 저장
4. `VRFallController.spec` 수정:

```python
icon='icon.ico',
```

---

## 📝 빌드 체크리스트

빌드 전 확인사항:

- [ ] 가상환경 설정 완료 (`setup_venv.bat`)
- [ ] 모든 의존성 설치 (`pip install -r requirements.txt`)
- [ ] 코드 테스트 완료 (`start_test.bat`)
- [ ] `config.py` 설정 확인
- [ ] `static/`, `controllers/`, `utils/` 폴더 존재 확인
- [ ] (선택) 아이콘 파일 준비

빌드 후 확인사항:

- [ ] `dist\VRFallController\VRFallController.exe` 생성 확인
- [ ] exe 파일 실행 테스트
- [ ] 웹 인터페이스 접속 테스트 (http://localhost:8000)
- [ ] 주요 기능 동작 확인

---

## 🚢 배포 가이드

### Windows PC 배포

1. **폴더 압축**
   ```bash
   # PowerShell
   Compress-Archive -Path dist\VRFallController -DestinationPath VRFallController-v1.0.zip
   ```

2. **압축 파일 전달**
   - 이메일, USB, 클라우드 등으로 전송

3. **사용자 설치**
   - 압축 해제
   - `VRFallController.exe` 실행
   - 브라우저에서 http://localhost:8000 접속

### USB 드라이브 배포

1. `dist\VRFallController` 폴더를 USB에 복사
2. USB를 대상 PC에 연결
3. 바로 실행 가능 ✅

---

## 🔄 업데이트

새 버전 배포 시:

1. 코드 수정
2. 빌드 재실행 (`build_exe.bat`)
3. `dist\VRFallController` 폴더 재배포

---

## 📧 문의

빌드 관련 문제가 있으면 이슈를 남겨주세요!

- **GitHub**: [https://github.com/sangil1018/VRFallController](https://github.com/sangil1018/VRFallController)
- **Email**: sangil1018@gmail.com
