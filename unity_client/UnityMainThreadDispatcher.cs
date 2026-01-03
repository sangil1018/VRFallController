using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Unity 메인 스레드에서 작업을 실행하기 위한 디스패처
/// 백그라운드 스레드에서 Unity API 호출 시 필요
/// </summary>
public class UnityMainThreadDispatcher : MonoBehaviour
{
    private static UnityMainThreadDispatcher _instance;
    private readonly Queue<Action> _executionQueue = new Queue<Action>();
    
    public static UnityMainThreadDispatcher Instance
    {
        get
        {
            if (_instance == null)
            {
                // 씬에 있는 디스패처 찾기
                _instance = FindObjectOfType<UnityMainThreadDispatcher>();
                
                // 없으면 새로 생성
                if (_instance == null)
                {
                    GameObject obj = new GameObject("UnityMainThreadDispatcher");
                    _instance = obj.AddComponent<UnityMainThreadDispatcher>();
                    DontDestroyOnLoad(obj);
                }
            }
            return _instance;
        }
    }
    
    private void Awake()
    {
        if (_instance == null)
        {
            _instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else if (_instance != this)
        {
            Destroy(gameObject);
        }
    }
    
    private void Update()
    {
        // 큐에 있는 작업을 메인 스레드에서 실행
        lock (_executionQueue)
        {
            while (_executionQueue.Count > 0)
            {
                _executionQueue.Dequeue()?.Invoke();
            }
        }
    }
    
    /// <summary>
    /// 메인 스레드에서 실행할 작업을 큐에 추가
    /// </summary>
    public void Enqueue(Action action)
    {
        if (action == null)
            return;
            
        lock (_executionQueue)
        {
            _executionQueue.Enqueue(action);
        }
    }
}
