import { useState, useRef, useCallback } from 'react';
import { config } from '../config';
import { getSession } from '../utils/session';

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
}

export function useLiveSession() {
  const wsRef = useRef<WebSocket | null>(null);
  const [state, setState] = useState<LiveSessionState>({
    status: 'idle',
    errorMessage: null,
    isSendingFrame: false,
    isPlayingAudio: false,
  });

  const start = useCallback(async () => {
    try {
      setState({
        status: 'connecting',
        errorMessage: null,
        isSendingFrame: false,
        isPlayingAudio: false,
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
        // TODO: parse message and play audio when audio library is decided
        // Expected backend message format: { type: 'audio', data: '<base64_audio>', format: 'mp3' | 'pcm' }
        setState((prev) => ({ ...prev, status: 'speaking', isPlayingAudio: true }));
        // Placeholder: return to streaming after simulated playback delay
        setTimeout(() => {
          setState((prev) => ({ ...prev, status: 'streaming', isPlayingAudio: false }));
        }, 1500);
      };

      ws.onerror = () => {
        setState((prev) => ({
          ...prev,
          status: 'error',
          errorMessage: 'Connection failed',
          isSendingFrame: false,
        }));
      };

      ws.onclose = () => {
        setState((prev) => ({
          ...prev,
          status: prev.status === 'error' ? 'error' : 'idle',
          isSendingFrame: false,
          isPlayingAudio: false,
        }));
      };
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        status: 'error',
        errorMessage: err.message || 'Failed to start session',
      }));
    }
  }, []);

  const stop = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setState({ status: 'idle', errorMessage: null, isSendingFrame: false, isPlayingAudio: false });
  }, []);

  const sendFrame = useCallback((frameData: string) => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    setState((prev) => ({ ...prev, isSendingFrame: true }));
    ws.send(JSON.stringify({ type: 'frame', data: frameData }));
    setState((prev) => ({ ...prev, isSendingFrame: false, status: 'processing' }));
  }, []);

  return { ...state, start, stop, sendFrame };
}
