import { StyleSheet } from 'react-native';
import { commonStyles } from './common.styles';

const SplashSpecificStyles = StyleSheet.create({
  container: {
    ...commonStyles.container,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  logo: {
    width: 120,
    height: 120,
    borderRadius: 28,
    marginBottom: 16,
  },
  appName: {
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 32,
  },
  spinner: {
    marginTop: 8,
  },
  text: {
    marginTop: 16,
  },
});

export const styles = {
  ...commonStyles,
  ...SplashSpecificStyles,
};
