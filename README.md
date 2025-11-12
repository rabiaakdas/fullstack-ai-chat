# Proje Hakkında

Kullanıcıların mesajlaşabildiği, yazışmaların AI tarafından duygu analizi yapılarak canlı olarak gösterildiği full-stack web ve mobil uygulama.

## Proje Dizin Yapısı
fullstack-ai-chat/


  frontend/              # React web uygulaması
    public/             # Static dosyalar
    src/                # React source kodları
      App.js            # Ana uygulama componenti
      App.css           # Stil dosyası
      services/         # API servisleri
    package.json        # Bağımlılıklar
    build/              # Production build

    
  mobile-new/           # React Native mobil uygulaması
    app.json            # React Native konfigürasyonu
    App.tsx             # Ana mobil uygulama componenti
    package.json        # Bağımlılıklar

    
  backend/              # .NET Core API
    ChatAPI/
      Program.cs        # Ana uygulama giriş noktası
      ChatAPI.csproj    # .NET proje dosyası

      
  ai-service/           # Python AI servisi
    app.py              # Gradio arayüzü ve AI entegrasyonu
    requirements.txt    # Python bağımlılıkları


# Kurulum Adımları

Backend (.NET Core)
bash
cd backend/ChatAPI
dotnet restore
dotnet run

Frontend Web (React)
bash
cd frontend
npm install
npm start

Frontend Mobile (React Native)
bash
cd mobile-new
npm install
npx react-native run-android

AI Servis (Python)
bash
cd ai-service
pip install -r requirements.txt
python app.py


# Kullanılan AI Araçları

Hugging Face Transformers
Kütüphane: transformers
Model: nlptown/bert-base-multilingual-uncased-sentiment
Kullanım: Duygu analizi pipeline'ı

Gradio
Kütüphane: gradio
Kullanım: Web arayüzü ve API endpoint


# Çalışır Demo Linkleri
Web Chat: https://fullstack-ai-chat-two.vercel.app/

AI Endpoint: https://rabianrrr-turkish-emotion-analysis.hf.space

Render API: https://fullstack-ai-chat-11.onrender.com

## Dosya İşlevleri

### Backend / Program.cs
- .NET Core tabanlı backend uygulamasının ana giriş noktasıdır.  
- Uygulama başlatılırken:
  - SQLite veritabanı bağlanır ve tablolar oluşturulur.  
  - `HttpClient` üzerinden AI servisi için bağlantı ayarlanır.  
  - CORS politikası (`AllowAll`) tüm frontend ve mobil isteklerini kabul edecek şekilde yapılandırılır.  
- Middleware pipeline kurulumu yapılır (`UseCors`, `UseAuthorization`).  
- Endpointler burada tanımlanır:
  - `/api/register` → Yeni kullanıcı kaydı ve mevcut kullanıcı kontrolü.  
  - `/api/messages` → Mesaj gönderme, AI ile duygu analizi ve veritabanına kaydetme.  
  - `/api/messages` (GET) → Mesajları listeleme.  
  - `/api/users` → Kullanıcı listesini ve mesaj sayısını döndürme.  
  - `/api/test-ai` → AI servisini test etmek için endpoint.  
  - `/api/ai-health` → AI servis bağlantı durumu ve sağlık kontrolü.  
  - `/api/debug` → Gelen raw request verilerini görmek için debug endpoint.  
  - `/api/test` ve `/` → Basit test ve root endpoint’leri.  

- Ayrıca, burada **veritabanı modelleri ve AI servisi sınıfı** tanımlanmıştır:
  - `User` → Kullanıcı bilgileri, ID, kullanıcı adı, oluşturulma zamanı ve mesaj listesi.  
  - `Message` → Mesaj metni, duygu analizi sonucu, kullanıcı bilgisi ve oluşturulma zamanı.  
  - `ChatContext` → Entity Framework DbContext, tabloların ve ilişkilerin tanımı.  
  - `AIService` → AI servisine HTTP istekleri gönderir ve mesaj metinlerinin duygu analizini döndürür.  

### Frontend / App.js
- React web uygulamasının ana componenti.  
- Kullanıcı arayüzünü render eder: mesajlaşma ekranı, kullanıcı listesi ve duygu analizi görselleştirmeleri.  
- Backend API ile iletişimi yönetir (mesaj gönderme, alma ve AI analiz sonuçlarını çekme).  
- State yönetimi ve component lifecycle işlemleri burada kontrol edilir.  

### Mobile-new / App.tsx
- React Native mobil uygulamanın ana componentidir.  
- Android ve iOS platformlarında mesajlaşma ve duygu analizi arayüzünü yönetir.  
- Kullanıcı girişleri, mesaj gönderme/alma ve canlı duygu analizi gösterimi buradan kontrol edilir.  
- Mobil deneyime özel UI ve performans optimizasyonları içerir.  

### Mobile-new / app.json
- React Native uygulamasının konfigürasyon dosyasıdır.  
- Uygulama adı, sürümü, ikon ve splash screen gibi temel mobil ayarlar burada tanımlanır.  
- Android ve iOS platformlarına özgü yapılandırmalar yapılır.  

### AI-Service / app.py
- Python tabanlı AI servisinin giriş noktasıdır.  
- Gradio kütüphanesi ile web arayüzü ve API endpoint oluşturur.  
- Mesajlar bu servis üzerinden alınır ve `transformers` modeli ile duygu analizi yapılır.  
- Analiz sonuçları JSON formatında frontend ve mobil uygulamaya iletilir.  
- Modelin ön işleme, tahmin ve sonuç döndürme süreçleri burada yönetilir.  



# Proje Hakkında
Projenin geliştirme sürecinde DeepSeek AI aracı, özellikle backend mimarisinin oluşturulması ve duygu analizi modelinin yapılandırılması aşamalarında yardımcı araç olarak kullanılmıştır.
API yapısının bazı bölümlerinde ve model optimizasyonunda AI’den yönlendirme alınmış, ancak kodun önemli bir kısmı kendi teknik katkım ve manuel düzenlemelerimle geliştirilmiştir.
Bu sayede proje, hem yapay zekâ desteğiyle hız kazanmış hem de geliştirici olarak benim teknik kontrolüm altında şekillenmiştir.

