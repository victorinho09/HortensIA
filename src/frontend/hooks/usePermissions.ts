import { Linking } from 'react-native';
import { useCameraPermission, useMicrophonePermission } from 'react-native-vision-camera';

export function usePermissions() {
  const { hasPermission: hasCameraPermission } = useCameraPermission();
  const { hasPermission: hasMicPermission } = useMicrophonePermission();

  const allGranted = hasCameraPermission && hasMicPermission;

  const openSettings = () => Linking.openSettings();

  return {
    hasCameraPermission,
    hasMicPermission,
    allGranted,
    openSettings,
  };
}
