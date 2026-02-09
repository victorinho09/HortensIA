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

type Props = NativeStackScreenProps<RootStackParamList, 'Login'>;

export default function LoginScreen({ navigation }: Props) {
  const theme = useTheme()

  const [apiError, setApiError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({
    email: '',
    password: '',
  });
  const [touched, setTouched] = useState({
    name: false,
    email: false,
    password: false,
    confirmPassword: false,
    contactEmail: false,
    countryCode: false,
    phone: false,
    diversityType: false,
  });

  const validateForm = () => {
      const newErrors = {
        email: validateEmailField(email),
        password: validatePassword(password),
      };
  
      setErrors(newErrors);
  
      return Object.values(newErrors).every(error => error === '');
    };

  const handleSubmit = async () => {
    if (validateForm()) {
      setLoading(true);
      setApiError(''); //To clear previous errors
      setSuccessMessage(''); //To clear previous success messages
      try {
        /*
        const result = await createUser({
          name,
          email,
          password,
          contactEmail,
          countryCode,
          phone,
          diversityType,
        });
        */
        
        setSuccessMessage(
          'Log in successful! Redirecting to home page...',
        );

        setTimeout(() => {
          //navigation.navigate('Home');
        }, 1000);
      } catch (error: any) {
        const errorMessage =
          error.response?.data?.detail ||
          error.response?.data?.message ||
          'Something went wrong. Please try again.';
        setApiError(errorMessage);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleEmailChange = (value: string) => {
      setEmail(value);
      if (!touched.email) return;

      if (email.trim() === '') {
        setErrors(prev => ({...prev,email: '',}));
        return;
      }
      setErrors(prev => ({...prev,email: validateEmailField(email),}));
    };
  
    const handlePasswordChange = (value: string) => {
      setPassword(value);
      if(!touched.password) return;

      if (password.trim() === '') {
        setErrors(prev => ({...prev,password: '',}));
        return;
      }
      setErrors(prev => ({...prev,password: validatePassword(password),}));
    };

    const handleEmailBlur = () => {
        setTouched(prev => ({ ...prev, email: true }));
        if(email.trim() === ''){
          setErrors(prev => ({...prev,email: '',}));
          return;
        }
        setErrors(prev => ({...prev,email: validateEmailField(email),}));
      };
    
    const handlePasswordBlur = () => {
      setTouched(prev => ({ ...prev, password: true }));
      if(password.trim() === ''){
        setErrors(prev => ({...prev,password: '',}));
        return;
      }
      setErrors(prev => ({...prev,password: validatePassword(password),}));
    };

    const isFormValid =
    email.trim() !== '' &&
    password !== '' &&
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
              value={email}
              onChangeText={handleEmailChange}
              onBlur={handleEmailBlur}
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
              value={password}
              onChangeText={handlePasswordChange}
              onBlur={handlePasswordBlur}
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
