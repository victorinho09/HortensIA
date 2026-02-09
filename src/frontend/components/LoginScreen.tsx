import React, { useState } from 'react';
import { ScrollView, View } from 'react-native';
import { Text, Card, TextInput, Button, HelperText,useTheme } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from './navigation/types';
import {styles} from './styles/LoginScreen.styles';

type Props = NativeStackScreenProps<RootStackParamList, 'Login'>;

export default function LoginScreen({ navigation }: Props) {
  const theme = useTheme()
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#f5f5f5' }}>
      <ScrollView
        contentContainerStyle={{ flexGrow: 1, padding: 16, paddingTop: 16 }}
      >
        <Text
          variant="headlineMedium"
          style={styles.title}
        >
          Log In
        </Text>
        <View style={styles.linkContainer}>
          <Text 
          variant='bodyMedium' 
          style={styles.linkText}
        >
          Don't have an account?
        </Text>
        <Text
          variant='bodyMedium'
          style={[styles.link, { color: theme.colors.primary }]}
          onPress={() => {navigation.navigate('Register')}}
        >
          Register
        </Text>
        </View>
        
      </ScrollView>
    </SafeAreaView>
  );
}
