import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Button } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';
import {styles} from './styles/HomeScreen.styles';

type Props = NativeStackScreenProps<RootStackParamList, 'Home'>;

export default function HomeScreen({navigation}: Props){
    return (
        <SafeAreaView style={styles.container}>
        <ScrollView contentContainerStyle={styles.content}>
        <Text 
            variant="headlineMedium" 
            style={styles.title}
            accessibilityRole="header"
            accessibilityLabel="Home page"
            >
            Home 
        </Text>
        </ScrollView>
        </SafeAreaView>
    );
}