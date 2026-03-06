import React, { useState, useRef } from 'react';
import { ScrollView } from 'react-native';
import { Button, Text, Card, HelperText } from 'react-native-paper';
import FormInput from './common/FormInput';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';
import { changePassword } from '../utils/api';
import { useFormValidation } from '../hooks/useFormValidation';
import { validatePassword, validatePasswordMatch } from '../utils/validation';
import { styles } from './styles/ChangePasswordScreen.styles';

type Props = NativeStackScreenProps<RootStackParamList, 'ChangePassword'>;

export default function ChangePasswordScreen({ navigation }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const newPasswordRef = useRef<any>(null);
  const confirmPasswordRef = useRef<any>(null);

  const { formData, errors, touched, handleBlur, handleChange, validateForm } = useFormValidation(
    {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    },
    (data) => ({
      currentPassword: validatePassword,
      newPassword: validatePassword,
      confirmPassword: (value: string) => validatePasswordMatch(data.newPassword, value),
    })
  );

  const isFormValid =
    formData.currentPassword !== '' &&
    formData.newPassword !== '' &&
    formData.confirmPassword !== '' &&
    Object.values(errors).every((error) => error === '');

  const handleSubmit = async () => {
    if (validateForm()) {
      try {
        setLoading(true);
        setError('');
        setSuccess('');

        await changePassword(formData.currentPassword, formData.newPassword);

        setSuccess('Password changed successfully!');

        // Clear form
        handleChange('currentPassword')('');
        handleChange('newPassword')('');
        handleChange('confirmPassword')('');

        // Navigate back after a short delay
        setTimeout(() => {
          navigation.goBack();
        }, 1000);
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.detail ||
          err.response?.data?.message ||
          'Failed to change password. Please try again.';
        setError(errorMessage);
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['bottom', 'left', 'right']}>
      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
        automaticallyAdjustKeyboardInsets={true}
      >
        <Text variant="bodyLarge" style={styles.subtitle}>
          Change your account password
        </Text>

        {error && (
          <HelperText
            type="error"
            visible
            style={styles.apiError}
            accessible={true}
            accessibilityLabel="Error message"
            accessibilityLiveRegion="polite"
          >
            {error}
          </HelperText>
        )}

        {success && (
          <HelperText
            type="info"
            visible
            style={styles.successMessage}
            accessible={true}
            accessibilityLabel="Success message"
            accessibilityLiveRegion="polite"
          >
            {success}
          </HelperText>
        )}

        <Card style={styles.card}>
          <Card.Content>
            <FormInput
              label="Current Password *"
              value={formData.currentPassword}
              onChangeText={handleChange('currentPassword')}
              onBlur={handleBlur('currentPassword')}
              touched={touched.currentPassword}
              errorMessage={errors.currentPassword}
              accessibilityLabel="Current password input field"
              accessibilityHint="Enter your current password"
              icon="lock"
              secureTextEntry={!showCurrentPassword}
              showSecureToggle
              isSecureVisible={showCurrentPassword}
              onToggleSecure={() => setShowCurrentPassword(!showCurrentPassword)}
              returnKeyType="next"
              submitBehavior="submit"
              onSubmitEditing={() => newPasswordRef.current?.focus()}
              disabled={loading}
              style={styles.input}
            />

            <FormInput
              ref={newPasswordRef}
              label="New Password *"
              value={formData.newPassword}
              onChangeText={handleChange('newPassword')}
              onBlur={handleBlur('newPassword')}
              touched={touched.newPassword}
              errorMessage={errors.newPassword}
              accessibilityLabel="New password input field"
              accessibilityHint="Enter your new password, minimum 8 characters"
              icon="lock-reset"
              secureTextEntry={!showNewPassword}
              showSecureToggle
              isSecureVisible={showNewPassword}
              onToggleSecure={() => setShowNewPassword(!showNewPassword)}
              returnKeyType="next"
              submitBehavior="submit"
              onSubmitEditing={() => confirmPasswordRef.current?.focus()}
              disabled={loading}
              style={styles.input}
            />

            <FormInput
              ref={confirmPasswordRef}
              label="Confirm New Password *"
              value={formData.confirmPassword}
              onChangeText={handleChange('confirmPassword')}
              onBlur={handleBlur('confirmPassword')}
              touched={touched.confirmPassword}
              errorMessage={errors.confirmPassword}
              accessibilityLabel="Confirm new password input field"
              accessibilityHint="Re-enter your new password to confirm"
              icon="lock-check"
              secureTextEntry={!showConfirmPassword}
              showSecureToggle
              isSecureVisible={showConfirmPassword}
              onToggleSecure={() => setShowConfirmPassword(!showConfirmPassword)}
              returnKeyType="done"
              disabled={loading}
              style={styles.input}
            />
          </Card.Content>
        </Card>

        <Button
          mode="contained"
          onPress={handleSubmit}
          loading={loading}
          disabled={loading || !isFormValid}
          style={[styles.button, !isFormValid && styles.buttonDisabled]}
          accessibilityLabel="Change password button"
          accessibilityHint="Press to change your password"
          accessibilityState={{ disabled: loading || !isFormValid }}
        >
          {loading ? 'Changing...' : 'Change Password'}
        </Button>
      </ScrollView>
    </SafeAreaView>
  );
}
