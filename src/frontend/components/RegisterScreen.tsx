import React, { useState, useRef } from 'react';
import { View, Image, ScrollView } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';
import { Text, Card, Divider, Button, HelperText } from 'react-native-paper';
import FormInput from './common/FormInput';
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
import { createUser, login } from '../utils/api';
import { useFormValidation } from '../hooks/useFormValidation';
import { saveSession } from '../utils/session';

type Props = NativeStackScreenProps<RootStackParamList, 'Register'>;

export default function RegisterScreen({ navigation }: Props) {
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const emailRef = useRef<any>(null);
  const passwordRef = useRef<any>(null);
  const confirmPasswordRef = useRef<any>(null);
  const contactEmailRef = useRef<any>(null);
  const phoneRef = useRef<any>(null);
  const countryCodeRef = useRef<any>(null);
  const diversityTypeRef = useRef<any>(null);

  const { formData, errors, touched, handleBlur, handleChange, validateForm } = useFormValidation(
    {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      contactEmail: '',
      countryCode: '',
      phone: '',
      diversityType: '',
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
        const loginResponse = await login(formData.email, formData.password);
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
    Object.values(errors).every((error) => error === '');

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
        automaticallyAdjustKeyboardInsets={true}
      >
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
            <FormInput
              label="Name"
              placeholder="Victor Vega"
              value={formData.name}
              onChangeText={handleChange('name')}
              onBlur={handleBlur('name')}
              touched={touched.name}
              errorMessage={errors.name}
              accessibilityLabel="Name input field"
              accessibilityHint="Enter your full name"
              icon="account"
              returnKeyType="next"
              submitBehavior="submit"
              onSubmitEditing={() => emailRef.current?.focus()}
              style={styles.input}
            />

            <FormInput
              ref={emailRef}
              label="Email *"
              placeholder="testaccount@gmail.com"
              value={formData.email}
              onChangeText={handleChange('email')}
              onBlur={handleBlur('email')}
              touched={touched.email}
              errorMessage={errors.email}
              accessibilityLabel="Email address input field"
              accessibilityHint="Enter your email address"
              icon="email"
              keyboardType="email-address"
              autoCapitalize="none"
              returnKeyType="next"
              submitBehavior="submit"
              onSubmitEditing={() => passwordRef.current?.focus()}
              style={styles.input}
            />

            <FormInput
              ref={passwordRef}
              label="Password *"
              placeholder="New Password"
              value={formData.password}
              onChangeText={handleChange('password')}
              onBlur={handleBlur('password')}
              touched={touched.password}
              errorMessage={errors.password}
              accessibilityLabel="Password input field"
              accessibilityHint="Enter your password, minimum 8 characters"
              icon="lock"
              secureTextEntry={!showPassword}
              showSecureToggle
              isSecureVisible={showPassword}
              onToggleSecure={() => setShowPassword(!showPassword)}
              returnKeyType="next"
              submitBehavior="submit"
              onSubmitEditing={() => confirmPasswordRef.current?.focus()}
              style={styles.input}
            />

            <FormInput
              ref={confirmPasswordRef}
              label="Confirm Password *"
              placeholder="Confirm Password"
              value={formData.confirmPassword}
              onChangeText={handleChange('confirmPassword')}
              onBlur={handleBlur('confirmPassword')}
              touched={touched.confirmPassword}
              errorMessage={errors.confirmPassword}
              accessibilityLabel="Confirm password input field"
              accessibilityHint="Re-enter your password to confirm"
              icon="lock-check"
              secureTextEntry={!showConfirmPassword}
              showSecureToggle
              isSecureVisible={showConfirmPassword}
              onToggleSecure={() => setShowConfirmPassword(!showConfirmPassword)}
              returnKeyType="next"
              submitBehavior="submit"
              onSubmitEditing={() => contactEmailRef.current?.focus()}
              style={styles.input}
            />

            <Divider style={styles.divider} />

            <Text
              variant="titleMedium"
              style={styles.sectionTitle}
              accessibilityRole="header"
              accessibilityLabel="Additional information section"
            >
              Additional Information (Optional)
            </Text>

            <FormInput
              ref={contactEmailRef}
              label="Contact Email"
              placeholder="myfriend@gmail.com"
              value={formData.contactEmail}
              onChangeText={handleChange('contactEmail')}
              onBlur={handleBlur('contactEmail')}
              touched={touched.contactEmail}
              errorMessage={errors.contactEmail}
              accessibilityLabel="Contact email input field"
              accessibilityHint="Enter an alternative contact email"
              icon="email-outline"
              keyboardType="email-address"
              autoCapitalize="none"
              returnKeyType="next"
              submitBehavior="submit"
              onSubmitEditing={() => phoneRef.current?.focus()}
              style={styles.input}
            />

            <View style={styles.row}>
              <FormInput
                ref={phoneRef}
                label="Phone Number"
                value={formData.phone}
                onChangeText={handleChange('phone')}
                onBlur={handleBlur('phone')}
                touched={touched.phone}
                errorMessage={errors.phone}
                showInlineError={false}
                accessibilityLabel="Phone number input field"
                accessibilityHint="Enter your phone number"
                icon="cellphone"
                keyboardType="phone-pad"
                placeholder="600123456"
                returnKeyType="next"
                submitBehavior="submit"
                onSubmitEditing={() => countryCodeRef.current?.focus()}
                style={[styles.input, styles.phoneInput]}
              />

              <FormInput
                ref={countryCodeRef}
                label="CC"
                value={formData.countryCode}
                onChangeText={handleChange('countryCode')}
                onBlur={handleBlur('countryCode')}
                touched={touched.countryCode}
                errorMessage={errors.countryCode}
                showInlineError={false}
                accessibilityLabel="Country code input field"
                accessibilityHint="Enter your country calling code"
                icon="phone"
                keyboardType="number-pad"
                placeholder="34"
                returnKeyType="next"
                submitBehavior="submit"
                onSubmitEditing={() => diversityTypeRef.current?.focus()}
                style={[styles.input, styles.countryCodeInput]}
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

            <FormInput
              ref={diversityTypeRef}
              label="Diversity Type"
              value={formData.diversityType}
              onChangeText={handleChange('diversityType')}
              onBlur={handleBlur('diversityType')}
              touched={touched.diversityType}
              errorMessage={errors.diversityType}
              accessibilityLabel="Diversity type input field"
              accessibilityHint="Enter your diversity type if applicable"
              icon="account-group"
              placeholder="e.g., Visual, Hearing, Motor..."
              returnKeyType="done"
              style={styles.input}
            />

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
