import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { Avatar, Title, Caption, Button, TextInput, Text } from 'react-native-paper';
import { supabase } from '../../utils/supabase';
import { SafeAreaView } from 'react-native-safe-area-context';

const ProfileScreen = () => {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const { data } = await supabase.auth.getSession();
      
      if (data.session?.user) {
        setUser(data.session.user);
        
        // Here you could fetch additional user profile data from your Supabase table
        // This is just a placeholder for demonstration
        setFullName('John Doe');
        setUsername('johndoe');
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async () => {
    setUpdateLoading(true);
    
    try {
      // Here you would typically update the user's profile in your database
      // Example:
      // const { error } = await supabase
      //   .from('profiles')
      //   .update({ full_name: fullName, username: username })
      //   .eq('id', user.id);
      
      // if (error) throw error;
      
      Alert.alert('Success', 'Profile updated successfully');
    } catch (error: any) {
      Alert.alert('Error', error.message);
    } finally {
      setUpdateLoading(false);
    }
  };

  const handleSignOut = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
    } catch (error: any) {
      Alert.alert('Error signing out', error.message);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading profile...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Title style={styles.headerTitle}>Profile</Title>
      </View>
      
      <View style={styles.profileSection}>
        <Avatar.Text 
          size={80} 
          label={fullName.substring(0, 2).toUpperCase()} 
          style={styles.avatar}
        />
        <Title style={styles.title}>{fullName}</Title>
        <Caption style={styles.caption}>{user?.email}</Caption>
      </View>
      
      <View style={styles.formContainer}>
        <TextInput
          label="Full Name"
          value={fullName}
          onChangeText={setFullName}
          mode="outlined"
          style={styles.input}
        />
        
        <TextInput
          label="Username"
          value={username}
          onChangeText={setUsername}
          mode="outlined"
          style={styles.input}
        />
        
        <Button 
          mode="contained" 
          onPress={updateProfile}
          loading={updateLoading}
          disabled={updateLoading}
          style={styles.button}
        >
          Update Profile
        </Button>
        
        <Button 
          mode="outlined" 
          onPress={handleSignOut}
          style={styles.signOutButton}
        >
          Sign Out
        </Button>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
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
  profileSection: {
    alignItems: 'center',
    marginVertical: 20,
  },
  avatar: {
    marginBottom: 10,
    backgroundColor: '#6200ee',
  },
  title: {
    marginBottom: 5,
  },
  caption: {
    fontSize: 14,
    lineHeight: 14,
  },
  formContainer: {
    padding: 16,
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 8,
    paddingVertical: 6,
  },
  signOutButton: {
    marginTop: 16,
    paddingVertical: 6,
    borderColor: '#f44336',
    borderWidth: 1,
  },
});

export default ProfileScreen; 