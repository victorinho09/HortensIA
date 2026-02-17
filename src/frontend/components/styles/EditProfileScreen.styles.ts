import { StyleSheet } from 'react-native';
import { commonStyles } from './common.styles';

export const editProfileStyles = StyleSheet.create({
  // Reuse common styles
  container: {
    ...commonStyles.container,
  },
  content: {
    ...commonStyles.content,
  },
  title: {
    ...commonStyles.title,
    marginTop: 0,
    marginBottom: 4,
  },
  subtitle: {
    ...commonStyles.subtitle,
    marginBottom: 12,
  },
  card: {
    ...commonStyles.card,
    marginBottom: 16,
  },
  button: {
    ...commonStyles.button,
    marginTop: 8,
    marginBottom: 24,
  },
  buttonDisabled: {
    ...commonStyles.buttonDisabled,
  },
  input: {
    ...commonStyles.input,
  },
  helperText: {
    ...commonStyles.helperText,
  },
  row: {
    ...commonStyles.row,
  },
  countryCodeInput: {
    ...commonStyles.countryCodeInput,
  },
  phoneInput: {
    ...commonStyles.phoneInput,
  },
  
  // EditProfileScreen-specific styles
  sectionTitle: {
    fontWeight: 'bold',
    marginTop: 16,
    marginBottom: 4,
  },
  divider: {
    marginBottom: 12,
  },
  centerContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  apiError: {
    ...commonStyles.apiError,
  },
});
