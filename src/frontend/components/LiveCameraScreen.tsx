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
import { useLiveSession, SessionStatus } from '../hooks/useLiveSession';

type Props = NativeStackScreenProps<RootStackParamList, 'LiveCamera'>;

const FRAME_INTERVAL_MS = 250;

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
  const cameraRef = useRef<Camera>(null);
  const frameIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isCapturingRef = useRef<boolean>(false);
  const device = useCameraDevice('back');

  const isActive = status !== 'idle' && status !== 'error';

  useEffect(() => {
    if (!allGranted) {
      navigation.replace('Permissions');
    }
  }, [allGranted, navigation]);

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
          detections.map((detection, index) => (
            <BoundingBox
              key={detection.track_id !== null ? `track-${detection.track_id}` : `det-${index}`}
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
