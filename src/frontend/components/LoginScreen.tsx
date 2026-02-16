import React, { useState } from 'react';
import { ScrollView, View } from 'react-native';
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
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

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
      setSuccessMessage(''); //To clear previous success messages
      try {
        const response = await login(formData.email, formData.password); 

        await saveSession(response.session_id)
        
        setSuccessMessage(
          'Log in successful! Redirecting to home page...',
        );

        setTimeout(() => {
          navigation.navigate('Home');
        }, 1000);
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
      <ScrollView contentContainerStyle={styles.content}>
       <Text 
          variant="headlineMedium" 
          style={styles.title}
        >
          Login
        </Text>
        <Text 
          variant="bodyMedium" 
          style={styles.subtitle}
        >
          Log in to your account to get started
        </Text>

        {apiError && (
          <HelperText type="error" visible style={styles.apiError}>
            {apiError}
          </HelperText>
        )}

        {successMessage && (
          <HelperText type="info" visible style={styles.successMessage}>
            {successMessage}
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
              left={<TextInput.Icon icon="email" />}
              style={styles.input}
            />

            {touched.email && errors.email && (
              <HelperText type="error" visible={!!errors.email}>
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
              right={
                <TextInput.Icon icon={showPassword ? "eye-off" : "eye"}
                onPress={() => setShowPassword(!showPassword)} />
              }
              left={<TextInput.Icon icon="lock" />}
              style={styles.input}
            />

            {touched.password && errors.password && (
              <HelperText type="error" visible={!!errors.password}>
                {errors.password}
              </HelperText>
            )}

            <Button
              mode="contained"
              onPress={handleSubmit}
              disabled={!isFormValid}
              loading={loading}
              style={[styles.button, !isFormValid && styles.buttonDisabled]}
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
              >
                Register
              </Text>
            </View>
          </Card.Content>
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
}
