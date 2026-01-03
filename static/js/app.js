// WebSocket 연결
let ws = null;
let controlMode = 'auto';
let selectedDevices = new Set();

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    connectWebSocket();
    checkTestMode();
    loadConfig();  // 설정 로드 추가
    log('info', '웹 인터페이스 초기화 완료');
});

// WebSocket 연결
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        log('success', 'WebSocket 연결됨');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };

    ws.onerror = (error) => {
        log('error', 'WebSocket 오류: ' + error);
    };

    ws.onclose = () => {
        log('warning', 'WebSocket 연결 끊김. 5초 후 재연결 시도...');
        setTimeout(connectWebSocket, 5000);
    };
}

// WebSocket 메시지 처리
function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'log':
            log(data.level, data.message);
            break;
        case 'simulator_status':
            updateSimulatorStatus(data.status);
            break;
        case 'devices':
            updateDeviceList(data.devices);
            break;
        case 'test_mode':
            updateTestMode(data.enabled);
            break;
    }
}

// API 요청 함수
async function apiRequest(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`/api/${endpoint}`, options);
        const result = await response.json();

        if (!response.ok) {
            log('error', result.error || '요청 실패');
            return null;
        }

        return result;
    } catch (error) {
        log('error', `API 오류: ${error.message}`);
        return null;
    }
}

// 시뮬레이터 제어
async function connectSimulator() {
    const ip = document.getElementById('simulatorIp').value;
    const port = document.getElementById('simulatorPort').value;

    log('info', `시뮬레이터 연결 시도: ${ip}:${port}`);
    const result = await apiRequest('simulator/connect', 'POST', { ip, port });

    if (result && result.success) {
        log('success', '시뮬레이터 연결 성공');
    }
}

async function disconnectSimulator() {
    log('info', '시뮬레이터 연결 해제 중...');
    await apiRequest('simulator/disconnect', 'POST');
}

async function scanSimulator() {
    log('info', '시뮬레이터 스캔 중...');
    await apiRequest('simulator/scan', 'POST');
}

function updateSimulatorStatus(status) {
    const statusEl = document.getElementById('simulatorStatus');
    statusEl.className = 'status-indicator';

    switch (status) {
        case 'connected':
            statusEl.classList.add('status-connected');
            statusEl.innerHTML = '<span class="status-dot"></span><span>연결됨</span>';
            break;
        case 'disconnected':
            statusEl.classList.add('status-disconnected');
            statusEl.innerHTML = '<span class="status-dot"></span><span>끊김</span>';
            break;
        default:
            statusEl.classList.add('status-waiting');
            statusEl.innerHTML = '<span class="status-dot"></span><span>대기 중</span>';
    }
}

// 체험 제어
async function startExperience() {
    log('info', '체험 시작 신호 전송 중...');
    const result = await apiRequest('experience/start', 'POST');
    if (result && result.success) {
        log('success', '체험 시작됨');
    }
}

async function pauseExperience() {
    log('info', '체험 일시정지 신호 전송 중...');
    const result = await apiRequest('experience/pause', 'POST');
    if (result && result.success) {
        log('success', '체험 일시정지됨');
    }
}

async function resumeExperience() {
    log('info', '체험 재개 신호 전송 중...');
    const result = await apiRequest('experience/resume', 'POST');
    if (result && result.success) {
        log('success', '체험 재개됨');
    }
}

async function stopExperience() {
    log('info', '체험 종료 신호 전송 중...');
    const result = await apiRequest('experience/stop', 'POST');
    if (result && result.success) {
        log('success', '체험 종료됨');
    }
}

// 제어 모드 변경
function setControlMode(mode) {
    controlMode = mode;

    const autoBtn = document.getElementById('autoModeBtn');
    const manualBtn = document.getElementById('manualModeBtn');
    const manualControls = document.getElementById('manualControls');

    if (mode === 'auto') {
        autoBtn.classList.add('active');
        manualBtn.classList.remove('active');
        manualControls.style.display = 'none';
        log('info', '자동 모드로 전환됨');
    } else {
        autoBtn.classList.remove('active');
        manualBtn.classList.add('active');
        manualControls.style.display = 'block';
        log('info', '수동 모드로 전환됨');
    }

    apiRequest('experience/mode', 'POST', { mode });
}

// 수동 제어
async function sendElevatorUp() {
    const time = document.getElementById('elevatorTime').value;
    log('info', `엘리베이터 상승 신호 전송 (${time}초)`);
    const result = await apiRequest('simulator/elevator_up', 'POST', { duration: parseInt(time) });
    if (result && result.success) {
        log('success', '엘리베이터 상승 신호 전송됨');
    }
}

async function sendFall() {
    const time = document.getElementById('fallTime').value;
    log('warning', `추락 신호 전송 (${time}초)`);
    const result = await apiRequest('simulator/fall', 'POST', { duration: parseInt(time) });
    if (result && result.success) {
        log('success', '추락 신호 전송됨');
    }
}

// ADB 디바이스 제어
async function scanDevices() {
    log('info', '피코 디바이스 스캔 중...');
    const result = await apiRequest('devices/scan', 'POST');
    if (result && result.devices) {
        updateDeviceList(result.devices);
        log('success', `${result.devices.length}개 디바이스 발견됨`);
    }
}

function updateDeviceList(devices) {
    const listEl = document.getElementById('deviceList');

    if (devices.length === 0) {
        listEl.innerHTML = '<div class="text-center" style="padding: 2rem; color: var(--gray-400); grid-column: 1 / -1;">디바이스를 찾을 수 없습니다</div>';
        return;
    }

    listEl.innerHTML = devices.map(device => `
        <div class="device-item ${selectedDevices.has(device.ip) ? 'selected' : ''}" onclick="toggleDevice('${device.ip}')">
            <input type="checkbox" class="device-checkbox" ${selectedDevices.has(device.ip) ? 'checked' : ''} onchange="event.stopPropagation(); toggleDevice('${device.ip}')">
            <div class="device-info">
                <div class="device-ip">${device.ip}</div>
                <div class="device-status">${device.status}</div>
            </div>
        </div>
    `).join('');
}

function toggleDevice(ip) {
    if (selectedDevices.has(ip)) {
        selectedDevices.delete(ip);
    } else {
        selectedDevices.add(ip);
    }

    // UI 업데이트
    const deviceItems = document.querySelectorAll('.device-item');
    deviceItems.forEach(item => {
        const itemIp = item.querySelector('.device-ip').textContent;
        if (selectedDevices.has(itemIp)) {
            item.classList.add('selected');
            item.querySelector('.device-checkbox').checked = true;
        } else {
            item.classList.remove('selected');
            item.querySelector('.device-checkbox').checked = false;
        }
    });
}

function getTargetDevices() {
    return selectedDevices.size > 0 ? Array.from(selectedDevices) : 'all';
}

// APK 설치 (전체 또는 선택된 디바이스)
async function installApkToDevices() {
    // 파일 선택 input 엘리먼트 생성
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.apk';

    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const devices = getTargetDevices();
        const deviceCount = devices === 'all' ? '모든' : devices.length + '개';

        if (!confirm(`${file.name}을(를) ${deviceCount} 디바이스에 설치하시겠습니까?\n\n덮어쓰기로 설치됩니다.`)) {
            return;
        }

        log('info', `APK 설치 중: ${file.name} → ${deviceCount} 디바이스`);

        // 실제로는 서버로 파일을 업로드하고 경로를 받아야 함
        // 여기서는 파일 경로를 직접 사용 (로컬 개발 환경)
        const apkPath = file.path || file.name;

        const result = await apiRequest('devices/install', 'POST', { apk_path: apkPath, devices });
        if (result && result.success) {
            log('success', 'APK 설치 완료');
        }
    };

    input.click();
}

// 개별 디바이스에 APK 설치
async function installToSingleDevice(deviceIp) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.apk';

    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        if (!confirm(`${file.name}을(를) ${deviceIp}에 설치하시겠습니까?\n\n덮어쓰기로 설치됩니다.`)) {
            return;
        }

        log('info', `APK 설치 중: ${file.name} → ${deviceIp}`);

        const apkPath = file.path || file.name;

        const result = await apiRequest('devices/install', 'POST', { apk_path: apkPath, devices: [deviceIp] });
        if (result && result.success) {
            log('success', `${deviceIp}에 APK 설치 완료`);
        }
    };

    input.click();
}

async function uninstallApk() {
    const packageName = document.getElementById('packageName').value;
    if (!packageName) {
        log('error', '패키지 이름을 입력하세요');
        return;
    }

    const devices = getTargetDevices();
    log('info', `APK 삭제 중... (대상: ${devices === 'all' ? '모든 디바이스' : devices.length + '개'})`);

    const result = await apiRequest('devices/uninstall', 'POST', { package_name: packageName, devices });
    if (result && result.success) {
        log('success', 'APK 삭제 완료');
    }
}

async function launchApp() {
    const packageName = document.getElementById('packageName').value;
    if (!packageName) {
        log('error', '패키지 이름을 입력하세요');
        return;
    }

    const devices = getTargetDevices();
    log('info', `앱 실행 중... (대상: ${devices === 'all' ? '모든 디바이스' : devices.length + '개'})`);

    const result = await apiRequest('devices/launch', 'POST', { package_name: packageName, devices });
    if (result && result.success) {
        log('success', '앱 실행 완료');
    }
}

async function stopApp() {
    const packageName = document.getElementById('packageName').value;
    if (!packageName) {
        log('error', '패키지 이름을 입력하세요');
        return;
    }

    const devices = getTargetDevices();
    log('info', `앱 종료 중... (대상: ${devices === 'all' ? '모든 디바이스' : devices.length + '개'})`);

    const result = await apiRequest('devices/stop', 'POST', { package_name: packageName, devices });
    if (result && result.success) {
        log('success', '앱 종료 완료');
    }
}

async function rebootDevices() {
    if (!confirm('선택된 디바이스를 재부팅하시겠습니까?')) {
        return;
    }

    const devices = getTargetDevices();
    log('warning', `디바이스 재부팅 중... (대상: ${devices === 'all' ? '모든 디바이스' : devices.length + '개'})`);

    const result = await apiRequest('devices/reboot', 'POST', { devices });
    if (result && result.success) {
        log('success', '디바이스 재부팅 시작됨');
    }
}

// 로그 함수
function log(level, message) {
    const logWindow = document.getElementById('logWindow');
    const time = new Date().toLocaleTimeString('ko-KR');

    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `
        <span class="log-time">${time}</span>
        <span class="log-message log-${level}">${message}</span>
    `;

    logWindow.appendChild(entry);
    logWindow.scrollTop = logWindow.scrollHeight;

    // 최대 로그 개수 제한
    while (logWindow.children.length > 1000) {
        logWindow.removeChild(logWindow.firstChild);
    }
}

function clearLogs() {
    const logWindow = document.getElementById('logWindow');
    logWindow.innerHTML = '';
    log('info', '로그가 지워졌습니다');
}

// 테스트 모드 확인
async function checkTestMode() {
    const result = await apiRequest('test_mode');
    if (result && result.enabled) {
        updateTestMode(true);
    }
}

// 설정 로드
async function loadConfig() {
    const result = await apiRequest('config');
    if (result) {
        // 패키지 이름 설정
        if (result.package_name) {
            document.getElementById('packageName').value = result.package_name;
        }

        // 시뮬레이터 IP/포트 설정
        if (result.simulator_host) {
            document.getElementById('simulatorIp').value = result.simulator_host;
        }
        if (result.simulator_port) {
            document.getElementById('simulatorPort').value = result.simulator_port;
        }

        log('success', '설정 로드 완료');
    }
}

function updateTestMode(enabled) {
    const badge = document.getElementById('testModeBadge');
    badge.style.display = enabled ? 'block' : 'none';

    if (enabled) {
        log('warning', '⚠️ 테스트 모드 활성화됨');
    }
}
