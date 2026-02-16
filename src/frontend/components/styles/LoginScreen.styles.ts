import { StyleSheet } from 'react-native';
import { commonStyles } from './common.styles';

const loginSpecificStyles = StyleSheet.create({
  container: {
    ...commonStyles.container,
    justifyContent: 'center',
  },
  content: {
    ...commonStyles.content,
    flexGrow: 1,
    padding: 24,
    justifyContent: 'center',
  },
  title: {
    ...commonStyles.title,
    fontSize: 32,
  },
  subtitle: {
    ...commonStyles.subtitle,
    marginBottom: 32,
    fontSize: 16,
  },
  card: {
    ...commonStyles.card,
    borderRadius: 16,
    elevation: 3,
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
