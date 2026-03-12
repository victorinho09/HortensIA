import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  box: {
    position: 'absolute',
    borderWidth: 2,
    borderColor: '#00ff00', // Green for now
  },
  label: {
    position: 'absolute',
    top: -24,
    left: 0,
    backgroundColor: 'rgba(0, 255, 0, 0.8)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  labelText: {
    color: '#000',
    fontSize: 12,
    fontWeight: 'bold',
  },
});
