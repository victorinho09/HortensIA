import React, { useState, useEffect } from 'react';
import { View, ScrollView } from 'react-native';
import { TextInput, Button, Text, ActivityIndicator, Card, Divider, HelperText } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';
import { getCurrentUser, updateProfile } from '../utils/api';
import { getSession } from '../utils/session';
import { useFormValidation } from '../hooks/useFormValidation';
import {
  validateName,
  validateContactEmail,
  validateCountryCode,
  validatePhone,
  validateDiversityType,
} from '../utils/validation';
import { editProfileStyles as styles } from './styles/EditProfileScreen.styles';

type Props = NativeStackScreenProps<RootStackParamList, 'EditProfile'>;

export default function EditProfileScreen({navigation}: Props){
    const [loading,setLoading] = useState(false);
    const [error,setError] = useState('');
    const [originalData,setOriginalData] = useState<any>(null);
    const {formData,errors,touched,handleBlur,handleChange,validateForm,setAllTouched} = useFormValidation(
        {
            name: '',
            contactEmail: '',
            countryCode:'',
            phone: '',
            diversityType: '',
        },
        (data) => ({
            name: validateName,
            contactEmail: validateContactEmail,
            countryCode: (value: string) => validateCountryCode(value,data.phone),
            phone: (value: string) => validatePhone(value,data.countryCode),
            diversityType: validateDiversityType,
        })
    );

    useEffect(() => {
        loadUserData();
    }, []);

    const loadUserData = async () => {
        try{
            setLoading(true);
            const sessionId = await getSession();
            if (!sessionId){
                navigation.replace('Login');
                return;
            }
            const userData = await getCurrentUser(sessionId)

            // Pre-fill form 
            handleChange('name')(userData.name || '');
            handleChange('contactEmail')(userData.contact_person_email || '');
            handleChange('countryCode')(userData.contact_person_country_code || '');
            handleChange('phone')(userData.contact_person_phone_number || '');
            handleChange('diversityType')(userData.diversity_type || '');
            
            // Mark all fields as touched so validation works on change
            setAllTouched();
            
            setOriginalData(userData);
        } catch(err){
            setError('Failed to load profile');
            console.error(err);
        } finally{
            setLoading(false);
        }
    };

    const isFormValid = Object.values(errors).every(error => error === '');

    const handleSave = async () => {
        if (validateForm()){
            try{
                setLoading(true);
                setError('');

                const updates: any = {};

                // Only add fields that have changed AND are not empty
                if (formData.name !== originalData.name && formData.name.trim()) {
                    updates.name = formData.name;
                }
                if (formData.contactEmail !== originalData.contact_person_email) {
                    updates.contact_person_email = formData.contactEmail.trim() || null;
                }
                if (formData.countryCode !== originalData.contact_person_country_code) {
                    updates.contact_person_country_code = formData.countryCode.trim() || null;
                }
                if (formData.phone !== originalData.contact_person_phone_number) {
                    updates.contact_person_phone_number = formData.phone.trim() || null;
                }
                if (formData.diversityType !== originalData.diversity_type) {
                    updates.diversity_type = formData.diversityType.trim() || null;
                }

                //If there are no changes, go back to profile screen
                if(Object.keys(updates).length === 0){
                    navigation.goBack();
                    return;
                }

                await updateProfile(updates);
                navigation.goBack();
            } catch(err: any){
                setError(err.response?.data?.detail || 'Failed to update profile');
                console.error(err);
            } finally {
                setLoading(false);
            }
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            {loading && (
                <ActivityIndicator size="large" style={styles.centerContent} />
            )}
            {!loading && (
                <ScrollView contentContainerStyle={styles.content}>
                    <Text 
                        variant="bodyMedium" 
                        style={styles.subtitle}
                    >
                        Update your account information
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

                    {originalData && (
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
                                    <HelperText 
                                        type="error" 
                                        visible
                                        accessible={true}
                                        accessibilityLabel="Name validation error"
                                        accessibilityLiveRegion="polite"
                                    >
                                        {errors.name}
                                    </HelperText>
                                )}

                                <TextInput
                                    label="Email"
                                    value={originalData.email}
                                    mode="outlined"
                                    left={<TextInput.Icon icon="email" />}
                                    disabled={true}
                                    style={styles.input}
                                />
                                <HelperText type="info" visible>
                                    Email cannot be changed
                                </HelperText>

                                <Text variant="titleMedium" style={[styles.sectionTitle, { marginTop: 16 }]}>Contact Information</Text>
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
                                    <HelperText 
                                        type="error" 
                                        visible
                                        accessible={true}
                                        accessibilityLabel="Contact email validation error"
                                        accessibilityLiveRegion="polite"
                                    >
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
                                    <HelperText 
                                        type="error" 
                                        visible
                                        accessible={true}
                                        accessibilityLabel="Phone validation error"
                                        accessibilityLiveRegion="polite"
                                    >
                                        {errors.phone}
                                    </HelperText>
                                )}

                                <Text variant="titleMedium" style={[styles.sectionTitle, { marginTop: 16 }]}>Accessibility</Text>
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
                                    <HelperText 
                                        type="error" 
                                        visible
                                        accessible={true}
                                        accessibilityLabel="Diversity type validation error"
                                        accessibilityLiveRegion="polite"
                                    >
                                        {errors.diversityType}
                                    </HelperText>
                                )}
                            </Card.Content>
                        </Card>
                    )}

                    <Button
                        mode="contained"
                        onPress={handleSave}
                        loading={loading}
                        disabled={loading || !isFormValid}
                        style={[styles.button, !isFormValid && styles.buttonDisabled]}
                        accessibilityLabel="Save changes button"
                        accessibilityHint="Press to save your profile updates"
                        accessibilityState={{ disabled: loading || !isFormValid }}
                    >
                        Save Changes
                    </Button>
                </ScrollView>
            )}
        </SafeAreaView>
    );
}