import { StyleSheet } from 'react-native';

export const commonStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 16,
    paddingTop: 4,
    paddingBottom: 16,
  },
  title: {
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
    marginTop: 0,
    color: '#333',
  },
  subtitle: {
    textAlign: 'center',
    color: '#555',
    marginBottom: 32,
    marginTop: 4,
    fontSize: 16,
    lineHeight: 22,
    paddingHorizontal: 20,
  },
  card: {
    borderRadius: 12,
    elevation: 2,
    paddingBottom: 24,
  },
  divider: {
    marginVertical: 16,
  },
  sectionTitle: {
    marginBottom: 12,
    fontWeight: '600',
    color: '#444',
  },
  input: {
    marginBottom: 12,
    backgroundColor: 'transparent',
  },
  button: {
    marginTop: 24,
    marginBottom: 12,
    borderRadius: 8,
  },
  linkButton: {
    marginTop: 4,
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  countryCodeInput: {
    flex: 1,
    maxWidth: 120,
  },
  phoneInput: {
    flex: 2,
  },
  helperText: {
    marginTop: -8,
    fontSize: 12,
    color: '#d32f2f',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  apiError: {
    backgroundColor: '#ffebee',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    fontSize: 14,
    color: '#c62828',
  },
  successMessage: {
    backgroundColor: '#e8f5e9',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    fontSize: 14,
    color: '#2e7d32',
  },
});
