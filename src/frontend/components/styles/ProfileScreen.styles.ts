import { StyleSheet } from 'react-native';
import { commonStyles } from './common.styles';

export const profileStyles = StyleSheet.create({
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
    marginBottom: 12,
  },
  button: {
    ...commonStyles.button,
    marginTop: 4,
    marginBottom: 16,
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
  
  // ProfileScreen-specific styles
  sectionTitle: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  divider: {
    marginBottom: 8,
  },
  label: {
    fontSize: 12,
    color: '#666',
    marginTop: 8,
    marginBottom: 2,
    fontWeight: '500',
  },
  value: {
    fontSize: 16,
    marginBottom: 4,
    color: '#000',
  },
  centerContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    ...commonStyles.apiError,
    textAlign: 'center',
    marginTop: 20,
  },
  dangerButton: {
    ...commonStyles.button,
    marginTop: 4,
    marginBottom: 16,
    borderColor: '#d32f2f',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
});
