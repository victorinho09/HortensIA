import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Button } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Profile'>;

export default function HomeScreen({navigation}: Props){
    return (
        <SafeAreaView >
        <ScrollView >
        <Text 
            variant="headlineMedium" 
            accessibilityRole="header"
            accessibilityLabel="Profile page"
            >
            Profile
        </Text>
        </ScrollView>
        </SafeAreaView>
    );
}