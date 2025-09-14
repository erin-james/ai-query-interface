import React, { useState } from 'react';
import {
  Button,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { queryCSV } from '../services/api';

/**
 * ChatScreen component provides a simple chat interface
 * for querying CSV-based data via a backend API.
 * Displays user and bot messages in styled bubbles,
 * handles loading state and timeout fallback.
 */
const ChatScreen = () => {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Sends the user's question to the backend and updates message history.
   * Includes a 7-second timeout fallback in case the request hangs.
   */
  const handleSend = async () => {
    if (!question.trim()) return;

    // Add user message to chat
    setMessages(prev => [...prev, { sender: 'user', text: question }]);
    setIsLoading(true);

    // Timeout fallback
    const timeout = new Promise<string>(resolve =>
      setTimeout(() => resolve('Sorry, that request timed out.'), 7000)
    );

    try {
      const response = await Promise.race([queryCSV(question), timeout]);
      setMessages(prev => [...prev, { sender: 'bot', text: response }]);
    } catch (error) {
      setMessages(prev => [
        ...prev,
        { sender: 'bot', text: 'Sorry, something went wrong.' },
      ]);
    }

    setIsLoading(false);
    setQuestion('');
  };

  return (
    <View style={styles.container}>
      {/* Chat history */}
      <ScrollView style={styles.chat}>
        {messages.map((msg, index) => (
          <Text key={index} style={msg.sender === 'user' ? styles.user : styles.bot}>
            {msg.text}
          </Text>
        ))}
        {isLoading && <Text style={styles.thinking}>Thinking…</Text>}
      </ScrollView>

      {/* Input field */}
      <TextInput
        style={styles.input}
        placeholder="Ask about your orders..."
        value={question}
        onChangeText={setQuestion}
        editable={!isLoading}
      />

      {/* Send button */}
      <Button title="Send" onPress={handleSend} disabled={isLoading} />
    </View>
  );
};

/**
 * Styles for chat layout, message bubbles, and input controls.
 */
const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  chat: {
    flex: 1,
    marginBottom: 10,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 10,
    marginBottom: 10,
  },
  user: {
    alignSelf: 'flex-end',
    backgroundColor: '#e0f7fa',
    padding: 8,
    marginVertical: 4,
    borderRadius: 6,
    maxWidth: '80%',
  },
  bot: {
    alignSelf: 'flex-start',
    backgroundColor: '#f1f8e9',
    padding: 8,
    marginVertical: 4,
    borderRadius: 6,
    maxWidth: '80%',
  },
  thinking: {
    alignSelf: 'flex-start',
    fontStyle: 'italic',
    color: '#888',
    marginVertical: 4,
    padding: 8,
  },
});

export default ChatScreen;
