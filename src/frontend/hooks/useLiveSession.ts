import { useState, useRef, useCallback } from 'react';
import { config } from '../config';
import { getSession } from '../utils/session';

export interface DetectedObject {
  class_name: string;
  confidence: number;
  bbox: [number, number, number, number]; // [x1, y1, x2, y2] normalized [0-1]
  track_id: number | null;
}

export type SessionStatus =
  | 'idle'
  | 'connecting'
  | 'streaming'
  | 'processing'
  | 'speaking'
  | 'error';

interface LiveSessionState {
  status: SessionStatus;
  errorMessage: string | null;
  isSendingFrame: boolean;
  isPlayingAudio: boolean;
  detections: DetectedObject[];
}

export function useLiveSession() {
  const wsRef = useRef<WebSocket | null>(null);
  const [state, setState] = useState<LiveSessionState>({
    status: 'idle',
    errorMessage: null,
    isSendingFrame: false,
    isPlayingAudio: false,
    detections: [],
  });

  const start = useCallback(async () => {
    try {
      setState({
        status: 'connecting',
        errorMessage: null,
        isSendingFrame: false,
        isPlayingAudio: false,
        detections: [],
      });

      const sessionId = await getSession();
      if (!sessionId) throw new Error('No active session');

      const wsUrl = `${config.backend.ws.url}/ws/live/${sessionId}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setState((prev) => ({ ...prev, status: 'streaming' }));
      };

      ws.onmessage = (_event) => {
        try {
          const msg = JSON.parse(_event.data);
          if (msg.type === 'status') {
            //connection status - no action needed, server just confirmed the opening of the websocket
          } else if (msg.type === 'error') {
            setState((prev) => ({ ...prev, status: 'error', errorMessage: msg.message }));
          } else if (msg.type === 'detection') {
            setState((prev) => ({ ...prev, detections: msg.objects || [] }));
          } else if (msg.type === 'alert') {
            setState((prev) => ({
              ...prev,
              status: prev.status === 'error' ? 'error' : 'streaming',
            }));
          }
        } catch {
          //ignore malformed messages
        }
      };

      ws.onerror = () => {
        setState((prev) => ({
          ...prev,
          status: 'error',
          errorMessage: 'Connection failed',
          isSendingFrame: false,
          detections: [],
        }));
      };

      ws.onclose = () => {
        setState((prev) => ({
          ...prev,
          status: prev.status === 'error' ? 'error' : 'idle',
          isSendingFrame: false,
          isPlayingAudio: false,
          detections: [],
        }));
      };
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        status: 'error',
        errorMessage: err.message || 'Failed to start session',
        detections: [],
      }));
    }
  }, []);

  const stop = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setState({
      status: 'idle',
      errorMessage: null,
      isSendingFrame: false,
      isPlayingAudio: false,
      detections: [],
    });
  }, []);

  const sendFrame = useCallback((frameData: string) => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    setState((prev) => ({ ...prev, isSendingFrame: true }));
    ws.send(JSON.stringify({ type: 'frame', data: frameData, timestamp: Date.now() }));
    setState((prev) => ({ ...prev, isSendingFrame: false, status: 'processing' }));
  }, []);

  return { ...state, start, stop, sendFrame };
}
