import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 16,
    paddingTop: 24,
    paddingBottom: 24,
  },
  title: {
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 12,
    marginTop: 4,
    color: '#333',
  },
  card: {
    borderRadius: 12,
    elevation: 2,
  },
  subtitle: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 8,
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
    marginBottom: 16,
  },
  countryCodeInput: {
    flex: 1,
    maxWidth: 120,
  },
  phoneInput: {
    flex: 2,
  },
});
