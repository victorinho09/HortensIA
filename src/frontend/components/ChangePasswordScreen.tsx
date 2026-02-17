import React, { useState } from 'react';
import { ScrollView } from 'react-native';
import { TextInput, Button, Text, Card, HelperText } from 'react-native-paper';
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
        Object.values(errors).every(error => error === '');

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
        <SafeAreaView style={styles.container}>
            <ScrollView contentContainerStyle={styles.content}>
                <Text 
                    variant="bodyMedium" 
                    style={styles.subtitle}
                >
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
                        <TextInput
                            label="Current Password *"
                            value={formData.currentPassword}
                            onChangeText={handleChange('currentPassword')}
                            onBlur={handleBlur('currentPassword')}
                            mode="outlined"
                            secureTextEntry={!showCurrentPassword}
                            right={
                                <TextInput.Icon 
                                    icon={showCurrentPassword ? "eye-off" : "eye"}
                                    onPress={() => setShowCurrentPassword(!showCurrentPassword)}
                                    accessibilityLabel={showCurrentPassword ? "Hide password" : "Show password"}
                                />
                            }
                            left={<TextInput.Icon icon="lock" />}
                            error={touched.currentPassword && !!errors.currentPassword}
                            disabled={loading}
                            style={styles.input}
                            accessibilityLabel="Current password input field"
                            accessibilityHint="Enter your current password"
                        />
                        {touched.currentPassword && errors.currentPassword && (
                            <HelperText 
                                type="error" 
                                visible
                                accessible={true}
                                accessibilityLabel="Current password validation error"
                                accessibilityLiveRegion="polite"
                            >
                                {errors.currentPassword}
                            </HelperText>
                        )}

                        <TextInput
                            label="New Password *"
                            value={formData.newPassword}
                            onChangeText={handleChange('newPassword')}
                            onBlur={handleBlur('newPassword')}
                            mode="outlined"
                            secureTextEntry={!showNewPassword}
                            right={
                                <TextInput.Icon 
                                    icon={showNewPassword ? "eye-off" : "eye"}
                                    onPress={() => setShowNewPassword(!showNewPassword)}
                                    accessibilityLabel={showNewPassword ? "Hide password" : "Show password"}
                                />
                            }
                            left={<TextInput.Icon icon="lock-reset" />}
                            error={touched.newPassword && !!errors.newPassword}
                            disabled={loading}
                            style={styles.input}
                            accessibilityLabel="New password input field"
                            accessibilityHint="Enter your new password, minimum 8 characters"
                        />
                        {touched.newPassword && errors.newPassword && (
                            <HelperText 
                                type="error" 
                                visible
                                accessible={true}
                                accessibilityLabel="New password validation error"
                                accessibilityLiveRegion="polite"
                            >
                                {errors.newPassword}
                            </HelperText>
                        )}

                        <TextInput
                            label="Confirm New Password *"
                            value={formData.confirmPassword}
                            onChangeText={handleChange('confirmPassword')}
                            onBlur={handleBlur('confirmPassword')}
                            mode="outlined"
                            secureTextEntry={!showConfirmPassword}
                            right={
                                <TextInput.Icon 
                                    icon={showConfirmPassword ? "eye-off" : "eye"}
                                    onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                                    accessibilityLabel={showConfirmPassword ? "Hide password" : "Show password"}
                                />
                            }
                            left={<TextInput.Icon icon="lock-check" />}
                            error={touched.confirmPassword && !!errors.confirmPassword}
                            disabled={loading}
                            style={styles.input}
                            accessibilityLabel="Confirm new password input field"
                            accessibilityHint="Re-enter your new password to confirm"
                        />
                        {touched.confirmPassword && errors.confirmPassword && (
                            <HelperText 
                                type="error" 
                                visible
                                accessible={true}
                                accessibilityLabel="Confirm password validation error"
                                accessibilityLiveRegion="polite"
                            >
                                {errors.confirmPassword}
                            </HelperText>
                        )}
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