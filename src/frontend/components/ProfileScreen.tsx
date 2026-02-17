import React, { useEffect, useState, useCallback } from 'react';
import { ScrollView } from 'react-native';
import { Text, Button, Card, ActivityIndicator, Divider } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useFocusEffect } from '@react-navigation/native';
import { RootStackParamList } from './navigation/types';
import { getSession } from '../utils/session';
import { getCurrentUser } from '../utils/api';
import { profileStyles as styles } from './styles/ProfileScreen.styles';

type Props = NativeStackScreenProps<RootStackParamList, 'Profile'>;

export default function ProfileScreen({navigation}: Props){
    const [user,setUser] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error,setError] = useState('');

    const loadUserData = useCallback(async () => {
        try {
            setLoading(true);
            const sessionId = await getSession();
            if (!sessionId) {
                navigation.replace('Login');
                return;
            }
            const userData = await getCurrentUser(sessionId);
            setUser(userData);
        } catch(err){
            setError('Failed to load profile');
            console.error(err);
        } finally{
            setLoading(false);
        }
    }, [navigation]);

    useFocusEffect(
        useCallback(() => {
            loadUserData();
        }, [loadUserData])
    );

    if (loading){
        return (
        <SafeAreaView style={styles.container}>
            <ActivityIndicator size="large" style={styles.centerContent} />
        </SafeAreaView>
        );
    }


    if (error || !user) {
        return (
        <SafeAreaView style={styles.container}>
            <Text style={styles.errorText}>{error || 'Failed to load profile'}</Text>
        </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
        <ScrollView contentContainerStyle={styles.content}>
            <Text 
                variant="bodyMedium" 
                style={styles.subtitle}
            >
                View and manage your account information
            </Text>

            <Card style={styles.card}>
                <Card.Content>
                    <Text variant="titleMedium" style={styles.sectionTitle}>Personal Information</Text>
                    <Divider style={styles.divider} />
                    
                    <Text style={styles.label}>Name</Text>
                    <Text style={styles.value}>{user.name}</Text>
                    
                    <Text style={styles.label}>Email</Text>
                    <Text style={styles.value}>{user.email}</Text>
                </Card.Content>
            </Card>

            <Card style={styles.card}>
                <Card.Content>
                    <Text variant="titleMedium" style={styles.sectionTitle}>Contact Information</Text>
                    <Divider style={styles.divider} />
                    
                    <Text style={styles.label}>Contact Email</Text>
                    <Text style={styles.value}>{user.contact_person_email || 'Not set'}</Text>
                    
                    <Text style={styles.label}>Phone Number</Text>
                    <Text style={styles.value}>
                        {user.contact_person_country_code && user.contact_person_phone_number
                        ? `+${user.contact_person_country_code} ${user.contact_person_phone_number}`
                        : 'Not set'}
                    </Text>
                </Card.Content>
            </Card>

            <Card style={styles.card}>
                <Card.Content>
                    <Text variant="titleMedium" style={styles.sectionTitle}>Accessibility</Text>
                    <Divider style={styles.divider} />
                    
                    <Text style={styles.label}>Diversity Type</Text>
                    <Text style={styles.value}>{user.diversity_type || 'Not set'}</Text>
                </Card.Content>
            </Card>

            <Button 
                mode="contained" 
                onPress={() => navigation.navigate('EditProfile')}
                style={styles.button}
                accessibilityLabel="Edit profile button"
                accessibilityHint="Press to edit your profile information"
            >
                Edit Profile
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
        </ScrollView>
        </SafeAreaView>
    );
}