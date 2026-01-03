using System;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

/// <summary>
/// VR 추락 시뮬레이터 PC 컨트롤러와 통신하는 클라이언트
/// </summary>
public class VRControllerClient : MonoBehaviour
{
    [Header("서버 설정")]
    [Tooltip("PC 컨트롤러 IP 주소")]
    public string serverIP = "192.168.1.100";
    
    [Tooltip("PC 컨트롤러 포트")]
    public int serverPort = 9100;
    
    [Header("연결 상태")]
    public bool isConnected = false;
    
    [Header("자동 재연결")]
    public bool autoReconnect = true;
    public float reconnectInterval = 5f;
    
    // TCP 클라이언트
    private TcpClient client;
    private NetworkStream stream;
    private bool isReceiving = false;
    private float reconnectTimer = 0f;
    
    // 이벤트
    public event Action OnConnected;
    public event Action OnDisconnected;
    public event Action<VRCommand> OnCommandReceived;
    
    private void Start()
    {
        ConnectToServer();
    }
    
    private void Update()
    {
        // 자동 재연결
        if (autoReconnect && !isConnected)
        {
            reconnectTimer += Time.deltaTime;
            if (reconnectTimer >= reconnectInterval)
            {
                reconnectTimer = 0f;
                ConnectToServer();
            }
        }
    }
    
    /// <summary>
    /// PC 컨트롤러 서버에 연결
    /// </summary>
    public async void ConnectToServer()
    {
        try
        {
            Debug.Log($"[VRController] 연결 시도: {serverIP}:{serverPort}");
            
            client = new TcpClient();
            await client.ConnectAsync(serverIP, serverPort);
            
            stream = client.GetStream();
            isConnected = true;
            
            Debug.Log($"[VRController] 연결 성공!");
            OnConnected?.Invoke();
            
            // 메시지 수신 시작
            if (!isReceiving)
            {
                isReceiving = true;
                _ = ReceiveMessages();
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[VRController] 연결 실패: {e.Message}");
            isConnected = false;
            OnDisconnected?.Invoke();
        }
    }
    
    /// <summary>
    /// 서버로부터 메시지 수신 (백그라운드)
    /// </summary>
    private async Task ReceiveMessages()
    {
        byte[] buffer = new byte[1024];
        
        while (isConnected && client != null && stream != null)
        {
            try
            {
                int bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length);
                
                if (bytesRead > 0)
                {
                    string message = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                    ProcessMessage(message);
                }
                else
                {
                    // 연결 끊김
                    Disconnect();
                    break;
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[VRController] 수신 오류: {e.Message}");
                Disconnect();
                break;
            }
        }
        
        isReceiving = false;
    }
    
    /// <summary>
    /// 수신한 JSON 메시지 처리
    /// </summary>
    private void ProcessMessage(string message)
    {
        try
        {
            // JSON 파싱
            VRCommand command = JsonUtility.FromJson<VRCommand>(message);
            
            Debug.Log($"[VRController] 명령 수신: {command.command}");
            
            // 메인 스레드에서 이벤트 발생
            UnityMainThreadDispatcher.Instance.Enqueue(() =>
            {
                OnCommandReceived?.Invoke(command);
                HandleCommand(command);
            });
        }
        catch (Exception e)
        {
            Debug.LogError($"[VRController] 메시지 처리 오류: {e.Message}\n메시지: {message}");
        }
    }
    
    /// <summary>
    /// 명령 처리
    /// </summary>
    private void HandleCommand(VRCommand command)
    {
        switch (command.command)
        {
            case "PLAY":
                Debug.Log("[VRController] 체험 시작");
                // TODO: Timeline 재생 시작
                break;
                
            case "PAUSE":
                Debug.Log("[VRController] 일시정지");
                // TODO: Timeline 일시정지
                break;
                
            case "RESUME":
                Debug.Log("[VRController] 재개");
                // TODO: Timeline 재개
                break;
                
            case "STOP":
                Debug.Log("[VRController] 종료");
                // TODO: Timeline 정지 및 초기화
                break;
                
            default:
                Debug.LogWarning($"[VRController] 알 수 없는 명령: {command.command}");
                break;
        }
    }
    
    /// <summary>
    /// PC 컨트롤러로 신호 전송 (자동 모드용)
    /// </summary>
    public async void SendSignal(string signalType, float duration = 0f)
    {
        if (!isConnected)
        {
            Debug.LogWarning("[VRController] 연결되지 않음");
            return;
        }
        
        try
        {
            VRSignal signal = new VRSignal
            {
                command = signalType,
                data = new SignalData { duration = duration }
            };
            
            string json = JsonUtility.ToJson(signal) + "\n";
            byte[] data = Encoding.UTF8.GetBytes(json);
            
            await stream.WriteAsync(data, 0, data.Length);
            Debug.Log($"[VRController] 신호 전송: {signalType} ({duration}초)");
        }
        catch (Exception e)
        {
            Debug.LogError($"[VRController] 전송 오류: {e.Message}");
            Disconnect();
        }
    }
    
    /// <summary>
    /// 엘리베이터 상승 신호 전송
    /// </summary>
    public void SendElevatorUpSignal(float duration = 5f)
    {
        SendSignal("ELEVATOR_UP", duration);
    }
    
    /// <summary>
    /// 추락 신호 전송
    /// </summary>
    public void SendFallSignal(float duration = 3f)
    {
        SendSignal("FALL", duration);
    }
    
    /// <summary>
    /// 연결 해제
    /// </summary>
    public void Disconnect()
    {
        if (isConnected)
        {
            Debug.Log("[VRController] 연결 해제");
            isConnected = false;
            
            stream?.Close();
            client?.Close();
            
            OnDisconnected?.Invoke();
        }
    }
    
    private void OnDestroy()
    {
        Disconnect();
    }
    
    private void OnApplicationQuit()
    {
        Disconnect();
    }
}

/// <summary>
/// PC 컨트롤러로부터 수신하는 명령
/// </summary>
[Serializable]
public class VRCommand
{
    public string command;
    public CommandData data;
}

[Serializable]
public class CommandData
{
    // 필요시 추가 데이터
}

/// <summary>
/// PC 컨트롤러로 전송하는 신호 (자동 모드)
/// </summary>
[Serializable]
public class VRSignal
{
    public string command;
    public SignalData data;
}

[Serializable]
public class SignalData
{
    public float duration;
}
