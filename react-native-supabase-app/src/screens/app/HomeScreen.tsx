import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Card, Title, Paragraph, Button, Text } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';

const HomeScreen = () => {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Title style={styles.headerTitle}>Home</Title>
      </View>
      
      <ScrollView style={styles.content}>
        <Card style={styles.card}>
          <Card.Content>
            <Title>Welcome to your app!</Title>
            <Paragraph>
              This is your home screen. You can customize this to display your app's content.
            </Paragraph>
          </Card.Content>
          <Card.Actions>
            <Button>Get Started</Button>
          </Card.Actions>
        </Card>
        
        <Card style={styles.card}>
          <Card.Content>
            <Title>Features</Title>
            <Paragraph>- Authentication ready with Supabase</Paragraph>
            <Paragraph>- Environment variables configured</Paragraph>
            <Paragraph>- React Navigation for screen management</Paragraph>
            <Paragraph>- React Native Paper UI components</Paragraph>
          </Card.Content>
        </Card>
        
        <Card style={styles.card}>
          <Card.Content>
            <Title>Next Steps</Title>
            <Paragraph>
              Start building your app by adding more screens and functionality.
            </Paragraph>
          </Card.Content>
          <Card.Actions>
            <Button>Documentation</Button>
          </Card.Actions>
        </Card>
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
    padding: 16,
  },
  card: {
    marginBottom: 16,
  },
});

export default HomeScreen;