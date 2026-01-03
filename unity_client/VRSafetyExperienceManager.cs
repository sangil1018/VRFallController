using UnityEngine;
using UnityEngine.Playables;

/// <summary>
/// VR 안전 체험 매니저 - Timeline 제어 및 신호 전송
/// </summary>
public class VRSafetyExperienceManager : MonoBehaviour
{
    [Header("컴포넌트")]
    public VRControllerClient controllerClient;
    public PlayableDirector timeline;
    
    [Header("자동 모드 설정")]
    [Tooltip("자동 모드 활성화 (피코 #1만 해당)")]
    public bool isAutoMode = false;
    
    [Tooltip("이 디바이스가 피코 #1인지 여부")]
    public bool isPrimary = false;
    
    [Header("Timeline 마커")]
    [Tooltip("엘리베이터 상승 시작 시간 (초)")]
    public float elevatorUpTime = 5f;
    
    [Tooltip("엘리베이터 상승 지속 시간 (초)")]
    public float elevatorDuration = 5f;
    
    [Tooltip("추락 시작 시간 (초)")]
    public float fallTime = 15f;
    
    [Tooltip("추락 지속 시간 (초)")]
    public float fallDuration = 3f;
    
    private bool isPlaying = false;
    private bool hasElevatorSignalSent = false;
    private bool hasFallSignalSent = false;
    
    private void Start()
    {
        // 컨트롤러 클라이언트 이벤트 구독
        if (controllerClient != null)
        {
            controllerClient.OnCommandReceived += OnCommandReceived;
        }
        
        // Timeline 초기화
        if (timeline != null)
        {
            timeline.stopped += OnTimelineStopped;
        }
    }
    
    private void Update()
    {
        // 자동 모드 && 피코 #1 && Timeline 재생 중
        if (isAutoMode && isPrimary && isPlaying && timeline != null)
        {
            double currentTime = timeline.time;
            
            // 엘리베이터 상승 신호
            if (!hasElevatorSignalSent && currentTime >= elevatorUpTime)
            {
                hasElevatorSignalSent = true;
                controllerClient?.SendElevatorUpSignal(elevatorDuration);
                Debug.Log($"[ExperienceManager] 엘리베이터 상승 신호 전송 ({elevatorDuration}초)");
            }
            
            // 추락 신호
            if (!hasFallSignalSent && currentTime >= fallTime)
            {
                hasFallSignalSent = true;
                controllerClient?.SendFallSignal(fallDuration);
                Debug.Log($"[ExperienceManager] 추락 신호 전송 ({fallDuration}초)");
            }
        }
    }
    
    /// <summary>
    /// PC 컨트롤러로부터 명령 수신
    /// </summary>
    private void OnCommandReceived(VRCommand command)
    {
        switch (command.command)
        {
            case "PLAY":
                StartExperience();
                break;
                
            case "PAUSE":
                PauseExperience();
                break;
                
            case "RESUME":
                ResumeExperience();
                break;
                
            case "STOP":
                StopExperience();
                break;
        }
    }
    
    /// <summary>
    /// 체험 시작
    /// </summary>
    public void StartExperience()
    {
        if (timeline == null)
        {
            Debug.LogError("[ExperienceManager] Timeline이 설정되지 않았습니다!");
            return;
        }
        
        Debug.Log("[ExperienceManager] 체험 시작");
        
        // 플래그 초기화
        hasElevatorSignalSent = false;
        hasFallSignalSent = false;
        
        // Timeline 재생
        timeline.time = 0;
        timeline.Play();
        isPlaying = true;
    }
    
    /// <summary>
    /// 체험 일시정지
    /// </summary>
    public void PauseExperience()
    {
        if (timeline == null) return;
        
        Debug.Log("[ExperienceManager] 일시정지");
        timeline.Pause();
        isPlaying = false;
    }
    
    /// <summary>
    /// 체험 재개
    /// </summary>
    public void ResumeExperience()
    {
        if (timeline == null) return;
        
        Debug.Log("[ExperienceManager] 재개");
        timeline.Resume();
        isPlaying = true;
    }
    
    /// <summary>
    /// 체험 종료 및 초기화
    /// </summary>
    public void StopExperience()
    {
        if (timeline == null) return;
        
        Debug.Log("[ExperienceManager] 종료");
        
        timeline.Stop();
        timeline.time = 0;
        isPlaying = false;
        
        // 플래그 초기화
        hasElevatorSignalSent = false;
        hasFallSignalSent = false;
    }
    
    /// <summary>
    /// Timeline 종료 이벤트
    /// </summary>
    private void OnTimelineStopped(PlayableDirector director)
    {
        Debug.Log("[ExperienceManager] Timeline 재생 완료");
        isPlaying = false;
        
        // 자동으로 초기화
        timeline.time = 0;
        hasElevatorSignalSent = false;
        hasFallSignalSent = false;
    }
    
    private void OnDestroy()
    {
        // 이벤트 구독 해제
        if (controllerClient != null)
        {
            controllerClient.OnCommandReceived -= OnCommandReceived;
        }
        
        if (timeline != null)
        {
            timeline.stopped -= OnTimelineStopped;
        }
    }
}
