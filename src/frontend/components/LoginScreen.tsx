import React, { useState } from 'react';
import { ScrollView } from 'react-native';
import { Text, Card, TextInput, Button, HelperText } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Login'>;

export default function LoginScreen({ navigation }: Props) {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#f5f5f5' }}>
      <ScrollView
        contentContainerStyle={{ flexGrow: 1, padding: 16, paddingTop: 16 }}
      >
        <Text
          variant="headlineMedium"
          style={{ fontWeight: 'bold', textAlign: 'center', marginBottom: 8 }}
        >
          Sign In
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}
