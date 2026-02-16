import { StyleSheet } from 'react-native';
import { commonStyles } from './common.styles';

const SplashSpecificStyles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  text: {
    marginTop: 16,
  },
});

export const styles = {
  ...commonStyles,
  ...SplashSpecificStyles,
};
