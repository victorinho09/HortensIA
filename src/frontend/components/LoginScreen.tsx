import React, { useState, useRef } from 'react';
import { ScrollView, View, Image, KeyboardAvoidingView,Platform } from 'react-native';
import { Text, Card, TextInput, Button, HelperText,useTheme } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';
import {styles} from './styles/LoginScreen.styles';
import {
  validateEmailField,
  validatePassword,
} from '../utils/validation';
import { useFormValidation } from '../hooks/useFormValidation';
import { login } from '../utils/api';
import { saveSession } from '../utils/session';

type Props = NativeStackScreenProps<RootStackParamList, 'Login'>;

export default function LoginScreen({ navigation }: Props) {
  const theme = useTheme()

  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const passwordRef = useRef<any>(null);

  const { formData, errors, touched, handleBlur, handleChange, validateForm } = useFormValidation(
    {
      email: '',
      password: ''
    },
    (data) => ({
      email: validateEmailField,
      password: validatePassword,
    })
  );

  const handleSubmit = async () => {
    if (validateForm()) {
      setLoading(true);
      setApiError(''); //To clear previous errors
      try {
        const response = await login(formData.email, formData.password); 
        console.log('LoginScreen - Login response:', response);

        await saveSession(response.session_id)
        console.log('LoginScreen - Session saved:', response.session_id);

        navigation.replace('Splash');
      } catch (error: any) {
        const errorMessage =
          error.response?.data?.detail ||
          error.response?.data?.message ||
          'Invalid email or password';
        setApiError(errorMessage);
      } finally {
        setLoading(false);
      }
    }
  };

  const isFormValid =
    formData.email.trim() !== '' &&
    formData.password !== '' &&
    Object.values(errors).every(error => error === '');

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{flex: 1}}
      >
        <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled" >
          <Image
            source={require('../assets/logo.png')}
            style={styles.logo}
            accessibilityLabel="App logo"
          />
          <Text variant="headlineSmall" style={styles.appName}>
            HortensIA
          </Text>
          <Text 
            variant="bodyMedium" 
            style={styles.subtitle}
            accessibilityLabel="Log in to your account to get started"
          >
            Log in to your account to get started
          </Text>

          {apiError && (
            <HelperText 
              type="error" 
              visible 
              style={styles.apiError}
              accessible={true}
              accessibilityLabel="Error message"
              accessibilityLiveRegion="polite"
            >
              {apiError}
            </HelperText>
          )}

          <Card style={styles.card}>
            <Card.Content>
              <TextInput
                label="Email *"
                placeholder="testaccount@gmail.com"
                value={formData.email}
                onChangeText={handleChange('email')}
                onBlur={handleBlur('email')}
                mode="outlined"
                keyboardType="email-address"
                autoCapitalize="none"
                autoComplete="email"
                textContentType="emailAddress"
                left={<TextInput.Icon icon="email" />}
                style={styles.input}
                accessibilityLabel="Email address input field"
                accessibilityHint="Enter your email address"
                accessibilityRole="text"
                returnKeyType="next"
                submitBehavior='submit'
                onSubmitEditing={() => passwordRef.current?.focus()}
              />

              {touched.email && errors.email && (
                <HelperText 
                  type="error" 
                  visible={!!errors.email}
                  accessible={true}
                  accessibilityLabel="Email validation error"
                  accessibilityLiveRegion="polite"
                >
                  {errors.email}
                </HelperText>
              )}

              <TextInput
                label="Password *"
                placeholder="New Password"
                value={formData.password}
                onChangeText={handleChange('password')}
                onBlur={handleBlur('password')}
                mode="outlined"
                secureTextEntry = {!showPassword}
                textContentType="password"
                autoComplete="current-password"
                right={
                  <TextInput.Icon 
                    icon={showPassword ? "eye-off" : "eye"}
                    onPress={() => setShowPassword(!showPassword)}
                    accessibilityLabel={showPassword ? "Hide password" : "Show password"}
                    accessibilityHint="Toggle password visibility"
                    accessibilityRole="button"
                  />
                }
                left={<TextInput.Icon icon="lock" />}
                style={styles.input}
                accessibilityLabel="Password input field"
                accessibilityHint="Enter your password"
                accessibilityRole="text"
                ref={passwordRef}
                returnKeyType="done"
              />

              {touched.password && errors.password && (
                <HelperText 
                  type="error" 
                  visible={!!errors.password}
                  accessible={true}
                  accessibilityLabel="Password validation error"
                  accessibilityLiveRegion="polite"
                >
                  {errors.password}
                </HelperText>
              )}

              <Button
                mode="contained"
                onPress={handleSubmit}
                disabled={!isFormValid}
                loading={loading}
                style={[styles.button, !isFormValid && styles.buttonDisabled]}
                accessibilityLabel="Log in button"
                accessibilityHint="Press to log in with your credentials"
                accessibilityRole="button"
                accessibilityState={{ disabled: !isFormValid }}
              >
                {loading ? 'Logging in...' : 'Log in'}
              </Button>

              <View style={styles.linkContainer}>
                <Text 
                  variant='bodyMedium' 
                  style={styles.linkText}
                >
                  Don't have an account?
                </Text>
                <Text
                  variant='bodyMedium'
                  style={[styles.link, { color: theme.colors.primary }]}
                  onPress={() => {navigation.navigate('Register')}}
                  accessibilityLabel="Register link"
                  accessibilityHint="Navigate to registration page"
                  accessibilityRole="link"
                >
                  Register
                </Text>
              </View>
            </Card.Content>
          </Card>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
