import React, { useState, useCallback, useRef } from 'react';
import { View, Alert, ScrollView } from 'react-native';
import {
  TextInput,
  Button,
  Text,
  ActivityIndicator,
  Card,
  Divider,
  HelperText,
} from 'react-native-paper';
import FormInput from './common/FormInput';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useFocusEffect } from '@react-navigation/native';
import { RootStackParamList } from './navigation/types';
import { getSession, clearSession } from '../utils/session';
import { getCurrentUser, updateProfile, deleteAccount } from '../utils/api';
import { useFormValidation } from '../hooks/useFormValidation';
import {
  validateName,
  validateContactEmail,
  validateCountryCode,
  validatePhone,
  validateDiversityType,
} from '../utils/validation';
import { profileStyles as styles } from './styles/ProfileScreen.styles';

type Props = NativeStackScreenProps<RootStackParamList, 'Profile'>;

export default function ProfileScreen({ navigation }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [originalData, setOriginalData] = useState<any>(null);

  const contactEmailRef = useRef<any>(null);
  const countryCodeRef = useRef<any>(null);
  const phoneRef = useRef<any>(null);
  const diversityTypeRef = useRef<any>(null);

  const { formData, errors, touched, handleBlur, handleChange, validateForm, setAllTouched } =
    useFormValidation(
      {
        name: '',
        contactEmail: '',
        countryCode: '',
        phone: '',
        diversityType: '',
      },
      (data) => ({
        name: validateName,
        contactEmail: validateContactEmail,
        countryCode: (value: string) => validateCountryCode(value, data.phone),
        phone: (value: string) => validatePhone(value, data.countryCode),
        diversityType: validateDiversityType,
      })
    );

  const loadUserData = useCallback(async () => {
    try {
      setLoading(true);
      const sessionId = await getSession();
      if (!sessionId) {
        navigation.replace('Login');
        return;
      }
      const userData = await getCurrentUser(sessionId);

      handleChange('name')(userData.name || '');
      handleChange('contactEmail')(userData.contact_person_email || '');
      handleChange('countryCode')(userData.contact_person_country_code || '');
      handleChange('phone')(userData.contact_person_phone_number || '');
      handleChange('diversityType')(userData.diversity_type || '');
      setAllTouched();

      setOriginalData(userData);
    } catch (err) {
      setError('Failed to load profile');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [navigation]);

  useFocusEffect(
    useCallback(() => {
      loadUserData();
    }, [loadUserData])
  );

  const isFormValid = Object.values(errors).every((e) => e === '');

  const handleSave = async () => {
    if (validateForm()) {
      try {
        setLoading(true);
        setError('');

        const normalize = (value: any) => (value === null || value === '' ? null : value);
        const updates: any = {};

        if (normalize(formData.name) !== normalize(originalData.name))
          updates.name = formData.name.trim() || null;
        if (normalize(formData.contactEmail) !== normalize(originalData.contact_person_email))
          updates.contact_person_email = formData.contactEmail.trim() || null;
        if (normalize(formData.countryCode) !== normalize(originalData.contact_person_country_code))
          updates.contact_person_country_code = formData.countryCode.trim() || null;
        if (normalize(formData.phone) !== normalize(originalData.contact_person_phone_number))
          updates.contact_person_phone_number = formData.phone.trim() || null;
        if (normalize(formData.diversityType) !== normalize(originalData.diversity_type))
          updates.diversity_type = formData.diversityType.trim() || null;

        if (Object.keys(updates).length === 0) return;

        await updateProfile(updates);
        await loadUserData();
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to update profile');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
  };

  if (loading && !originalData) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" style={styles.centerContent} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['bottom', 'left', 'right']}>
      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
        automaticallyAdjustKeyboardInsets={true}
      >
        <Text variant="headlineLarge" style={styles.title}>
          Profile
        </Text>

        {error ? (
          <HelperText
            type="error"
            visible
            style={styles.errorText}
            accessible={true}
            accessibilityLiveRegion="polite"
          >
            {error}
          </HelperText>
        ) : null}

        {originalData && (
          <>
            <Card style={styles.card}>
              <Card.Content>
                <Text variant="titleMedium" style={styles.sectionTitle}>
                  Personal Information
                </Text>
                <Divider style={styles.divider} />

                <FormInput
                  label="Name"
                  value={formData.name}
                  onChangeText={handleChange('name')}
                  onBlur={handleBlur('name')}
                  touched={touched.name}
                  errorMessage={errors.name}
                  accessibilityLabel="Name input field"
                  accessibilityHint="Enter your full name"
                  icon="account"
                  disabled={loading}
                  returnKeyType="next"
                  submitBehavior="submit"
                  onSubmitEditing={() => contactEmailRef.current?.focus()}
                  style={styles.input}
                />

                <TextInput
                  label="Email"
                  value={originalData.email}
                  mode="outlined"
                  left={<TextInput.Icon icon="email" />}
                  disabled
                  style={styles.input}
                  accessibilityLabel="Email address (read only)"
                  accessibilityHint="Email cannot be changed"
                  accessibilityRole="text"
                />
                <HelperText type="info" visible>
                  Email cannot be changed
                </HelperText>
              </Card.Content>
            </Card>

            <Card style={styles.card}>
              <Card.Content>
                <Text variant="titleMedium" style={styles.sectionTitle}>
                  Contact Information
                </Text>
                <Divider style={styles.divider} />

                <FormInput
                  ref={contactEmailRef}
                  label="Contact Email"
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
                  disabled={loading}
                  returnKeyType="next"
                  submitBehavior="submit"
                  onSubmitEditing={() => countryCodeRef.current?.focus()}
                  style={styles.input}
                />

                <View style={styles.row}>
                  <FormInput
                    ref={countryCodeRef}
                    label="Country Code"
                    value={formData.countryCode}
                    onChangeText={handleChange('countryCode')}
                    onBlur={handleBlur('countryCode')}
                    touched={touched.countryCode}
                    errorMessage={errors.countryCode}
                    showInlineError={false}
                    accessibilityLabel="Country code input field"
                    accessibilityHint="Enter your country calling code"
                    keyboardType="number-pad"
                    disabled={loading}
                    returnKeyType="next"
                    submitBehavior="submit"
                    onSubmitEditing={() => phoneRef.current?.focus()}
                    style={[styles.input, styles.countryCodeInput]}
                  />
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
                    keyboardType="phone-pad"
                    disabled={loading}
                    returnKeyType="next"
                    submitBehavior="submit"
                    onSubmitEditing={() => diversityTypeRef.current?.focus()}
                    style={[styles.input, styles.phoneInput]}
                  />
                </View>
                {touched.countryCode && errors.countryCode ? (
                  <HelperText
                    type="error"
                    visible
                    accessible={true}
                    accessibilityLiveRegion="polite"
                  >
                    {errors.countryCode}
                  </HelperText>
                ) : null}
                {touched.phone && errors.phone ? (
                  <HelperText
                    type="error"
                    visible
                    accessible={true}
                    accessibilityLiveRegion="polite"
                  >
                    {errors.phone}
                  </HelperText>
                ) : null}
              </Card.Content>
            </Card>

            <Card style={styles.card}>
              <Card.Content>
                <Text variant="titleMedium" style={styles.sectionTitle}>
                  Accessibility
                </Text>
                <Divider style={styles.divider} />

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
                  icon="wheelchair-accessibility"
                  disabled={loading}
                  returnKeyType="done"
                  style={styles.input}
                />
              </Card.Content>
            </Card>
          </>
        )}

        <Button
          mode="contained"
          onPress={handleSave}
          loading={loading}
          disabled={loading || !isFormValid}
          style={[styles.button, (loading || !isFormValid) && styles.buttonDisabled]}
          accessibilityLabel="Save changes button"
          accessibilityHint="Press to save your profile updates"
          accessibilityState={{ disabled: loading || !isFormValid }}
        >
          Save Changes
        </Button>

        <Button
          mode="outlined"
          onPress={() => navigation.navigate('ChangePassword')}
          style={styles.button}
          accessibilityLabel="Change password button"
          accessibilityHint="Press to change your password"
        >
          Change Password
        </Button>

        <Button
          mode="outlined"
          onPress={() =>
            Alert.alert(
              'Delete Account',
              'This will permanently delete your account and all your data. This action cannot be undone.',
              [
                { text: 'Cancel', style: 'cancel' },
                {
                  text: 'Delete',
                  style: 'destructive',
                  onPress: async () => {
                    try {
                      await deleteAccount();
                      await clearSession();
                      navigation.replace('Login');
                    } catch (err) {
                      Alert.alert('Error', 'Could not delete account. Please try again.');
                      console.error(err);
                    }
                  },
                },
              ]
            )
          }
          style={styles.dangerButton}
          textColor="#d32f2f"
          accessibilityLabel="Delete account button"
          accessibilityHint="Press to permanently delete your account"
        >
          Delete Account
        </Button>
      </ScrollView>
    </SafeAreaView>
  );
}
