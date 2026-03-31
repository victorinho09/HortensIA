import React, { useRef, useEffect, useCallback } from 'react';
import { View, TouchableOpacity } from 'react-native';
import { Camera, useCameraDevice } from 'react-native-vision-camera';
import { Text } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackScreenProps } from '@react-navigation/native-stack';

import { BoundingBox } from './common/BoundingBox';
import { RootStackParamList } from './navigation/types';
import { styles } from './styles/LiveCameraScreen.styles';
import { usePermissions } from '../hooks/usePermissions';
import { useLiveSession, SessionStatus, DetectedObject } from '../hooks/useLiveSession';

type Props = NativeStackScreenProps<RootStackParamList, 'LiveCamera'>;

const FRAME_INTERVAL_MS = 250;
const TRACK_IOU_THRESHOLD = 0.2;
const STABLE_POSITION_DELTA = 0.02;
const STABLE_CONFIDENCE_DELTA = 0.05;
const MAX_MISSED_FRAMES = 1;

interface TrackedDetection extends DetectedObject {
  id: string;
  lastSeenAt: number;
  missedFrames: number;
}

const STATUS_LABELS: Record<SessionStatus, string> = {
  idle: 'Idle',
  connecting: 'Connecting...',
  streaming: 'Streaming',
  processing: 'Processing...',
  speaking: 'Speaking',
  error: 'Error',
};

const STATUS_COLORS: Record<SessionStatus, string> = {
  idle: '#888',
  connecting: '#f59e0b',
  streaming: '#22c55e',
  processing: '#3b82f6',
  speaking: '#8b5cf6',
  error: '#ef4444',
};

function getIntersectionOverUnion(
  first: [number, number, number, number],
  second: [number, number, number, number]
): number {
  const [ax1, ay1, ax2, ay2] = first;
  const [bx1, by1, bx2, by2] = second;

  const intersectionWidth = Math.max(0, Math.min(ax2, bx2) - Math.max(ax1, bx1));
  const intersectionHeight = Math.max(0, Math.min(ay2, by2) - Math.max(ay1, by1));
  const intersectionArea = intersectionWidth * intersectionHeight;

  if (intersectionArea <= 0) {
    return 0;
  }

  const firstArea = Math.max(0, ax2 - ax1) * Math.max(0, ay2 - ay1);
  const secondArea = Math.max(0, bx2 - bx1) * Math.max(0, by2 - by1);
  const unionArea = firstArea + secondArea - intersectionArea;

  return unionArea > 0 ? intersectionArea / unionArea : 0;
}

function mergeTrackedDetections(
  previous: TrackedDetection[],
  incoming: DetectedObject[],
  now: number,
  nextTrackIdRef: React.MutableRefObject<number>
): TrackedDetection[] {
  const availablePrevious = [...previous];
  const matched: TrackedDetection[] = [];

  for (const detection of incoming) {
    let bestIndex = -1;
    let bestScore = 0;

    availablePrevious.forEach((candidate, index) => {
      if (candidate.class_name !== detection.class_name) {
        return;
      }

      const iou = getIntersectionOverUnion(
        candidate.bbox as [number, number, number, number],
        detection.bbox
      );
      if (iou > bestScore) {
        bestScore = iou;
        bestIndex = index;
      }
    });

    if (bestIndex >= 0 && bestScore >= TRACK_IOU_THRESHOLD) {
      const reused = availablePrevious.splice(bestIndex, 1)[0];
      const isStable = reused.bbox.every(
        (value, bboxIndex) => Math.abs(value - detection.bbox[bboxIndex]) <= STABLE_POSITION_DELTA
      );
      const hasSimilarConfidence =
        Math.abs(reused.confidence - detection.confidence) <= STABLE_CONFIDENCE_DELTA;

      matched.push({
        ...(isStable && hasSimilarConfidence ? reused : detection),
        id: reused.id,
        lastSeenAt: now,
        missedFrames: 0,
      });
      continue;
    }

    matched.push({
      ...detection,
      id: `tracked-${nextTrackIdRef.current}`,
      lastSeenAt: now,
      missedFrames: 0,
    });
    nextTrackIdRef.current += 1;
  }

  const retained = availablePrevious
    .map((candidate) => ({
      ...candidate,
      missedFrames: candidate.missedFrames + 1,
    }))
    .filter((candidate) => candidate.missedFrames <= MAX_MISSED_FRAMES);

  return [...matched, ...retained];
}

export default function LiveCameraScreen({ navigation }: Props) {
  const { allGranted } = usePermissions();
  const {
    status,
    errorMessage,
    isSendingFrame,
    isPlayingAudio,
    detections,
    start,
    stop,
    sendFrame,
  } = useLiveSession();
  const [cameraLayout, setCameraLayout] = React.useState({ width: 0, height: 0 });
  const [trackedDetections, setTrackedDetections] = React.useState<TrackedDetection[]>([]);
  const cameraRef = useRef<Camera>(null);
  const frameIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isCapturingRef = useRef<boolean>(false);
  const nextTrackIdRef = useRef<number>(1);
  const device = useCameraDevice('back');

  const isActive = status !== 'idle' && status !== 'error';

  useEffect(() => {
    if (!allGranted) {
      navigation.replace('Permissions');
    }
  }, [allGranted, navigation]);

  useEffect(() => {
    const now = Date.now();
    setTrackedDetections((previous) =>
      mergeTrackedDetections(previous, detections, now, nextTrackIdRef)
    );
  }, [detections]);

  const captureAndSendFrame = useCallback(async () => {
    if (!cameraRef.current || !isActive || isCapturingRef.current) {
      return;
    }

    isCapturingRef.current = true;
    try {
      const photo = await cameraRef.current.takePhoto({
        flash: 'off',
        enableShutterSound: false,
      });
      const response = await fetch(`file://${photo.path}`);
      const blob = await response.blob();
      const base64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve((reader.result as string).split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });

      sendFrame(base64);
    } catch {
      // Ignore capture failures to keep the session running.
    } finally {
      isCapturingRef.current = false;
    }
  }, [isActive, sendFrame]);

  useEffect(() => {
    if (isActive) {
      frameIntervalRef.current = setInterval(captureAndSendFrame, FRAME_INTERVAL_MS);
    } else if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }

    return () => {
      if (frameIntervalRef.current) {
        clearInterval(frameIntervalRef.current);
        frameIntervalRef.current = null;
      }
    };
  }, [isActive, captureAndSendFrame]);

  if (!device) {
    return (
      <SafeAreaView style={styles.container} edges={['bottom', 'left', 'right']}>
        <View style={styles.overlay}>
          <Text variant="bodyMedium" style={styles.statusText} accessibilityRole="alert">
            No camera device found.
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['bottom', 'left', 'right']}>
      <Camera
        ref={cameraRef}
        style={styles.camera}
        device={device}
        isActive={allGranted}
        photo={true}
        accessibilityLabel="Live camera preview"
        onLayout={(event) => {
          const { width, height } = event.nativeEvent.layout;
          setCameraLayout({ width, height });
        }}
      />

      <View style={styles.overlay}>
        {cameraLayout.width > 0 &&
          trackedDetections.map((detection) => (
            <BoundingBox
              key={detection.id}
              detection={detection}
              frameWidth={cameraLayout.width}
              frameHeight={cameraLayout.height}
            />
          ))}

        <View style={styles.statusBar} accessibilityLiveRegion="polite">
          <View
            style={[styles.statusDot, { backgroundColor: STATUS_COLORS[status] }]}
            accessibilityElementsHidden={true}
            importantForAccessibility="no"
          />
          <Text style={styles.statusText}>{STATUS_LABELS[status]}</Text>
          {errorMessage ? <Text style={styles.errorText}>{errorMessage}</Text> : null}
        </View>

        <View style={styles.indicators} accessibilityLiveRegion="polite">
          {isActive && (
            <View style={styles.indicator}>
              <View
                style={styles.recordingDot}
                accessibilityElementsHidden={true}
                importantForAccessibility="no"
              />
              <Text style={styles.indicatorText}>Live</Text>
            </View>
          )}
          {isSendingFrame && (
            <View style={styles.indicator}>
              <Text style={styles.indicatorText}>⬆ Sending</Text>
            </View>
          )}
          {isPlayingAudio && (
            <View style={styles.indicator}>
              <Text style={styles.indicatorText}>🔊 Audio</Text>
            </View>
          )}
        </View>

        <View style={styles.controls}>
          <TouchableOpacity
            style={styles.captureButtonContainer}
            onPress={isActive ? stop : start}
            accessibilityLabel={isActive ? 'Stop session button' : 'Start session button'}
            accessibilityHint={
              isActive ? 'Press to stop the live session' : 'Press to start the live session'
            }
            accessibilityRole="button"
            accessibilityState={{ disabled: false }}
          >
            <View style={isActive ? styles.captureButtonInnerActive : styles.captureButtonInner} />
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}
