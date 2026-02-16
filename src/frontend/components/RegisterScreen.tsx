import React, { useState } from 'react';
import { ScrollView, View } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';
import {
  Text,
  Card,
  TextInput,
  Divider,
  Button,
  HelperText,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { styles } from './styles/RegisterScreen.styles';
import {
  validateDiversityType,
  validatePhone,
  validateCountryCode,
  validateContactEmail,
  validateName,
  validateEmailField,
  validatePassword,
  validatePasswordMatch,
} from '../utils/validation';
import { createUser,login } from '../utils/api';
import { useFormValidation } from '../hooks/useFormValidation';
import { saveSession } from '../utils/session';

type Props = NativeStackScreenProps<RootStackParamList, 'Register'>;

export default function RegisterScreen({ navigation }: Props) {
  const [apiError, setApiError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const { formData, errors, touched, handleBlur, handleChange, validateForm } = useFormValidation(
    {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      contactEmail: '',
      countryCode: '',
      phone: '',
      diversityType: ''
    },
    (data) => ({
      name: validateName,
      email: validateEmailField,
      password: validatePassword,
      confirmPassword: (value: string) => validatePasswordMatch(data.password, value),
      contactEmail: validateContactEmail,
      countryCode: (value: string) => validateCountryCode(value, data.phone),
      phone: (value: string) => validatePhone(value, data.countryCode),
      diversityType: validateDiversityType,
    })
  );

  const handleSubmit = async () => {
    if (validateForm()) {
      setLoading(true);
      setApiError(''); //To clear previous errors
      setSuccessMessage(''); //To clear previous success messages
      try {
        await createUser({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          contactEmail: formData.contactEmail,
          countryCode: formData.countryCode,
          phone: formData.phone,
          diversityType: formData.diversityType,
        });

        //Auto-login after successful registration
        const loginResponse = await login(formData.email,formData.password);
        await saveSession(loginResponse.session_id);

        setSuccessMessage(
          'Account created successfully! Logged in automatically. Redirecting to home page',
        );

        setTimeout(() => {
          navigation.navigate('Home');
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

  const isFormValid =
    formData.email.trim() !== '' &&
    formData.password !== '' &&
    formData.confirmPassword !== '' &&
    Object.values(errors).every(error => error === '');

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text variant="headlineMedium" style={styles.title}>
          Register
        </Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Create your account to get started
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
              label="Name"
              placeholder="Victor Vega"
              value={formData.name}
              onChangeText={handleChange('name')}
              onBlur={handleBlur('name')}
              mode="outlined"
              left={<TextInput.Icon icon="account" />}
              style={styles.input}
            />
            {touched.name && errors.name && (
              <HelperText type="error" visible style={styles.helperText}>
                {errors.name}
              </HelperText>
            )}

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

            <TextInput
              label="Confirm Password *"
              placeholder="Confirm Password"
              value={formData.confirmPassword}
              onChangeText={handleChange('confirmPassword')}
              onBlur={handleBlur('confirmPassword')}
              mode="outlined"
              secureTextEntry={!showConfirmPassword}
              right={
                <TextInput.Icon 
                  icon={showConfirmPassword ? "eye-off" : "eye"}
                  onPress={() => setShowConfirmPassword(!showConfirmPassword)} 
                />
              }
              left={<TextInput.Icon icon="lock-check" />}
              style={styles.input}
            />

            {touched.confirmPassword && errors.confirmPassword && (
              <HelperText type="error" visible={!!errors.confirmPassword}>
                {errors.confirmPassword}
              </HelperText>
            )}

            <Divider style={styles.divider} />

            <Text variant="titleMedium" style={styles.sectionTitle}>
              Additional Information (Optional)
            </Text>

            <TextInput
              label="Contact Email"
              placeholder="myfriend@gmail.com"
              value={formData.contactEmail}
              onChangeText={handleChange('contactEmail')}
              onBlur={handleBlur('contactEmail')}
              mode="outlined"
              keyboardType="email-address"
              autoCapitalize="none"
              left={<TextInput.Icon icon="email-outline" />}
              style={styles.input}
            />

            {touched.contactEmail && errors.contactEmail && (
              <HelperText type="error" visible={!!errors.contactEmail}>
                {errors.contactEmail}
              </HelperText>
            )}

            <View style={styles.row}>
              <TextInput
                label="Phone Number"
                value={formData.phone}
                onChangeText={handleChange('phone')}
                onBlur={handleBlur('phone')}
                mode="outlined"
                keyboardType="phone-pad"
                placeholder="600123456"
                left={<TextInput.Icon icon="cellphone" />}
                style={[styles.input, styles.phoneInput]}
              />

              <TextInput
                label="CC"
                value={formData.countryCode}
                onChangeText={handleChange('countryCode')}
                onBlur={handleBlur('countryCode')}
                mode="outlined"
                keyboardType="number-pad"
                placeholder="34"
                left={<TextInput.Icon icon="phone" />}
                style={[styles.input, styles.countryCodeInput]}
              />
            </View>

            <View>
              {touched.phone && errors.phone && (
                <HelperText type="error" visible style={styles.helperText}>
                  {errors.phone}
                </HelperText>
              )}

              {touched.countryCode && errors.countryCode && (
                <HelperText type="error" visible style={styles.helperText}>
                  {errors.countryCode}
                </HelperText>
              )}
            </View>

            <TextInput
              label="Diversity Type"
              value={formData.diversityType}
              onChangeText={handleChange('diversityType')}
              onBlur={handleBlur('diversityType')}
              mode="outlined"
              placeholder="e.g., Visual, Hearing, Motor..."
              left={<TextInput.Icon icon="account-group" />}
              style={styles.input}
            />

            {touched.diversityType && errors.diversityType && (
              <HelperText type="error" visible={!!errors.diversityType}>
                {errors.diversityType}
              </HelperText>
            )}

            <Button
              mode="contained"
              onPress={handleSubmit}
              disabled={!isFormValid}
              loading={loading}
              style={[styles.button, !isFormValid && styles.buttonDisabled]}
            >
              {loading ? 'Creating...' : 'Create Account'}
            </Button>

            <Button
              mode="text"
              onPress={() => {
                navigation.navigate('Login');
              }}
              style={styles.linkButton}
            >
              Already have an account? Sign In
            </Button>
          </Card.Content>
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
}
