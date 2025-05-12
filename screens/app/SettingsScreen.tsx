import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, List, Switch, Button, Divider, useTheme } from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AppStackParamList } from '../../types';

type SettingsScreenProps = {
  navigation: NativeStackNavigationProp<AppStackParamList, 'Settings'>;
};

export default function SettingsScreen({ navigation }: SettingsScreenProps) {
  const { signOut } = useAuth();
  const theme = useTheme();
  
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);
  const [biometricsEnabled, setBiometricsEnabled] = useState(false);
  
  const handleSignOut = async () => {
    await signOut();
  };
  
  const handleDeleteAccount = () => {
    Alert.alert(
      'Delete Account',
      'Are you sure you want to delete your account? This action cannot be undone.',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            // Implement account deletion logic
            Alert.alert('Not Implemented', 'Account deletion is not implemented yet');
          },
        },
      ],
    );
  };

  return (
    <View style={styles.container}>
      <ScrollView>
        <List.Section>
          <List.Subheader>Preferences</List.Subheader>
          
          <List.Item
            title="Notifications"
            description="Receive push notifications"
            left={props => <List.Icon {...props} icon="bell" />}
            right={props => (
              <Switch
                value={notificationsEnabled}
                onValueChange={setNotificationsEnabled}
                color={theme.colors.primary}
              />
            )}
          />
          
          <List.Item
            title="Dark Mode"
            description="Enable dark theme"
            left={props => <List.Icon {...props} icon="theme-light-dark" />}
            right={props => (
              <Switch
                value={darkModeEnabled}
                onValueChange={setDarkModeEnabled}
                color={theme.colors.primary}
              />
            )}
          />
          
          <List.Item
            title="Biometric Authentication"
            description="Use fingerprint or face ID"
            left={props => <List.Icon {...props} icon="fingerprint" />}
            right={props => (
              <Switch
                value={biometricsEnabled}
                onValueChange={setBiometricsEnabled}
                color={theme.colors.primary}
              />
            )}
          />
        </List.Section>
        
        <Divider />
        
        <List.Section>
          <List.Subheader>Account</List.Subheader>
          
          <List.Item
            title="Language"
            description="English"
            left={props => <List.Icon {...props} icon="translate" />}
            onPress={() => Alert.alert('Language', 'Language selection is not implemented yet')}
          />
          
          <List.Item
            title="Privacy Policy"
            left={props => <List.Icon {...props} icon="shield-account" />}
            onPress={() => Alert.alert('Privacy Policy', 'Privacy policy is not implemented yet')}
          />
          
          <List.Item
            title="Terms of Service"
            left={props => <List.Icon {...props} icon="file-document" />}
            onPress={() => Alert.alert('Terms of Service', 'Terms of service is not implemented yet')}
          />
          
          <List.Item
            title="Help & Support"
            left={props => <List.Icon {...props} icon="help-circle" />}
            onPress={() => Alert.alert('Help & Support', 'Help and support is not implemented yet')}
          />
        </List.Section>
        
        <View style={styles.buttonContainer}>
          <Button
            mode="outlined"
            onPress={handleSignOut}
            style={styles.button}
          >
            Sign Out
          </Button>
          
          <Button
            mode="outlined"
            onPress={handleDeleteAccount}
            style={[styles.button, styles.deleteButton]}
            textColor="red"
          >
            Delete Account
          </Button>
        </View>
        
        <View style={styles.versionContainer}>
          <Text variant="bodySmall" style={styles.versionText}>
            Version 1.0.0
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  buttonContainer: {
    padding: 16,
  },
  button: {
    marginBottom: 16,
  },
  deleteButton: {
    borderColor: 'red',
  },
  versionContainer: {
    alignItems: 'center',
    padding: 16,
    marginBottom: 16,
  },
  versionText: {
    opacity: 0.6,
  },
});
