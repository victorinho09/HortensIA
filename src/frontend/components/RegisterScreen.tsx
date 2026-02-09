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
import { createUser } from '../utils/api';

type Props = NativeStackScreenProps<RootStackParamList, 'Register'>;

export default function RegisterScreen({ navigation }: Props) {
  const [apiError, setApiError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [countryCode, setCountryCode] = useState('');
  const [phone, setPhone] = useState('');
  const [diversityType, setDiversityType] = useState('');
  const [errors, setErrors] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    contactEmail: '',
    countryCode: '',
    phone: '',
    diversityType: '',
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
      name: validateName(name),
      email: validateEmailField(email),
      password: validatePassword(password),
      confirmPassword: validatePasswordMatch(password, confirmPassword),
      contactEmail: validateContactEmail(email),
      countryCode: validateCountryCode(countryCode, phone),
      phone: validatePhone(phone, countryCode),
      diversityType: validateDiversityType(diversityType),
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
        const result = await createUser({
          name,
          email,
          password,
          contactEmail,
          countryCode,
          phone,
          diversityType,
        });

        setSuccessMessage(
          'Account created successfully! Redirecting to login...',
        );

        setTimeout(() => {
          navigation.navigate('Login');
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

  const handleNameBlur = () => {
    setTouched(prev => ({ ...prev, name: true }));
    setErrors(prev => ({
      ...prev,
      name: validateName(name),
    }));
  };

  const handleEmailBlur = () => {
    setTouched(prev => ({ ...prev, email: true }));
    setErrors(prev => ({
      ...prev,
      email: validateEmailField(email),
    }));
  };

  const handlePasswordBlur = () => {
    setTouched(prev => ({ ...prev, password: true }));
    setErrors(prev => ({
      ...prev,
      password: validatePassword(password),
    }));
  };

  const handleConfirmPasswordBlur = () => {
    setTouched(prev => ({ ...prev, confirmPassword: true }));
    setErrors(prev => ({
      ...prev,
      confirmPassword: validatePasswordMatch(password, confirmPassword),
    }));
  };

  const handleContactEmailBlur = () => {
    setTouched(prev => ({ ...prev, contactEmail: true }));
    setErrors(prev => ({
      ...prev,
      contactEmail: validateContactEmail(contactEmail),
    }));
  };

  const handleCountryCodeBlur = () => {
    setTouched(prev => ({ ...prev, countryCode: true }));
    setErrors(prev => ({
      ...prev,
      countryCode: validateCountryCode(countryCode, phone),
    }));
  };

  const handlePhoneBlur = () => {
    setTouched(prev => ({ ...prev, phone: true }));
    setErrors(prev => ({
      ...prev,
      phone: validatePhone(phone, countryCode),
    }));
  };

  const handleDiversityTypeBlur = () => {
    setTouched(prev => ({ ...prev, diversityType: true }));
    setErrors(prev => ({
      ...prev,
      diversityType: validateDiversityType(diversityType),
    }));
  };

  const handleNameChange = (value: string) => {
    setName(value);
    if (touched.name) {
      setErrors(prev => ({
        ...prev,
        name: validateName(name),
      }));
    }
  };
  const handleEmailChange = (value: string) => {
    setEmail(value);
    if (touched.email) {
      setErrors(prev => ({
        ...prev,
        email: validateEmailField(email),
      }));
    }
  };

  const handlePasswordChange = (value: string) => {
    setPassword(value);
    if (touched.password) {
      setErrors(prev => ({
        ...prev,
        password: validatePassword(password),
      }));
    }
  };

  const handleConfirmPasswordChange = (value: string) => {
    setConfirmPassword(value);
    if (touched.confirmPassword) {
      setErrors(prev => ({
        ...prev,
        confirmPassword: validatePasswordMatch(password, confirmPassword),
      }));
    }
  };

  const handleContactEmailChange = (value: string) => {
    setContactEmail(value);
    if (touched.contactEmail) {
      setErrors(prev => ({
        ...prev,
        contactEmail: validateContactEmail(contactEmail),
      }));
    }
  };

  const handleCountryCodeChange = (value: string) => {
    setCountryCode(value);
    if (touched.countryCode) {
      setErrors(prev => ({
        ...prev,
        countryCode: validateCountryCode(countryCode, phone),
      }));
    }
  };

  const handlePhoneChange = (value: string) => {
    setPhone(value);
    if (touched.phone) {
      setErrors(prev => ({
        ...prev,
        phone: validatePhone(phone, countryCode),
      }));
    }
  };

  const handleDiversityTypeChange = (value: string) => {
    setDiversityType(value);
    if (touched.diversityType) {
      setErrors(prev => ({
        ...prev,
        diversityType: validateDiversityType(diversityType),
      }));
    }
  };

  const isFormValid =
    email.trim() !== '' &&
    password !== '' &&
    confirmPassword !== '' &&
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
              value={name}
              onChangeText={handleNameChange}
              onBlur={handleNameBlur}
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
              secureTextEntry
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
              value={confirmPassword}
              onChangeText={handleConfirmPasswordChange}
              onBlur={handleConfirmPasswordBlur}
              mode="outlined"
              secureTextEntry
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
              value={contactEmail}
              onChangeText={handleContactEmailChange}
              onBlur={handleContactEmailBlur}
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
                value={phone}
                onChangeText={handlePhoneChange}
                onBlur={handlePhoneBlur}
                mode="outlined"
                keyboardType="phone-pad"
                placeholder="600123456"
                left={<TextInput.Icon icon="cellphone" />}
                style={[styles.input, styles.phoneInput]}
              />

              <TextInput
                label="CC"
                value={countryCode}
                onChangeText={handleCountryCodeChange}
                onBlur={handleCountryCodeBlur}
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
              value={diversityType}
              onChangeText={handleDiversityTypeChange}
              onBlur={handleDiversityTypeBlur}
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
