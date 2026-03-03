import React, { useState } from 'react';
import { ScrollView, View, Image } from 'react-native';
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

        navigation.reset({ index: 0, routes: [{ name: 'Splash' }] });
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
        <Image
          source={require('../assets/logo.png')}
          style={styles.logo}
          accessibilityLabel="App logo"
        />
        <Text variant="headlineSmall" style={styles.appName}>
          Hortensia
        </Text>
        <Text 
          variant="bodyMedium" 
          style={styles.subtitle}
          accessibilityLabel="Create your account to get started"
        >
          Create your account to get started
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
              label="Name"
              placeholder="Victor Vega"
              value={formData.name}
              onChangeText={handleChange('name')}
              onBlur={handleBlur('name')}
              mode="outlined"
              left={<TextInput.Icon icon="account" />}
              error={touched.name && !!errors.name}
              style={styles.input}
              accessibilityLabel="Name input field"
              accessibilityHint="Enter your full name"
              accessibilityRole="text"
            />
            {touched.name && errors.name && (
              <HelperText 
                type="error" 
                visible 
                style={styles.helperText}
                accessible={true}
                accessibilityLabel="Name validation error"
                accessibilityLiveRegion="polite"
              >
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
              error={touched.email && !!errors.email}
              style={styles.input}
              accessibilityLabel="Email address input field"
              accessibilityHint="Enter your email address"
              accessibilityRole="text"
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
              error={touched.password && !!errors.password}
              style={styles.input}
              accessibilityLabel="Password input field"
              accessibilityHint="Enter your password, minimum 8 characters"
              accessibilityRole="text"
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
                  accessibilityLabel={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
                  accessibilityHint="Toggle confirm password visibility"
                  accessibilityRole="button"
                />
              }
              left={<TextInput.Icon icon="lock-check" />}
              error={touched.confirmPassword && !!errors.confirmPassword}
              style={styles.input}
              accessibilityLabel="Confirm password input field"
              accessibilityHint="Re-enter your password to confirm"
              accessibilityRole="text"
            />

            {touched.confirmPassword && errors.confirmPassword && (
              <HelperText 
                type="error" 
                visible={!!errors.confirmPassword}
                accessible={true}
                accessibilityLabel="Confirm password validation error"
                accessibilityLiveRegion="polite"
              >
                {errors.confirmPassword}
              </HelperText>
            )}

            <Divider style={styles.divider} />

            <Text 
              variant="titleMedium" 
              style={styles.sectionTitle}
              accessibilityRole="header"
              accessibilityLabel="Additional information section"
            >
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
              error={touched.contactEmail && !!errors.contactEmail}
              style={styles.input}
              accessibilityLabel="Contact email input field"
              accessibilityHint="Enter an alternative contact email"
              accessibilityRole="text"
            />

            {touched.contactEmail && errors.contactEmail && (
              <HelperText 
                type="error" 
                visible={!!errors.contactEmail}
                accessible={true}
                accessibilityLabel="Contact email validation error"
                accessibilityLiveRegion="polite"
              >
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
                error={touched.phone && !!errors.phone}
                style={[styles.input, styles.phoneInput]}
                accessibilityLabel="Phone number input field"
                accessibilityHint="Enter your phone number"
                accessibilityRole="text"
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
                error={touched.countryCode && !!errors.countryCode}
                style={[styles.input, styles.countryCodeInput]}
                accessibilityLabel="Country code input field"
                accessibilityHint="Enter your country calling code"
                accessibilityRole="text"
              />
            </View>

            <View>
              {touched.phone && errors.phone && (
                <HelperText 
                  type="error" 
                  visible 
                  style={styles.helperText}
                  accessible={true}
                  accessibilityLabel="Phone validation error"
                  accessibilityLiveRegion="polite"
                >
                  {errors.phone}
                </HelperText>
              )}

              {touched.countryCode && errors.countryCode && (
                <HelperText 
                  type="error" 
                  visible 
                  style={styles.helperText}
                  accessible={true}
                  accessibilityLabel="Country code validation error"
                  accessibilityLiveRegion="polite"
                >
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
              error={touched.diversityType && !!errors.diversityType}
              style={styles.input}
              accessibilityLabel="Diversity type input field"
              accessibilityHint="Enter your diversity type if applicable"
              accessibilityRole="text"
            />

            {touched.diversityType && errors.diversityType && (
              <HelperText 
                type="error" 
                visible={!!errors.diversityType}
                accessible={true}
                accessibilityLabel="Diversity type validation error"
                accessibilityLiveRegion="polite"
              >
                {errors.diversityType}
              </HelperText>
            )}

            <Button
              mode="contained"
              onPress={handleSubmit}
              disabled={!isFormValid}
              loading={loading}
              style={[styles.button, !isFormValid && styles.buttonDisabled]}
              accessibilityLabel="Create account button"
              accessibilityHint="Press to create your account"
              accessibilityRole="button"
              accessibilityState={{ disabled: !isFormValid }}
            >
              {loading ? 'Creating...' : 'Create Account'}
            </Button>

            <Button
              mode="text"
              onPress={() => {
                navigation.navigate('Login');
              }}
              style={styles.linkButton}
              accessibilityLabel="Sign in link"
              accessibilityHint="Navigate to login page"
              accessibilityRole="link"
            >
              Already have an account? Sign In
            </Button>
          </Card.Content>
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
}
