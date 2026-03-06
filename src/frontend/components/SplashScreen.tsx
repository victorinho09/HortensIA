import React, { useEffect } from 'react';
import { View, ActivityIndicator, Image } from 'react-native';
import { Text } from 'react-native-paper';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';
import { getSession } from '../utils/session';
import { getCurrentUser } from '../utils/api';
import { useCameraPermission, useMicrophonePermission } from 'react-native-vision-camera';
import { styles } from './styles/SplashScreen.styles';

type Props = NativeStackScreenProps<RootStackParamList, 'Splash'>;

export default function SplashScreen({ navigation }: Props) {
  const { hasPermission: hasCameraPermission } = useCameraPermission();
  const { hasPermission: hasMicPermission } = useMicrophonePermission();

  useEffect(() => {
    const timer = setTimeout(() => {
      checkSession();
    }, 300);
    return () => clearTimeout(timer);
  }, []);

  const checkSession = async () => {
    try {
      const sessionId = await getSession(); //Returns null if no session exists
      console.log('SplashScreen - Session ID from storage:', sessionId);

      if (!sessionId) {
        console.log('SplashScreen - No session found, going to Login');
        navigation.replace('Login'); //use replace so that back button won't return to this screen
        return;
      }

      console.log('SplashScreen - Validating session with backend...');
      await getCurrentUser(sessionId); //Have to check if session is valid (not expired)
      console.log('SplashScreen - Session valid! Checking permissions...');

      // Only check — never request here. PermissionsScreen is responsible for requesting.
      if (hasCameraPermission && hasMicPermission) {
        console.log('SplashScreen - Permissions already granted, going to LiveCamera');
        navigation.replace('LiveCamera');
      } else {
        console.log('SplashScreen - Permissions not granted, going to Permissions screen');
        navigation.replace('Permissions');
      }
    } catch (error) {
      //getCurrentUser fails it throws error
      console.log('SplashScreen - Session validation failed:', error);
      navigation.replace('Login');
    }
  };

  return (
    <View style={styles.container} accessibilityLabel="Loading screen">
      <Image
        source={require('../assets/logo.png')}
        style={styles.logo}
        accessibilityLabel="App logo"
      />
      <Text variant="headlineMedium" style={styles.appName}>
        HortensIA
      </Text>
      <ActivityIndicator
        size="large"
        style={styles.spinner}
        accessibilityLabel="Loading indicator"
        accessibilityHint="Please wait while we check your session"
      />
    </View>
  );
}
