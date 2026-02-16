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
});

export const styles = {
  ...commonStyles,
  ...loginSpecificStyles,
};
