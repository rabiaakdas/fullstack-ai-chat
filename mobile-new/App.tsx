
import React, { useState, useRef, useEffect } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  StatusBar,
} from 'react-native';


import { Message, RegisterResponse } from './types';



const API_BASE_URL = 'http://192.168.1.12:5050';


const App = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [username, setUsername] = useState('');
  const [userId, setUserId] = useState<number | null>(null);
  const [isRegistered, setIsRegistered] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const flatListRef = useRef<FlatList>(null);

  // Sayfa açıldığında mesajları çek
  useEffect(() => {
    fetchMessages();
    
  
    const interval = setInterval(fetchMessages, 3000);
    return () => clearInterval(interval);
  }, []);

  // Mesajları backend'den çek
  const fetchMessages = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/messages`);
      
      if (response.ok) {
        const data: Message[] = await response.json();
        setMessages(data);
      }
    } catch (error) {
      console.log('❌ Mesaj çekme hatası:', error);
    }
  };

  // Kullanıcı kaydı
  const registerUser = async () => {
    if (!username.trim() || username.length < 2) {
      Alert.alert('Hata', 'Lütfen en az 2 karakterlik bir rumuz girin');
      return;
    }

    try {
      setIsLoading(true);

      const response = await fetch(`${API_BASE_URL}/api/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username.trim()
        }),
      });

      if (response.ok) {
        const result: RegisterResponse = await response.json();
        
        setUserId(result.userId);
        setIsRegistered(true);
        
        Alert.alert('Başarılı', `Hoş geldin ${result.username}!`);
        
        
        fetchMessages();
      } else {
        const errorData = await response.json();
        Alert.alert('Hata', errorData.error || 'Kayıt başarısız');
      }
    } catch (error) {
      Alert.alert('Bağlantı Hatası', 'Backend servisine ulaşılamıyor. Localhost:5050 çalışıyor mu?');
    } finally {
      setIsLoading(false);
    }
  };

  // Mesaj gönder 
  const sendMessage = async () => {
    if (!inputText.trim() || !userId) {
      Alert.alert('Hata', 'Lütfen mesaj yazın ve giriş yapın');
      return;
    }

    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: userId,
          text: inputText.trim(),
        }),
      });

      if (response.ok) {
        
        await fetchMessages();
      } else {
        const errorData = await response.json();
        Alert.alert('Hata', errorData.error || 'Mesaj gönderilemedi');
      }
    } catch (error) {
      Alert.alert('Hata', 'Mesaj gönderilemedi. Bağlantıyı kontrol edin.');
    } finally {
      setIsLoading(false);
    }
  };

  // Duygu renkleri
  const getSentimentColor = (sentiment: string) => {
    switch(sentiment.toLowerCase()) {
      case 'positive': return '#10B981';
      case 'negative': return '#EF4444';
      case 'neutral': return '#6B7280';
      default: return '#9CA3AF';
    }
  };

  // Duygu emojisi
  const getSentimentEmoji = (sentiment: string) => {
    switch(sentiment.toLowerCase()) {
      case 'positive': return '😊';
      case 'negative': return '😔';
      case 'neutral': return '😐';
      default: return '🤔';
    }
  };

  // Mesaj bileşeni
  const renderMessage = ({ item }: { item: Message }) => (
    <View style={[
      styles.messageContainer,
      item.username === username ? styles.userMessage : styles.otherMessage
    ]}>
      <View style={styles.messageHeader}>
        <Text style={styles.username}>@{item.username}</Text>
        <View style={[
          styles.sentimentBadge,
          { backgroundColor: getSentimentColor(item.sentiment) }
        ]}>
          <Text style={styles.sentimentText}>
            {getSentimentEmoji(item.sentiment)} {item.sentiment} ({(item.sentimentScore * 100).toFixed(0)}%)
          </Text>
        </View>
      </View>
      <Text style={[
        styles.messageText,
        item.username === username && styles.userMessageText
      ]}>
        {item.text}
      </Text>
      <Text style={styles.timestamp}>
        {new Date(item.createdAt).toLocaleTimeString('tr-TR', {
          hour: '2-digit',
          minute: '2-digit'
        })}
      </Text>
    </View>
  );

  // Çıkış yap
  const logout = () => {
    setUserId(null);
    setUsername('');
    setIsRegistered(false);
    setMessages([]);
  };

  // KAYIT EKRANI
  if (!isRegistered) {
    return (
      <View style={styles.container}>
        <StatusBar barStyle="dark-content" />
        <View style={styles.registerContainer}>
          <Text style={styles.title}>🇹🇷 AI Duygu Analizi Sohbet</Text>
          <Text style={styles.subtitle}>Sohbete başlamak için rumuzunuzu girin</Text>
          
          <TextInput
            style={styles.usernameInput}
            placeholder="Rumuzunuz (en az 2 karakter)"
            value={username}
            onChangeText={setUsername}
            maxLength={20}
            autoCapitalize="none"
            autoCorrect={false}
          />
          
          <TouchableOpacity
            style={[
              styles.registerButton,
              (isLoading || username.length < 2) && styles.buttonDisabled
            ]}
            onPress={registerUser}
            disabled={isLoading || username.length < 2}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.registerButtonText}>Sohbete Başla 🚀</Text>
            )}
          </TouchableOpacity>

          <View style={styles.infoBox}>
            <Text style={styles.infoText}>
              📍 Backend: {API_BASE_URL}
            </Text>
            <Text style={styles.infoText}>
              🤖 AI: Backend üzerinden entegre
            </Text>
          </View>
        </View>
      </View>
    );
  }

  // SOHBET EKRANI
  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <StatusBar barStyle="light-content" />
      
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>AI Duygu Analizi</Text>
          <Text style={styles.headerSubtitle}>Kullanıcı: @{username}</Text>
        </View>
        <TouchableOpacity style={styles.logoutButton} onPress={logout}>
          <Text style={styles.logoutButtonText}>Çıkış</Text>
        </TouchableOpacity>
      </View>

      {/* Mesaj Listesi */}
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id.toString()}
        style={styles.messagesList}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>Henüz mesaj yok 😴</Text>
            <Text style={styles.emptySubtext}>İlk mesajı sen gönder! 🎉</Text>
          </View>
        }
      />

      {/* Mesaj Girişi */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Mesajınızı yazın..."
          placeholderTextColor="#999"
          multiline
          maxLength={500}
          editable={!isLoading}
        />
        <TouchableOpacity
          style={[
            styles.sendButton,
            (!inputText.trim() || isLoading) && styles.buttonDisabled
          ]}
          onPress={sendMessage}
          disabled={!inputText.trim() || isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.sendButtonText}>Gönder</Text>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

// STYLES
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  registerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#1f2937',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 32,
    textAlign: 'center',
    lineHeight: 22,
  },
  usernameInput: {
    width: '100%',
    height: 56,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    marginBottom: 20,
    backgroundColor: '#ffffff',
    color: '#1f2937',
  },
  registerButton: {
    width: '100%',
    height: 56,
    backgroundColor: '#007AFF',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#007AFF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  registerButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  buttonDisabled: {
    backgroundColor: '#9ca3af',
    shadowOpacity: 0,
  },
  infoBox: {
    marginTop: 32,
    padding: 16,
    backgroundColor: '#f3f4f6',
    borderRadius: 8,
    width: '100%',
  },
  infoText: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 4,
  },
  header: {
    backgroundColor: '#007AFF',
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#dbeafe',
    marginTop: 2,
  },
  logoutButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 8,
  },
  logoutButtonText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  messagesList: {
    flex: 1,
    padding: 12,
  },
  messageContainer: {
    maxWidth: '85%',
    padding: 16,
    borderRadius: 16,
    marginVertical: 6,
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#007AFF',
  },
  otherMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  messageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  username: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6b7280',
  },
  sentimentBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  sentimentText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  messageText: {
    fontSize: 16,
    color: '#1f2937',
    lineHeight: 20,
  },
  userMessageText: {
    color: '#ffffff',
  },
  timestamp: {
    fontSize: 10,
    color: '#9ca3af',
    marginTop: 8,
    alignSelf: 'flex-end',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 48,
  },
  emptyText: {
    fontSize: 18,
    color: '#6b7280',
    marginBottom: 8,
    textAlign: 'center',
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9ca3af',
    textAlign: 'center',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    alignItems: 'flex-end',
  },
  textInput: {
    flex: 1,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    maxHeight: 100,
    backgroundColor: '#f9fafb',
    marginRight: 12,
    fontSize: 16,
    color: '#1f2937',
  },
  sendButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 20,
    minWidth: 60,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 14,
  },
});

export default App;