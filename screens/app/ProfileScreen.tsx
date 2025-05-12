import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { Text, Avatar, TextInput, Button, Divider, useTheme } from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import { supabase } from '../../lib/supabase';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AppStackParamList } from '../../types';

type ProfileScreenProps = {
  navigation: NativeStackNavigationProp<AppStackParamList, 'Profile'>;
};

export default function ProfileScreen({ navigation }: ProfileScreenProps) {
  const { session } = useAuth();
  const theme = useTheme();
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (session.user) {
      fetchProfile();
    }
  }, [session]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      
      if (!session.user?.id) return;
      
      const { data, error } = await supabase
        .from('profiles')
        .select('username')
        .eq('id', session.user.id)
        .single();
      
      if (error) {
        console.error('Error fetching profile:', error);
      } else if (data) {
        setUsername(data.username || '');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async () => {
    try {
      setUpdating(true);
      
      if (!session.user?.id) return;
      
      const { error } = await supabase
        .from('profiles')
        .upsert({
          id: session.user.id,
          username,
          updated_at: new Date().toISOString(),
        });
      
      if (error) {
        Alert.alert('Error', error.message);
      } else {
        Alert.alert('Success', 'Profile updated successfully');
      }
    } catch (error: any) {
      Alert.alert('Error', error.message);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.avatarContainer}>
          <Avatar.Text 
            size={80} 
            label={(session.user?.email?.charAt(0) || 'U').toUpperCase()} 
            backgroundColor={theme.colors.primary}
          />
          <TouchableOpacity style={styles.changeAvatarButton}>
            <Text style={{ color: theme.colors.primary }}>Change Avatar</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.infoContainer}>
          <Text variant="titleMedium" style={styles.sectionTitle}>Account Information</Text>
          
          <TextInput
            label="Email"
            value={session.user?.email || ''}
            disabled
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
            loading={updating}
            disabled={updating || loading}
            style={styles.updateButton}
          >
            Update Profile
          </Button>
        </View>

        <Divider style={styles.divider} />

        <View style={styles.securityContainer}>
          <Text variant="titleMedium" style={styles.sectionTitle}>Security</Text>
          
          <Button 
            mode="outlined" 
            onPress={() => {
              // Navigate to change password screen or implement password change logic
              Alert.alert('Change Password', 'This feature is not implemented yet');
            }}
            style={styles.securityButton}
          >
            Change Password
          </Button>
          
          <Button 
            mode="outlined" 
            onPress={() => {
              // Navigate to two-factor authentication screen or implement 2FA logic
              Alert.alert('Two-Factor Authentication', 'This feature is not implemented yet');
            }}
            style={styles.securityButton}
          >
            Two-Factor Authentication
          </Button>
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
  scrollContainer: {
    padding: 16,
  },
  avatarContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  changeAvatarButton: {
    marginTop: 8,
  },
  infoContainer: {
    marginBottom: 24,
  },
  sectionTitle: {
    marginBottom: 16,
    fontWeight: 'bold',
  },
  input: {
    marginBottom: 16,
  },
  updateButton: {
    marginTop: 8,
  },
  divider: {
    marginVertical: 16,
  },
  securityContainer: {
    marginBottom: 24,
  },
  securityButton: {
    marginBottom: 16,
  },
});
