import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Image } from 'react-native';
import { Text, Button } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { Camera } from 'react-native-vision-camera';
import { RootStackParamList } from './navigation/types';
import { usePermissions } from '../hooks/usePermissions';
import { commonStyles } from './styles/common.styles';

type Props = NativeStackScreenProps<RootStackParamList, 'Permissions'>;

export default function PermissionsScreen({ navigation }: Props) {
  const { hasCameraPermission, allGranted, openSettings } = usePermissions();
  const [needsSettings, setNeedsSettings] = useState(false);

  // Request permissions automatically on mount
  useEffect(() => {
    const requestOnMount = async () => {
      const cameraStatus = await Camera.requestCameraPermission();
      if (cameraStatus === 'denied') {
        setNeedsSettings(true);
      }
    };
    requestOnMount();
  }, []);

  // Navigate as soon as camera access becomes granted (e.g. user came back from Settings)
  useEffect(() => {
    if (allGranted) {
      navigation.replace('LiveCamera');
    }
  }, [allGranted, navigation]);

  const handlePress = async () => {
    if (needsSettings) {
      openSettings();
      return;
    }
    // Use Camera static methods directly — most reliable way to trigger the OS dialog
    const cameraStatus = await Camera.requestCameraPermission();
    if (cameraStatus === 'denied') {
      setNeedsSettings(true);
    }
    // If granted, allGranted will update reactively via usePermissions and the useEffect will navigate
  };

  return (
    <SafeAreaView style={commonStyles.container} accessibilityLabel="Permissions required screen">
      <View style={styles.content}>
        <Image
          source={require('../assets/logo.png')}
          style={styles.logo}
          accessibilityLabel="App logo"
        />
        <Text variant="headlineSmall" style={styles.title}>
          Permissions Required
        </Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          HortensIA needs access to your camera to work.
        </Text>
        <View style={styles.cameraStatusContainer}>
          <Text
            style={[styles.statusItem, { color: hasCameraPermission ? '#22c55e' : '#ef4444' }]}
            accessibilityLabel={
              hasCameraPermission ? 'Camera permission granted' : 'Camera permission denied'
            }
          >
            {hasCameraPermission ? '✓' : '✗'} Camera
          </Text>
        </View>
        <Button
          mode="contained"
          onPress={handlePress}
          style={commonStyles.button}
          accessibilityLabel={
            needsSettings ? 'Open settings button' : 'Grant camera permission button'
          }
          accessibilityHint={
            needsSettings
              ? 'Press to open iOS Settings and grant permissions manually'
              : 'Press to grant camera permissions'
          }
        >
          {needsSettings ? 'Open Settings' : 'Grant Camera Access'}
        </Button>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  logo: {
    width: 80,
    height: 80,
    borderRadius: 20,
    marginBottom: 24,
  },
  title: {
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 12,
    color: '#333',
  },
  subtitle: {
    textAlign: 'center',
    color: '#555',
    marginBottom: 32,
  },
  cameraStatusContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 32,
  },
  statusItem: {
    fontSize: 16,
    fontWeight: '600',
  },
});
