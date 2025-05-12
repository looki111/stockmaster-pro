import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, Button, Avatar, useTheme } from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AppStackParamList } from '../../types';

type HomeScreenProps = {
  navigation: NativeStackNavigationProp<AppStackParamList, 'Home'>;
};

export default function HomeScreen({ navigation }: HomeScreenProps) {
  const { session, signOut } = useAuth();
  const theme = useTheme();

  const handleSignOut = async () => {
    await signOut();
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text variant="headlineMedium" style={styles.title}>
          Welcome, {session.user?.email?.split('@')[0] || 'User'}
        </Text>
        <Avatar.Text 
          size={40} 
          label={(session.user?.email?.charAt(0) || 'U').toUpperCase()} 
          backgroundColor={theme.colors.primary}
        />
      </View>

      <ScrollView style={styles.content}>
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleLarge">Getting Started</Text>
            <Text variant="bodyMedium" style={styles.cardText}>
              This is your home screen. You can customize it to display your app's main features.
            </Text>
          </Card.Content>
          <Card.Actions>
            <Button>Explore</Button>
          </Card.Actions>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleLarge">Your Profile</Text>
            <Text variant="bodyMedium" style={styles.cardText}>
              View and edit your profile information.
            </Text>
          </Card.Content>
          <Card.Actions>
            <Button onPress={() => navigation.navigate('Profile')}>View Profile</Button>
          </Card.Actions>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleLarge">Settings</Text>
            <Text variant="bodyMedium" style={styles.cardText}>
              Configure your app preferences and account settings.
            </Text>
          </Card.Content>
          <Card.Actions>
            <Button onPress={() => navigation.navigate('Settings')}>Open Settings</Button>
          </Card.Actions>
        </Card>

        <Button 
          mode="outlined" 
          onPress={handleSignOut} 
          style={styles.signOutButton}
        >
          Sign Out
        </Button>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    elevation: 2,
  },
  title: {
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  card: {
    marginBottom: 16,
    elevation: 2,
  },
  cardText: {
    marginTop: 8,
  },
  signOutButton: {
    marginTop: 16,
    marginBottom: 32,
  },
});
