# Unity 클라이언트 연동 가이드

VR 추락 시뮬레이터 PC 컨트롤러와 Unity VR 앱을 연동하는 방법입니다.

## 📋 목차

1. [개요](#개요)
2. [스크립트 설치](#스크립트-설치)
3. [씬 설정](#씬-설정)
4. [자동 모드 vs 수동 모드](#자동-모드-vs-수동-모드)
5. [통신 프로토콜](#통신-프로토콜)
6. [테스트](#테스트)
7. [문제 해결](#문제-해결)

---

## 개요

Unity VR 앱은 PC 컨트롤러와 **TCP 소켓**으로 통신합니다.

### 통신 구조

```
PC 컨트롤러 (192.168.1.100:9100)
        ↕ TCP
Unity VR 앱 (피코4)
        ↕
Timeline (VR 체험)
```

### 제공 스크립트

| 스크립트 | 설명 |
|---------|------|
| `VRControllerClient.cs` | PC 컨트롤러 통신 클라이언트 |
| `UnityMainThreadDispatcher.cs` | 백그라운드 스레드 → 메인 스레드 브릿지 |
| `VRSafetyExperienceManager.cs` | Timeline 제어 및 신호 전송 매니저 |

---

## 스크립트 설치

### 1. 스크립트 파일 복사

`unity_client` 폴더의 모든 `.cs` 파일을 Unity 프로젝트로 복사:

```
YourUnityProject/
└── Assets/
    └── Scripts/
        ├── VRControllerClient.cs
        ├── UnityMainThreadDispatcher.cs
        └── VRSafetyExperienceManager.cs
```

### 2. Unity 설정

Unity 에디터에서:
1. **Player Settings** → **API Compatibility Level** → **.NET 4.x** 이상
2. **Player Settings** → **Allow 'unsafe' Code** → ✅ (필요시)

---

## 씬 설정

### 1. 기본 오브젝트 생성

Hierarchy에서:

```
Scene
├── VRControllerManager  (빈 GameObject)
│   ├── VRControllerClient (컴포넌트)
│   └── UnityMainThreadDispatcher (컴포넌트)
│
└── ExperienceManager  (빈 GameObject)
    └── VRSafetyExperienceManager (컴포넌트)
```

### 2. VRControllerClient 설정

**Inspector 설정:**

| 필드 | 값 | 설명 |
|------|-----|------|
| **Server IP** | `192.168.1.100` | PC 컨트롤러 IP |
| **Server Port** | `9100` | 통신 포트 |
| **Auto Reconnect** | ✅ | 자동 재연결 활성화 |
| **Reconnect Interval** | `5` | 재연결 시도 간격 (초) |

![VRControllerClient 설정](https://via.placeholder.com/600x200/1e293b/10b981?text=VRControllerClient+Settings)

### 3. VRSafetyExperienceManager 설정

**Inspector 설정:**

| 필드 | 값 | 설명 |
|------|-----|------|
| **Controller Client** | VRControllerClient 참조 | 드래그 앤 드롭 |
| **Timeline** | PlayableDirector 참조 | Timeline 컴포넌트 |
| **Is Auto Mode** | ✅ / ☐ | 자동 모드 활성화 |
| **Is Primary** | ✅ / ☐ | 피코 #1 여부 |
| **Elevator Up Time** | `5` | 엘리베이터 상승 시작 시간 (초) |
| **Elevator Duration** | `5` | 상승 지속 시간 (초) |
| **Fall Time** | `15` | 추락 시작 시간 (초) |
| **Fall Duration** | `3` | 추락 지속 시간 (초) |

> [!IMPORTANT]
> **피코4 #1**만 `Is Auto Mode`와 `Is Primary`를 모두 체크하세요!

---

## 자동 모드 vs 수동 모드

### 자동 모드 🤖

**피코4 #1**이 Unity Timeline 재생 중 자동으로 시뮬레이터 제어 신호를 전송합니다.

**설정:**
- 피코4 #1: `Is Auto Mode = ✅`, `Is Primary = ✅`
- 피코4 #2, #3: `Is Auto Mode = ☐`, `Is Primary = ☐`

**동작 흐름:**
```
1. PC 앱에서 "체험 시작" 클릭
2. 모든 피코4에 PLAY 신호 전송
3. Unity Timeline 재생 시작
4. 피코4 #1이 Timeline 시간 체크
5. elevatorUpTime 도달 → 엘리베이터 상승 신호 전송
6. fallTime 도달 → 추락 신호 전송
7. PC 앱이 신호 받아 시뮬레이터 제어
```

### 수동 모드 🎛️

PC 앱에서 직접 버튼으로 시뮬레이터를 제어합니다.

**설정:**
- 모든 피코4: `Is Auto Mode = ☐`

**동작 흐름:**
```
1. PC 앱에서 "체험 시작" 클릭
2. 모든 피코4에 PLAY 신호 전송
3. Unity Timeline 재생 시작
4. PC 앱에서 "⬆️ 상승" 버튼 클릭 → 시뮬레이터 제어
5. PC 앱에서 "⬇️ 추락" 버튼 클릭 → 시뮬레이터 제어
```

---

## 통신 프로토콜

### PC → Unity (명령)

Unity가 수신하는 JSON 메시지:

#### 체험 시작
```json
{
  "command": "PLAY"
}
```

#### 일시정지
```json
{
  "command": "PAUSE"
}
```

#### 재개
```json
{
  "command": "RESUME"
}
```

#### 종료
```json
{
  "command": "STOP"
}
```

### Unity → PC (신호, 자동 모드)

피코4 #1이 전송하는 JSON 메시지:

#### 엘리베이터 상승
```json
{
  "command": "ELEVATOR_UP",
  "data": {
    "duration": 5.0
  }
}
```

#### 추락
```json
{
  "command": "FALL",
  "data": {
    "duration": 3.0
  }
}
```

---

## 코드 예제

### 이벤트 구독

```csharp
using UnityEngine;

public class MyCustomController : MonoBehaviour
{
    public VRControllerClient client;
    
    private void Start()
    {
        // 연결 이벤트
        client.OnConnected += () => {
            Debug.Log("PC 컨트롤러 연결됨!");
        };
        
        // 연결 해제 이벤트
        client.OnDisconnected += () => {
            Debug.Log("PC 컨트롤러 연결 끊김!");
        };
        
        // 명령 수신 이벤트
        client.OnCommandReceived += (command) => {
            Debug.Log($"명령 수신: {command.command}");
        };
    }
}
```

### 수동 신호 전송

```csharp
// 엘리베이터 상승 신호 (5초)
client.SendElevatorUpSignal(5f);

// 추락 신호 (3초)
client.SendFallSignal(3f);
```

### Timeline 제어

```csharp
public VRSafetyExperienceManager manager;

// 체험 시작
manager.StartExperience();

// 일시정지
manager.PauseExperience();

// 재개
manager.ResumeExperience();

// 종료
manager.StopExperience();
```

---

## 테스트

### 1. Unity 에디터에서 테스트

1. PC 컨트롤러 앱 실행 (`start_test.bat`)
2. Unity Play 모드 진입
3. 브라우저에서 `http://localhost:8000` 접속
4. "체험 시작" 버튼 클릭
5. Unity 콘솔에서 로그 확인

**예상 로그:**
```
[VRController] 연결 시도: 192.168.1.100:9100
[VRController] 연결 성공!
[VRController] 명령 수신: PLAY
[ExperienceManager] 체험 시작
```

### 2. 피코4 실제 디바이스 테스트

1. Unity 프로젝트 빌드 (Android / Pico)
2. APK를 피코4에 설치
3. PC와 피코4를 같은 네트워크에 연결
4. VRControllerClient의 Server IP를 PC IP로 설정
5. APK 실행 후 PC 앱에서 제어

---

## 문제 해결

### ❌ Unity 콘솔에 "연결 실패" 오류

**원인:**
- PC와 피코4가 다른 네트워크
- PC IP가 잘못됨
- 방화벽 차단

**해결:**
1. PC IP 확인:
   ```cmd
   ipconfig
   ```
2. `VRControllerClient.serverIP`를 PC IP로 수정
3. Windows 방화벽에서 포트 9100 허용

### ❌ "메시지 처리 오류" 로그

**원인:**
- JSON 형식 오류
- Unity JsonUtility 제한

**해결:**
1. PC 앱의 로그 확인 (`vr_controller.log`)
2. JSON 형식이 올바른지 확인
3. 필요시 `VRCommand` 클래스 수정

### ❌ Timeline이 재생되지 않음

**원인:**
- PlayableDirector 참조 누락
- Timeline Asset 미설정

**해결:**
1. `VRSafetyExperienceManager.timeline`에 PlayableDirector 할당
2. PlayableDirector에 Timeline Asset 할당
3. Inspector에서 참조 확인

### ❌ 자동 모드에서 신호가 전송되지 않음

**원인:**
- `Is Auto Mode` 또는 `Is Primary` 미체크
- Timeline 시간 설정 오류

**해결:**
1. 피코4 #1: `Is Auto Mode = ✅`, `Is Primary = ✅` 확인
2. `Elevator Up Time`, `Fall Time` 값 확인
3. Timeline 길이가 충분한지 확인

---

## 추가 커스터마이징

### 새로운 명령 추가

1. `VRCommand` 클래스에 새 필드 추가 (필요시)
2. `VRControllerClient.HandleCommand()` 수정:

```csharp
case "MY_CUSTOM_COMMAND":
    Debug.Log("커스텀 명령 처리");
    // 처리 로직
    break;
```

3. PC 앱 (`main.py`, `app.js`)에서 명령 전송 추가

### Timeline Markers 사용

Unity Timeline의 Marker를 사용하여 더 정밀한 신호 전송:

```csharp
using UnityEngine.Timeline;

public void OnNotification(Playable origin, INotification notification, object context)
{
    if (notification is SignalEmitter signal)
    {
        // Marker에서 신호 전송
        client.SendElevatorUpSignal(5f);
    }
}
```

---

## 참고 자료

- **PC 컨트롤러 README**: [`../README.md`](../README.md)
- **네트워크 설정 가이드**: [`../NETWORK_SETUP.md`](../NETWORK_SETUP.md)
- **Unity Timeline 문서**: https://docs.unity3d.com/Packages/com.unity.timeline@latest

---

## 요약 체크리스트

설정 완료 후 확인:

- [ ] 3개 스크립트 파일을 Unity 프로젝트에 복사
- [ ] VRControllerManager GameObject와 컴포넌트 추가
- [ ] ExperienceManager GameObject와 컴포넌트 추가
- [ ] VRControllerClient에 PC IP 설정 (192.168.1.100)
- [ ] VRSafetyExperienceManager에 Timeline 참조 연결
- [ ] 피코4 #1만 Auto Mode + Primary 체크
- [ ] Unity 에디터에서 연결 테스트 성공
- [ ] Timeline 재생 확인
- [ ] PC 앱에서 명령 수신 확인

---

**Happy Coding! 🎮**
