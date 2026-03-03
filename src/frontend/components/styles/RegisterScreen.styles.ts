import { StyleSheet } from 'react-native';
import { commonStyles } from './common.styles';

const registerSpecificStyles = StyleSheet.create({
  logo: {
    width: 80,
    height: 80,
    borderRadius: 18,
    alignSelf: 'center',
    marginTop: 16,
    marginBottom: 8,
  },
  appName: {
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#333',
    marginBottom: 4,
  },
});

export const styles = {
  ...commonStyles,
  ...registerSpecificStyles,
};
