import React, { useState, useCallback } from 'react';
import { View, ScrollView, Alert } from 'react-native';
import { TextInput, Button, Text, ActivityIndicator, Card, Divider, HelperText } from 'react-native-paper';
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

export default function ProfileScreen({navigation}: Props){
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [originalData, setOriginalData] = useState<any>(null);

    const {formData, errors, touched, handleBlur, handleChange, validateForm, setAllTouched} = useFormValidation(
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

    const isFormValid = Object.values(errors).every(e => e === '');

    const handleSave = async () => {
        if (validateForm()) {
            try {
                setLoading(true);
                setError('');

                const normalize = (value: any) => (value === null || value === '') ? null : value;
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
        <SafeAreaView style={styles.container}>
            <ScrollView contentContainerStyle={styles.content}>
                <Text variant="bodyMedium" style={styles.subtitle}>
                    View and manage your account information
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
                                <Text variant="titleMedium" style={styles.sectionTitle}>Personal Information</Text>
                                <Divider style={styles.divider} />

                                <TextInput
                                    label="Name"
                                    value={formData.name}
                                    onChangeText={handleChange('name')}
                                    onBlur={handleBlur('name')}
                                    mode="outlined"
                                    left={<TextInput.Icon icon="account" />}
                                    error={touched.name && !!errors.name}
                                    disabled={loading}
                                    style={styles.input}
                                />
                                {touched.name && errors.name && (
                                    <HelperText type="error" visible accessible={true} accessibilityLiveRegion="polite">
                                        {errors.name}
                                    </HelperText>
                                )}

                                <TextInput
                                    label="Email"
                                    value={originalData.email}
                                    mode="outlined"
                                    left={<TextInput.Icon icon="email" />}
                                    disabled
                                    style={styles.input}
                                />
                                <HelperText type="info" visible>
                                    Email cannot be changed
                                </HelperText>
                            </Card.Content>
                        </Card>

                        <Card style={styles.card}>
                            <Card.Content>
                                <Text variant="titleMedium" style={styles.sectionTitle}>Contact Information</Text>
                                <Divider style={styles.divider} />

                                <TextInput
                                    label="Contact Email"
                                    value={formData.contactEmail}
                                    onChangeText={handleChange('contactEmail')}
                                    onBlur={handleBlur('contactEmail')}
                                    mode="outlined"
                                    left={<TextInput.Icon icon="email-outline" />}
                                    error={touched.contactEmail && !!errors.contactEmail}
                                    disabled={loading}
                                    style={styles.input}
                                />
                                {touched.contactEmail && errors.contactEmail && (
                                    <HelperText type="error" visible accessible={true} accessibilityLiveRegion="polite">
                                        {errors.contactEmail}
                                    </HelperText>
                                )}

                                <View style={styles.row}>
                                    <TextInput
                                        label="Country Code"
                                        value={formData.countryCode}
                                        onChangeText={handleChange('countryCode')}
                                        onBlur={handleBlur('countryCode')}
                                        mode="outlined"
                                        error={touched.countryCode && !!errors.countryCode}
                                        disabled={loading}
                                        style={[styles.input, styles.countryCodeInput]}
                                    />
                                    <TextInput
                                        label="Phone Number"
                                        value={formData.phone}
                                        onChangeText={handleChange('phone')}
                                        onBlur={handleBlur('phone')}
                                        mode="outlined"
                                        error={touched.phone && !!errors.phone}
                                        disabled={loading}
                                        style={[styles.input, styles.phoneInput]}
                                    />
                                </View>
                                {touched.phone && errors.phone && (
                                    <HelperText type="error" visible accessible={true} accessibilityLiveRegion="polite">
                                        {errors.phone}
                                    </HelperText>
                                )}
                            </Card.Content>
                        </Card>

                        <Card style={styles.card}>
                            <Card.Content>
                                <Text variant="titleMedium" style={styles.sectionTitle}>Accessibility</Text>
                                <Divider style={styles.divider} />

                                <TextInput
                                    label="Diversity Type"
                                    value={formData.diversityType}
                                    onChangeText={handleChange('diversityType')}
                                    onBlur={handleBlur('diversityType')}
                                    mode="outlined"
                                    left={<TextInput.Icon icon="wheelchair-accessibility" />}
                                    error={touched.diversityType && !!errors.diversityType}
                                    disabled={loading}
                                    style={styles.input}
                                />
                                {touched.diversityType && errors.diversityType && (
                                    <HelperText type="error" visible accessible={true} accessibilityLiveRegion="polite">
                                        {errors.diversityType}
                                    </HelperText>
                                )}
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