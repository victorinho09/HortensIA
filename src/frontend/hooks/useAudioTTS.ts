import { useCallback, useEffect, useRef, useState } from 'react';
import Tts from 'react-native-tts';
import { translateObjectClassName } from '../utils/objectClassTranslations';

// Constants for managing alert frequency and TTS settings
const ALERT_COOLDOWN_MS = 5000;
const CRITICAL_STREAK_REQUIRED = 2;

export interface CriticalSceneRisk {
  severity: 'info' | 'warning' | 'critical';
  dominant_track_id: number | null;
  dominant_class_name: string | null;
}

export interface CriticalAudioAlertController {
  isPlayingAudio: boolean;
  handleSceneRisk: (sceneRisk: CriticalSceneRisk | null) => void;
  resetAudioAlerts: () => void;
  stopAudio: () => Promise<void>;
}

export function useCriticalAudioAlert(): CriticalAudioAlertController {
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const lastAlertAtRef = useRef(0);
  const lastAlertTrackIdRef = useRef<number | null>(null);
  const lastAlertClassNameRef = useRef<string | null>(null);
  const criticalStreakRef = useRef(0);
  const isSpeakingRef = useRef(false);

  const resetAudioAlerts = useCallback(() => {
    lastAlertAtRef.current = 0;
    lastAlertTrackIdRef.current = null;
    lastAlertClassNameRef.current = null;
    criticalStreakRef.current = 0;
  }, []);

  useEffect(() => {
    Tts.setDefaultLanguage('es-ES');

    const handleTtsStart = () => {
      isSpeakingRef.current = true;
      setIsPlayingAudio(true);
    };

    const handleTtsFinish = () => {
      isSpeakingRef.current = false;
      setIsPlayingAudio(false);
    };

    const handleTtsCancel = () => {
      isSpeakingRef.current = false;
      setIsPlayingAudio(false);
    };

    const startSubscription = Tts.addEventListener(
    'tts-start',
    handleTtsStart,
  ) as unknown as { remove: () => void };

  const finishSubscription = Tts.addEventListener(
    'tts-finish',
    handleTtsFinish,
  ) as unknown as { remove: () => void };

  const cancelSubscription = Tts.addEventListener(
    'tts-cancel',
    handleTtsCancel,
  ) as unknown as { remove: () => void };

  return () => {
    startSubscription.remove();
    finishSubscription.remove();
    cancelSubscription.remove();
  };
  }, []);

  const buildCriticalAlertMessage = useCallback((sceneRisk: CriticalSceneRisk) => {
    const translatedClassName = translateObjectClassName(sceneRisk.dominant_class_name);

    if (!translatedClassName) {
      return null;
    }

    return `Alerta. ${translatedClassName}.`;
  }, []);

  const shouldSpeakCriticalAlert = useCallback((sceneRisk: CriticalSceneRisk | null) => {
    if (!sceneRisk) {
      criticalStreakRef.current = 0;
      return false;
    }

    if (sceneRisk.severity !== 'critical') {
      criticalStreakRef.current = 0;
      return false;
    }

    if (!sceneRisk.dominant_class_name) {
      return false;
    }

    if (isSpeakingRef.current) {
      return false;
    }

    criticalStreakRef.current += 1;

    if (criticalStreakRef.current < CRITICAL_STREAK_REQUIRED) {
      return false;
    }

    const now = Date.now();
    const cooldownActive = now - lastAlertAtRef.current < ALERT_COOLDOWN_MS;

    const sameTrack =
      sceneRisk.dominant_track_id !== null &&
      sceneRisk.dominant_track_id === lastAlertTrackIdRef.current;

    const sameClass =
      sceneRisk.dominant_class_name === lastAlertClassNameRef.current;

    if (cooldownActive && (sameTrack || sameClass)) {
      return false;
    }

    return true;
  }, []);

  const speakCriticalAlert = useCallback(async (sceneRisk: CriticalSceneRisk) => {
    const message = buildCriticalAlertMessage(sceneRisk);

    if (!message) {
      return;
    }

    lastAlertAtRef.current = Date.now();
    lastAlertTrackIdRef.current = sceneRisk.dominant_track_id;
    lastAlertClassNameRef.current = sceneRisk.dominant_class_name;

    try {
      Tts.speak(message);
    } catch (error) {
      isSpeakingRef.current = false;
      setIsPlayingAudio(false);
      console.warn('[live][tts] Failed to speak alert', error);
    }
  }, [buildCriticalAlertMessage]);

  const handleSceneRisk = useCallback((sceneRisk: CriticalSceneRisk | null) => {
  if (!sceneRisk) {
    return;
  }

  if (!shouldSpeakCriticalAlert(sceneRisk)) {
    return;
  }

  void speakCriticalAlert(sceneRisk);
}, [shouldSpeakCriticalAlert, speakCriticalAlert]);

  const stopAudio = useCallback(async () => {
    resetAudioAlerts();
    isSpeakingRef.current = false;
    setIsPlayingAudio(false);
  }, [resetAudioAlerts]);

  return {
    isPlayingAudio,
    handleSceneRisk,
    resetAudioAlerts,
    stopAudio,
  };
}