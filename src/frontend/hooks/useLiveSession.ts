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

export interface FrameTelemetry {
  frame_id: string;
  capture_started_at: number;
  capture_finished_at: number;
  encode_finished_at: number;
  sent_at?: number;
}

export interface DetectionTelemetry {
  frame_id: string | null;
  capture_started_at: number | null;
  capture_finished_at: number | null;
  encode_finished_at: number | null;
  sent_at: number | null;
  server_received_at: number;
  server_responded_at: number;
  processing_ms: number;
}

interface DetectionRenderTelemetry {
  frameId: string;
  captureStartedAt: number;
  receivedAt: number;
}

interface SendFrameInput {
  frameData: string;
  telemetry: Omit<FrameTelemetry, 'sent_at'>;
}

interface LiveSessionState {
  status: SessionStatus;
  errorMessage: string | null;
  isSendingFrame: boolean;
  isPlayingAudio: boolean;
  detections: DetectedObject[];
  lastDetectionTelemetry: DetectionRenderTelemetry | null;
}

export function useLiveSession() {
  const wsRef = useRef<WebSocket | null>(null);
  const frameInFlightRef = useRef(false);

  const [state, setState] = useState<LiveSessionState>({
    status: 'idle',
    errorMessage: null,
    isSendingFrame: false,
    isPlayingAudio: false,
    detections: [],
    lastDetectionTelemetry: null,
  });

  const start = useCallback(async () => {
    try {
      frameInFlightRef.current = false;
      setState({
        status: 'connecting',
        errorMessage: null,
        isSendingFrame: false,
        isPlayingAudio: false,
        detections: [],
        lastDetectionTelemetry: null,
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
            return;
            //connection status - no action needed, server just confirmed the opening of the websocket
          }

          if (msg.type === 'error') {
            frameInFlightRef.current = false;
            setState((prev) => ({
              ...prev,
              status: 'error',
              errorMessage: msg.message,
              isSendingFrame: false,
              lastDetectionTelemetry: null,
            }));
            return;
          }

          if (msg.type === 'detection') {
            frameInFlightRef.current = false;
            const receivedAt = Date.now();
            const telemetry = msg.telemetry as DetectionTelemetry | undefined;

            if (
              telemetry?.frame_id &&
              telemetry.capture_started_at !== null &&
              telemetry.capture_finished_at !== null &&
              telemetry.encode_finished_at !== null &&
              telemetry.sent_at !== null
            ) {
              const captureMs = telemetry.capture_finished_at - telemetry.capture_started_at;
              const encodeMs = telemetry.encode_finished_at - telemetry.capture_finished_at;
              const networkToServerMs = telemetry.server_received_at - telemetry.sent_at;
              const backendToClientMs = receivedAt - telemetry.server_responded_at;
              const roundtripMs = receivedAt - telemetry.sent_at;
              const endToEndMsBeforePaint = receivedAt - telemetry.capture_started_at;

              console.log('[live][timing][response]', {
                frameId: telemetry.frame_id,
                captureMs,
                encodeMs,
                networkToServerMs,
                backendProcessingMs: telemetry.processing_ms,
                backendToClientMs,
                roundtripMs,
                endToEndMsBeforePaint,
              });
            }

            setState((prev) => ({
              ...prev,
              detections: msg.objects || [],
              isSendingFrame: false,
              status: 'streaming',
              lastDetectionTelemetry:
                telemetry?.frame_id && telemetry.capture_started_at !== null
                  ? {
                      frameId: telemetry.frame_id,
                      captureStartedAt: telemetry.capture_started_at,
                      receivedAt,
                    }
                  : null,
            }));
            return;
          }

          if (msg.type === 'alert') {
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
        frameInFlightRef.current = false;

        setState((prev) => ({
          ...prev,
          status: 'error',
          errorMessage: 'Connection failed',
          isSendingFrame: false,
          detections: [],
          lastDetectionTelemetry: null,
        }));
      };

      ws.onclose = () => {
        frameInFlightRef.current = false;

        setState((prev) => ({
          ...prev,
          status: prev.status === 'error' ? 'error' : 'idle',
          isSendingFrame: false,
          isPlayingAudio: false,
          detections: [],
          lastDetectionTelemetry: null,
        }));
      };
    } catch (err: any) {
      frameInFlightRef.current = false;

      setState((prev) => ({
        ...prev,
        status: 'error',
        errorMessage: err.message || 'Failed to start session',
        isSendingFrame: false,
        detections: [],
        lastDetectionTelemetry: null,
      }));
    }
  }, []);

  const stop = useCallback(() => {
    frameInFlightRef.current = false;

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
      lastDetectionTelemetry: null,
    });
  }, []);

  const sendFrame = useCallback(({ frameData, telemetry }: SendFrameInput) => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    if (frameInFlightRef.current) return;

    frameInFlightRef.current = true;

    const sentAt = Date.now();

    setState((prev) => ({ ...prev, isSendingFrame: true, status: 'processing' }));
    ws.send(
      JSON.stringify({
        type: 'frame',
        data: frameData,
        timestamp: sentAt,
        telemetry: {
          ...telemetry,
          sent_at: sentAt,
        },
      })
    );
  }, []);

  return { ...state, start, stop, sendFrame };
}
