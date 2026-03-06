import { useCameraPermission, useMicrophonePermission } from 'react-native-vision-camera';

export function usePermissions() {
  const { hasPermission: hasCameraPermission, requestPermission: requestCameraPermission } =
    useCameraPermission();
  const { hasPermission: hasMicPermission, requestPermission: requestMicPermission } =
    useMicrophonePermission();

  const allGranted = hasCameraPermission && hasMicPermission;

  const requestAll = async () => {
    if (!hasCameraPermission) await requestCameraPermission();
    if (!hasMicPermission) await requestMicPermission();
  };

  return {
    hasCameraPermission,
    hasMicPermission,
    allGranted,
    requestAll,
  };
}
