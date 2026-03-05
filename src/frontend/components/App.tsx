import React from 'react';
import { StatusBar, View, Image } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { PaperProvider, MD3LightTheme } from 'react-native-paper';
import RegisterScreen from './RegisterScreen';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';
import { NavigationContainer } from '@react-navigation/native';
import LoginScreen from './LoginScreen';
import HomeScreen from './HomeScreen';
import SplashScreen from './SplashScreen';
import { IconButton } from 'react-native-paper';
import { clearSession, getSession } from '../utils/session';
import { LogBox } from 'react-native';
import ProfileScreen from './ProfileScreen';
import ChangePasswordScreen from './ChangePasswordScreen';
import { logout } from '../utils/api';


LogBox.ignoreLogs([
  'Sending `onAnimatedValueUpdate` with no listeners registered.',
]);

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  const theme = MD3LightTheme;
  const handleLogout = async (navigation: any) => {
    try{
      const sessionId = await getSession();
      if (sessionId){
        await logout(sessionId); //Deletes session from db
      }
    } catch(error){
      console.error('Logout failed: ', error);
    } finally{
      await clearSession();
      navigation.replace('Login');
    }
    
  };

  return (
    <SafeAreaProvider>
      <PaperProvider theme={theme}>
        <StatusBar barStyle="dark-content" />
        <NavigationContainer>
          <Stack.Navigator 
            initialRouteName='Splash' 
            screenOptions={({navigation}) => ({ //Parenthesis syntax is an implicit return of the object
              headerShown: true,
              headerTitle: () => (
                <Image
                  source={require('../assets/logo.png')}
                  style={{ width: 32, height: 32, borderRadius: 8 }}
                  accessibilityLabel="App logo"
                />
              ),
              headerRight: () => (
                <View style={{flexDirection: 'row'}}>
                  <IconButton
                    icon="account-circle"
                    size={24}
                    onPress={() => navigation.navigate('Profile')}
                    accessibilityLabel="Profile button"
                    accessibilityHint="Press to view your Profile"
                    accessibilityRole="button"
                  />
                  <IconButton
                    icon="logout"
                    size={24}
                    onPress={() => handleLogout(navigation)}
                    accessibilityLabel="Log out button"
                    accessibilityHint="Press to log out of your account"
                    accessibilityRole="button"
                  />
                </View>
                
              ),
            })}
            >
              <Stack.Screen name='Register' component={RegisterScreen} options={{ headerShown: false }} />
              <Stack.Screen name='Login' component={LoginScreen} options={{ headerShown: false }} />
              <Stack.Screen name='Home' component={HomeScreen} />
              <Stack.Screen name='Splash' component={SplashScreen} options={{ headerShown: false }} />
              <Stack.Screen 
                name='Profile' 
                component={ProfileScreen} 
                options={({navigation}) => ({
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
              />
              <Stack.Screen 
                name='ChangePassword' 
                component={ChangePasswordScreen} 
                options={{ title: 'Change Password' }} 
              />
          </Stack.Navigator>
        </NavigationContainer>
      </PaperProvider>
    </SafeAreaProvider>
  );
}
