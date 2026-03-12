import React, { useRef, useEffect, useCallback } from 'react';
import { View, TouchableOpacity, Dimensions } from 'react-native';
import { Camera, useCameraDevice } from 'react-native-vision-camera';
import { Text } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { BoundingBox } from './common/BoundingBox';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';
import { usePermissions } from '../hooks/usePermissions';
import { useLiveSession, SessionStatus } from '../hooks/useLiveSession';
import { styles } from './styles/LiveCameraScreen.styles';

type Props = NativeStackScreenProps<RootStackParamList, 'LiveCamera'>;

// Default capture interval — adjust when frame frequency is decided
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

  // Redirect to Permissions if user revokes permissions from iOS Settings while in the app
  useEffect(() => {
    if (!allGranted) {
      navigation.replace('Permissions');
    }
  }, [allGranted, navigation]);

  const captureAndSendFrame = useCallback(async () => {
    // Skip if already capturing or camera not ready
    if (!cameraRef.current || !isActive || isCapturingRef.current) return;

    isCapturingRef.current = true;
    try {
      const photo = await cameraRef.current.takePhoto({ flash: 'off', enableShutterSound: false });
      console.log('[LiveCamera] Photo dimensions:', { width: photo.width, height: photo.height });
      const response = await fetch(`file://${photo.path}`);
      const blob = await response.blob();
      const base64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve((reader.result as string).split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
      sendFrame(base64);
    } catch (err) {
      // Frame capture failed — continue silently, do not interrupt session
      console.debug('[LiveCamera] Frame capture failed:', err);
    } finally {
      isCapturingRef.current = false;
    }
  }, [isActive, sendFrame]);

  useEffect(() => {
    if (isActive) {
      frameIntervalRef.current = setInterval(captureAndSendFrame, FRAME_INTERVAL_MS);
    } else {
      if (frameIntervalRef.current) {
        clearInterval(frameIntervalRef.current);
        frameIntervalRef.current = null;
      }
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
      {/* Camera preview */}
      <Camera
        ref={cameraRef}
        style={styles.camera}
        device={device}
        isActive={allGranted}
        photo={true}
        accessibilityLabel="Live camera preview"
        onLayout={(e) => {
          const { width, height } = e.nativeEvent.layout;
          setCameraLayout({ width, height });
          console.log('[LiveCamera] Camera layout:', { width, height });
        }}
      />

      {/* Overlay UI */}
      <View style={styles.overlay}>
        {/* Bounding boxes */}
        {cameraLayout.width > 0 &&
          detections.map((detection, index) => (
            <BoundingBox
              key={`detection-${index}`}
              detection={detection}
              frameWidth={cameraLayout.width}
              frameHeight={cameraLayout.height}
            />
          ))}

        {/* Top: session status */}
        <View style={styles.statusBar} accessibilityLiveRegion="polite">
          <View
            style={[styles.statusDot, { backgroundColor: STATUS_COLORS[status] }]}
            accessibilityElementsHidden={true}
            importantForAccessibility="no"
          />
          <Text style={styles.statusText}>{STATUS_LABELS[status]}</Text>
          {errorMessage ? <Text style={styles.errorText}>{errorMessage}</Text> : null}
        </View>

        {/* Top-right: live activity indicators */}
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

        {/* Bottom: Start / Stop */}
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
