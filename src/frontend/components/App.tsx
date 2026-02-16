import React from 'react';
import { StatusBar, useColorScheme } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { PaperProvider, MD3LightTheme, MD3DarkTheme } from 'react-native-paper';
import RegisterScreen from './RegisterScreen';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';
import { NavigationContainer } from '@react-navigation/native';
import LoginScreen from './LoginScreen';
import HomeScreen from './HomeScreen';
import SplashScreen from './SplashScreen';
import { IconButton } from 'react-native-paper';
import { clearSession } from '../utils/session';
import { LogBox } from 'react-native';

LogBox.ignoreLogs([
  'Sending `onAnimatedValueUpdate` with no listeners registered.',
]);

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  const isDarkMode = useColorScheme() === 'dark';
  const theme = isDarkMode ? MD3DarkTheme : MD3LightTheme;
  const handleLogout = async (navigation: any) => {
    await clearSession();
    navigation.replace('Login');
  };

  return (
    <SafeAreaProvider>
      <PaperProvider theme={theme}>
        <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />
        <NavigationContainer>
          <Stack.Navigator 
            initialRouteName='Splash' 
            screenOptions={({navigation}) => ({ //Parenthesis syntax is an implicit return of the object
              headerShown: true,
              headerRight: () => (
                <IconButton
                  icon="logout"
                  size={24}
                  onPress={() => handleLogout(navigation)}
                  accessibilityLabel="Log out button"
                  accessibilityHint="Press to log out of your account"
                  accessibilityRole="button"
                />
              ),
            })}
            >
              <Stack.Screen name='Register' component={RegisterScreen} options={{ headerShown: false }} />
              <Stack.Screen name='Login' component={LoginScreen} options={{ headerShown: false }} />
              <Stack.Screen name='Home' component={HomeScreen} />
              <Stack.Screen name='Splash' component={SplashScreen} options={{ headerShown: false }} />

          </Stack.Navigator>
        </NavigationContainer>
      </PaperProvider>
    </SafeAreaProvider>
  );
}
