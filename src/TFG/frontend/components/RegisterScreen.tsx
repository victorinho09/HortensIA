import React, { useState } from 'react';
import { ScrollView, View } from 'react-native';
import { Text, Card, TextInput, Divider, Button } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { styles } from './styles/RegisterScreen.styles';

export default function RegisterScreen() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [countryCode, setCountryCode] = useState('');
  const [phone, setPhone] = useState('');
  const [diversityType, setDiversityType] = useState('');

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text variant="headlineLarge" style={styles.title}>
          Register
        </Text>

        <Card style={styles.card}>
          <Card.Content>
            <TextInput
              label="Name"
              placeholder="Victor Vega"
              value={name}
              onChangeText={setName}
              mode="outlined"
              left={<TextInput.Icon icon="account" />}
              style={styles.input}
            />

            <TextInput
              label="Email"
              placeholder="testaccount@gmail.com"
              value={email}
              onChangeText={setEmail}
              mode="outlined"
              keyboardType="email-address"
              autoCapitalize="none"
              left={<TextInput.Icon icon="email" />}
              style={styles.input}
            />

            <TextInput
              label="Password"
              placeholder="New Password"
              value={password}
              onChangeText={setPassword}
              mode="outlined"
              secureTextEntry
              left={<TextInput.Icon icon="lock" />}
              style={styles.input}
            />

            <TextInput
              label="Confirm Password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              mode="outlined"
              secureTextEntry
              left={<TextInput.Icon icon="lock-check" />}
              style={styles.input}
            />

            <Divider style={styles.divider} />

            <Text variant="titleMedium" style={styles.sectionTitle}>
              Additional Information (Optional)
            </Text>

            <TextInput
              label="Contact Email"
              placeholder="myfriend@gmail.com"
              value={contactEmail}
              onChangeText={setContactEmail}
              mode="outlined"
              keyboardType="email-address"
              autoCapitalize="none"
              left={<TextInput.Icon icon="email-outline" />}
              style={styles.input}
            />

            <View style={styles.row}>
              <TextInput
                label="Country Code"
                value={countryCode}
                onChangeText={setCountryCode}
                mode="outlined"
                keyboardType="number-pad"
                placeholder="34"
                left={<TextInput.Icon icon="phone" />}
                style={[styles.input, styles.countryCodeInput]}
              />

              <TextInput
                label="Phone Number"
                value={phone}
                onChangeText={setPhone}
                mode="outlined"
                keyboardType="phone-pad"
                placeholder="600123456"
                left={<TextInput.Icon icon="cellphone" />}
                style={[styles.input, styles.phoneInput]}
              />
            </View>

            <TextInput
              label="Diversity Type"
              value={diversityType}
              onChangeText={setDiversityType}
              mode="outlined"
              placeholder="e.g., Visual, Hearing, Motor..."
              left={<TextInput.Icon icon="account-group" />}
              style={styles.input}
            />

            <Button
              mode="contained"
              onPress={() => console.log('h')}
              style={styles.button}
            >
              Create Account
            </Button>

            <Button
              mode="text"
              onPress={() => {
                console.log('h');
              }}
              style={styles.linkButton}
            >
              Already have an account? Sign In
            </Button>
          </Card.Content>
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
}
