import { StyleSheet } from 'react-native';
import { commonStyles } from './common.styles';

const loginSpecificStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
  },
  content: {
    flexGrow: 1,
    padding: 24,
    justifyContent: 'center',
  },
  title: {
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
    color: '#333',
    fontSize: 32,
  },
  subtitle: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 32,
    fontSize: 16,
  },
  card: {
    borderRadius: 16,
    elevation: 3,
    paddingBottom: 24,
  },
  linkContainer: {
    marginTop: 20,
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 6,
  },
  linkText: {
    textAlign: 'center',
    color: '#666',
  },
  link: {
    fontWeight: 'bold',
  },
});

export const styles = {
  ...commonStyles,
  ...loginSpecificStyles,
};
