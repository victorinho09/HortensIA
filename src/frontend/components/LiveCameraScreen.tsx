import React, { useRef, useEffect, useCallback } from 'react';
import { View } from 'react-native';
import { Camera, useCameraDevice } from 'react-native-vision-camera';
import { Button, Text } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';
import { usePermissions } from '../hooks/usePermissions';
import { useLiveSession, SessionStatus } from '../hooks/useLiveSession';
import { styles } from './styles/LiveCameraScreen.styles';

type Props = NativeStackScreenProps<RootStackParamList, 'LiveCamera'>;

// Default capture interval — adjust when frame frequency is decided
const FRAME_INTERVAL_MS = 1000;

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
  const { allGranted, hasCameraPermission, hasMicPermission, requestAll } = usePermissions();
  const { status, errorMessage, isSendingFrame, isPlayingAudio, start, stop, sendFrame } =
    useLiveSession();
  const cameraRef = useRef<Camera>(null);
  const frameIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const device = useCameraDevice('back');

  const isActive = status !== 'idle' && status !== 'error';

  const captureAndSendFrame = useCallback(async () => {
    if (!cameraRef.current || !isActive) return;
    try {
      // TODO: replace placeholder with real frame capture when frequency is decided
      // Steps:
      //   1. const photo = await cameraRef.current.takePhoto({ flash: 'off', enableShutterSound: false });
      //   2. const base64 = await RNFS.readFile(photo.path, 'base64'); // requires react-native-fs
      //   3. sendFrame(base64);
      sendFrame('__placeholder__');
    } catch {
      // Frame capture failed — continue silently, do not interrupt session
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

  // Dedicated permissions screen
  if (!allGranted) {
    return (
      <SafeAreaView style={styles.container} edges={['bottom', 'left', 'right']}>
        <View style={styles.permissionsContainer}>
          <Text variant="headlineSmall" style={styles.permissionsTitle}>
            Permissions Required
          </Text>
          <Text variant="bodyMedium" style={styles.permissionsSubtitle}>
            HortensIA needs access to your camera and microphone to work.
          </Text>
          <View style={styles.permissionStatusRow}>
            <Text
              style={[
                styles.permissionItem,
                { color: hasCameraPermission ? '#22c55e' : '#ef4444' },
              ]}
            >
              {hasCameraPermission ? '✓' : '✗'} Camera
            </Text>
            <Text
              style={[styles.permissionItem, { color: hasMicPermission ? '#22c55e' : '#ef4444' }]}
            >
              {hasMicPermission ? '✓' : '✗'} Microphone
            </Text>
          </View>
          <Button
            mode="contained"
            onPress={requestAll}
            style={styles.permissionsButton}
            accessibilityLabel="Grant permissions button"
            accessibilityHint="Press to grant camera and microphone permissions"
          >
            Grant Permissions
          </Button>
        </View>
      </SafeAreaView>
    );
  }

  if (!device) {
    return (
      <SafeAreaView style={styles.container} edges={['bottom', 'left', 'right']}>
        <View style={styles.permissionsContainer}>
          <Text variant="bodyMedium" style={{ color: '#fff' }}>
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
      />

      {/* Overlay UI */}
      <View style={styles.overlay}>
        {/* Top: session status */}
        <View style={styles.statusBar}>
          <View style={[styles.statusDot, { backgroundColor: STATUS_COLORS[status] }]} />
          <Text style={styles.statusText}>{STATUS_LABELS[status]}</Text>
          {errorMessage ? <Text style={styles.errorText}>{errorMessage}</Text> : null}
        </View>

        {/* Top-right: live activity indicators */}
        <View style={styles.indicators}>
          {isActive && (
            <View style={styles.indicator}>
              <View style={styles.recordingDot} />
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
          <Button
            mode={isActive ? 'outlined' : 'contained'}
            onPress={isActive ? stop : start}
            style={isActive ? styles.stopButton : styles.startButton}
            textColor={isActive ? '#fff' : undefined}
            accessibilityLabel={isActive ? 'Stop session button' : 'Start session button'}
            accessibilityHint={
              isActive ? 'Press to stop the live session' : 'Press to start the live session'
            }
            accessibilityState={{ disabled: false }}
          >
            {isActive ? 'Stop' : 'Start'}
          </Button>
        </View>
      </View>
    </SafeAreaView>
  );
}
