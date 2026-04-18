import { useState, useRef, useCallback } from 'react';
import { config } from '../config';
import { getSession } from '../utils/session';
import { useCriticalAudioAlert } from './useAudioTTS';


export interface DetectedObject {
  class_name: string;
  confidence: number;
  bbox: [number, number, number, number]; // [x1, y1, x2, y2] normalized [0-1]
  track_id: number | null;
  zone: string;
  supercategory: string;
  supercategory_risk_level: string;
  supercategory_risk_weight: number;
  effective_risk_level: string;
  effective_risk_weight: number;
  risk_source: string;
  size_ratio: number;
  size_category: string;
  size_factor: number;
  velocity_x_px_s: number | null;
  velocity_y_px_s: number | null;
  speed_px_s: number | null;
  area_growth_ratio_2s: number | null;
  is_approaching: boolean;
  track_age_ms: number;
  is_track_stable: boolean;
  object_risk: number | null;
}

export type SessionStatus =
  | 'idle'
  | 'connecting'
  | 'streaming'
  | 'processing'
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

export interface SceneRiskAssessment {
  instant: number;
  smoothed: number;
  severity: 'info' | 'warning' | 'critical';
  dominant_object_index: number | null;
  dominant_track_id: number | null;
  dominant_class_name: string | null;
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
  detections: DetectedObject[];
  lastDetectionTelemetry: DetectionRenderTelemetry | null;
  sceneRisk: SceneRiskAssessment | null;
}

export function useLiveSession() {
  const wsRef = useRef<WebSocket | null>(null);
  const frameInFlightRef = useRef(false);

  const {
    isPlayingAudio,
    handleSceneRisk,
    resetAudioAlerts,
    stopAudio,
  } = useCriticalAudioAlert();

  const [state, setState] = useState<LiveSessionState>({
    status: 'idle',
    errorMessage: null,
    isSendingFrame: false,
    detections: [],
    lastDetectionTelemetry: null,
    sceneRisk: null,
  });

  const start = useCallback(async () => {
    try {
      frameInFlightRef.current = false;
      resetAudioAlerts();

      setState({
        status: 'connecting',
        errorMessage: null,
        isSendingFrame: false,
        detections: [],
        lastDetectionTelemetry: null,
        sceneRisk: null,
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
            const detectionObjects = (msg.objects || []) as DetectedObject[];
            const sceneRisk = (msg.scene_risk ?? null) as SceneRiskAssessment | null;

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

            if (detectionObjects.length > 0) {
              console.log('[live][detections][frame]', {
                frameId: telemetry?.frame_id ?? null,
                detectionsCount: detectionObjects.length,
                frameTimestamp: msg.frame_timestamp,
              });

              detectionObjects.forEach((detection, index) => {
                console.log('[live][detections][object]', {
                  index,
                  className: detection.class_name,
                  confidence: Number(detection.confidence.toFixed(3)),
                  trackId: detection.track_id,
                  bbox: detection.bbox,
                  zone: detection.zone,
                  supercategory: detection.supercategory,
                  domesticRisk: {
                    baseLevel: detection.supercategory_risk_level,
                    baseWeight: detection.supercategory_risk_weight,
                    effectiveLevel: detection.effective_risk_level,
                    effectiveWeight: detection.effective_risk_weight,
                    source: detection.risk_source,
                  },
                  sizeAssessment: {
                    sizeRatio: Number(detection.size_ratio.toFixed(4)),
                    category: detection.size_category,
                    factor: detection.size_factor,
                  },
                  motionAssessment: {
                    velocityXPxS:
                      detection.velocity_x_px_s !== null
                        ? Number(detection.velocity_x_px_s.toFixed(2))
                        : null,
                    velocityYPxS:
                      detection.velocity_y_px_s !== null
                        ? Number(detection.velocity_y_px_s.toFixed(2))
                        : null,
                    speedPxS:
                      detection.speed_px_s !== null
                        ? Number(detection.speed_px_s.toFixed(2))
                        : null,
                    areaGrowthRatio2s:
                      detection.area_growth_ratio_2s !== null
                        ? Number(detection.area_growth_ratio_2s.toFixed(3))
                        : null,
                    isApproaching: detection.is_approaching,
                    trackAgeMs: Number(detection.track_age_ms.toFixed(0)),
                    isTrackStable: detection.is_track_stable,
                  },
                });

                console.log(
                  '[live][summary]',
                  `class=${detection.class_name} track=${detection.track_id} zone=${detection.zone} ` +
                    `base=${detection.supercategory_risk_level}:${detection.supercategory_risk_weight} ` +
                    `effective=${detection.effective_risk_level}:${detection.effective_risk_weight} ` +
                    `size=${detection.size_category}:${detection.size_factor} ` +
                    `speed=${detection.speed_px_s ?? 'null'} ` +
                    `growth=${detection.area_growth_ratio_2s ?? 'null'} ` +
                    `approaching=${detection.is_approaching} ` +
                    `stable=${detection.is_track_stable} age=${detection.track_age_ms}`
                );
              });
            }

            if (sceneRisk !== null) {
              console.log('[live][sceneRisk]', {
                instant: Number(sceneRisk.instant.toFixed(3)),
                smoothed: Number(sceneRisk.smoothed.toFixed(3)),
                severity: sceneRisk.severity,
                dominantObjectIndex: sceneRisk.dominant_object_index,
                dominantTrackId: sceneRisk.dominant_track_id,
                dominantClassName: sceneRisk.dominant_class_name,
              });
            }

            handleSceneRisk(sceneRisk);

            setState((prev) => ({
              ...prev,
              detections: detectionObjects,
              sceneRisk,
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
        void stopAudio();

        setState((prev) => ({
          ...prev,
          status: 'error',
          errorMessage: 'Connection failed',
          isSendingFrame: false,
          detections: [],
          lastDetectionTelemetry: null,
          sceneRisk: null,
        }));
      };

      ws.onclose = () => {
        frameInFlightRef.current = false;
        void stopAudio();

        setState((prev) => ({
          ...prev,
          status: prev.status === 'error' ? 'error' : 'idle',
          isSendingFrame: false,
          detections: [],
          lastDetectionTelemetry: null,
          sceneRisk: null,
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
        sceneRisk: null,
      }));
    }
  }, []);

  const stop = useCallback(() => {
    frameInFlightRef.current = false;
    void stopAudio();

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setState({
      status: 'idle',
      errorMessage: null,
      isSendingFrame: false,
      detections: [],
      lastDetectionTelemetry: null,
      sceneRisk: null,
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

  return { ...state, isPlayingAudio, start, stop, sendFrame };
}
