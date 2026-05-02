import { Linking } from 'react-native';
import { useCameraPermission } from 'react-native-vision-camera';

export function usePermissions() {
  const { hasPermission: hasCameraPermission } = useCameraPermission();

  const allGranted = hasCameraPermission;

  const openSettings = () => Linking.openSettings();

  return {
    hasCameraPermission,
    allGranted,
    openSettings,
  };
}
