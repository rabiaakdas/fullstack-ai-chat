import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [username, setUsername] = useState('');
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isRegistered, setIsRegistered] = useState(false);
  const messagesEndRef = useRef(null);

  const BACKEND_URL = 'http://localhost:5050';

  // LocalStorage'dan kullanıcı bilgilerini yükle
  useEffect(() => {
    const savedUserId = localStorage.getItem('userId');
    const savedUsername = localStorage.getItem('username');
    
    if (savedUserId && savedUsername) {
      setUserId(parseInt(savedUserId));
      setUsername(savedUsername);
      setIsRegistered(true);
      console.log('✅ Oturum yeniden yüklendi:', { userId: savedUserId, username: savedUsername });
    }
    
    fetchMessages();
    const interval = setInterval(fetchMessages, 3000);
    return () => clearInterval(interval);
  }, []);

  // Backend'den mesajları çek
  const fetchMessages = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/messages`);
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (error) {
      console.log('❌ Mesajlar alınamadı:', error);
    }
  };

  // Kullanıcı kaydı
  const registerUser = async () => {
    if (!username.trim()) {
      alert('Lütfen kullanıcı adı girin!');
      return;
    }

    setLoading(true);
    try {
      console.log('🔄 Kullanıcı kaydı yapılıyor...', username);

   
      const requestData = {
        username: username.trim()
      };

      console.log('📤 Gönderilen JSON:', JSON.stringify(requestData));

      const response = await fetch(`${BACKEND_URL}/api/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      console.log('📨 Register response:', response.status);
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Kullanıcı kaydı başarılı:', result);
        
        setUserId(result.userId);
        setIsRegistered(true);
        
        // LocalStorage'a kaydet
        localStorage.setItem('userId', result.userId);
        localStorage.setItem('username', username);
        
        alert(`Hoş geldin ${result.username}!`);
      } else {
        const errorData = await response.json();
        console.log('❌ Register hatası:', errorData);
        alert(`Kayıt hatası: ${errorData.error || response.status}`);
      }
    } catch (error) {
      console.log('❌ Register bağlantı hatası:', error);
      alert('Backend bağlantı hatası! Backend çalışıyor mu?');
    } finally {
      setLoading(false);
    }
  };

  // Mesaj gönder
  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim()) {
      alert('Lütfen mesaj girin!');
      return;
    }

    if (!userId) {
      alert('Lütfen önce kullanıcı girişi yapın!');
      return;
    }

    setLoading(true);
    try {
      console.log('🔄 Mesaj gönderiliyor...', {
        userId: userId,
        text: newMessage
      });

      const requestData = {
        userId: userId,
        text: newMessage.trim()
      };

      const response = await fetch(`${BACKEND_URL}/api/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      console.log('📨 Mesaj response:', response.status);
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Mesaj gönderildi:', result);
        setNewMessage('');
        fetchMessages();
      } else {
        const errorData = await response.json();
        console.log('❌ Mesaj gönderme hatası:', errorData);
        alert(`Mesaj gönderilemedi: ${errorData.error || response.status}`);
      }
    } catch (error) {
      console.log('❌ Mesaj bağlantı hatası:', error);
      alert('Backend bağlantı hatası!');
    } finally {
      setLoading(false);
    }
  };

  // Çıkış yap
  const logout = () => {
    setUserId(null);
    setUsername('');
    setIsRegistered(false);
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    setNewMessage('');
  };

  // Otomatik scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Duygu renkleri
  const getSentimentColor = (sentiment) => {
    switch(sentiment) {
      case 'positive': return '#10B981';
      case 'negative': return '#EF4444';
      case 'neutral': return '#6B7280';
      default: return '#9CA3AF';
    }
  };

  return (
    <div className="App">
      <div className="chat-container">
        <div className="chat-header">
          <h1>🤖 AI Destekli Chat</h1>
          {isRegistered && (
            <div className="user-info">
              <span>@{username}</span>
              <button onClick={logout} className="logout-btn">Çıkış</button>
            </div>
          )}
        </div>
        
        {/* KULLANICI GİRİŞ EKRANI */}
        {!isRegistered ? (
          <div className="register-container">
            <div className="register-form">
              <h2>Chat'e Hoş Geldiniz! 👋</h2>
              <p>Başlamak için bir kullanıcı adı seçin:</p>
              
              <div className="input-group">
                <input
                  type="text"
                  placeholder="Kullanıcı adınız (en az 2 karakter)"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && registerUser()}
                  className="register-input"
                />
                <button 
                  onClick={registerUser}
                  disabled={loading || username.length < 2}
                  className="register-button"
                >
                  {loading ? 'Kaydediliyor...' : 'Giriş Yap'}
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* CHAT EKRANI */
          <>
            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="no-messages">
                  <p>Henüz mesaj yok 😴</p>
                  <p>İlk mesajı sen gönder! 🚀</p>
                </div>
              ) : (
                messages.map((msg) => (
                  <div key={msg.id} className="message">
                    <div className="message-header">
                      <strong>@{msg.username}</strong>
                      <span 
                        className="sentiment-badge"
                        style={{backgroundColor: getSentimentColor(msg.sentiment)}}
                      >
                        {msg.sentiment} ({(msg.sentimentScore * 100).toFixed(0)}%)
                      </span>
                    </div>
                    <div className="message-text">{msg.text}</div>
                    <div className="message-time">
                      {new Date(msg.createdAt).toLocaleTimeString('tr-TR')}
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* MESAJ GÖNDERME FORMÜ */}
            <form onSubmit={sendMessage} className="message-form">
              <div className="message-input-container">
                <input
                  type="text"
                  placeholder="Mesajınızı yazın..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  className="message-input"
                  disabled={loading}
                />
                <button 
                  type="submit" 
                  className="send-button"
                  disabled={loading || !newMessage.trim()}
                >
                  {loading ? '⏳' : '📤'}
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
}

export default App;