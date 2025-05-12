import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Switch, Alert } from 'react-native';
import { List, Divider, Title, Text, Button } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { supabase } from '../../utils/supabase';

const SettingsScreen = () => {
  const [pushNotifications, setPushNotifications] = useState(true);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [biometricLogin, setBiometricLogin] = useState(false);

  const togglePushNotifications = () => setPushNotifications(!pushNotifications);
  const toggleEmailNotifications = () => setEmailNotifications(!emailNotifications);
  const toggleDarkMode = () => setDarkMode(!darkMode);
  const toggleBiometricLogin = () => setBiometricLogin(!biometricLogin);

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
          onPress: async () => {
            try {
              // Here you would delete the user's account
              // For demonstration purposes only
              // const { error } = await supabase.auth.api.deleteUser(user.id)
              Alert.alert('Account deleted successfully');
            } catch (error: any) {
              Alert.alert('Error', error.message);
            }
          },
        },
      ],
    );
  };

  const handleSignOut = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
    } catch (error: any) {
      Alert.alert('Error signing out', error.message);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Title style={styles.headerTitle}>Settings</Title>
      </View>
      
      <ScrollView style={styles.content}>
        <List.Section>
          <List.Subheader>Notifications</List.Subheader>
          <List.Item
            title="Push Notifications"
            right={() => <Switch value={pushNotifications} onValueChange={togglePushNotifications} />}
          />
          <List.Item
            title="Email Notifications"
            right={() => <Switch value={emailNotifications} onValueChange={toggleEmailNotifications} />}
          />
          <Divider />

          <List.Subheader>Appearance</List.Subheader>
          <List.Item
            title="Dark Mode"
            right={() => <Switch value={darkMode} onValueChange={toggleDarkMode} />}
          />
          <Divider />

          <List.Subheader>Security</List.Subheader>
          <List.Item
            title="Biometric Login"
            right={() => <Switch value={biometricLogin} onValueChange={toggleBiometricLogin} />}
          />
          <List.Item
            title="Change Password"
            onPress={() => Alert.alert('Change Password', 'This feature would allow users to change their password.')}
            right={props => <List.Icon {...props} icon="chevron-right" />}
          />
          <Divider />

          <List.Subheader>About</List.Subheader>
          <List.Item
            title="App Version"
            description="1.0.0"
          />
          <List.Item
            title="Terms of Service"
            onPress={() => Alert.alert('Terms of Service', 'This would show the Terms of Service.')}
            right={props => <List.Icon {...props} icon="chevron-right" />}
          />
          <List.Item
            title="Privacy Policy"
            onPress={() => Alert.alert('Privacy Policy', 'This would show the Privacy Policy.')}
            right={props => <List.Icon {...props} icon="chevron-right" />}
          />
          <Divider />

          <View style={styles.buttonContainer}>
            <Button 
              mode="outlined" 
              onPress={handleSignOut}
              style={styles.signOutButton}
            >
              Sign Out
            </Button>
            
            <Button 
              mode="outlined" 
              onPress={handleDeleteAccount}
              style={styles.deleteButton}
              textColor="#f44336"
            >
              Delete Account
            </Button>
          </View>
        </List.Section>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 20,
  },
  content: {
    flex: 1,
  },
  buttonContainer: {
    padding: 16,
    gap: 12,
  },
  signOutButton: {
    borderColor: '#6200ee',
  },
  deleteButton: {
    borderColor: '#f44336',
  },
});

export default SettingsScreen; 