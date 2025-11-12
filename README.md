# fullstack-ai-chat

Proje Hakkında
Kullanıcıların mesajlaşabildiği, yazışmaların AI tarafından duygu analizi yapılarak canlı olarak gösterildiği full-stack web ve mobil uygulama.

fullstack-ai-chat/
├── frontend/              # React web uygulaması
│   ├── public/           # Static dosyalar
│   ├── src/              # React source kodları
│   │   ├── App.js        # Ana uygulama componenti
│   │   ├── App.css       # Stil dosyası
│   │   └── services/     # API servisleri
│   ├── package.json      # Bağımlılıklar
│   └── build/            # Production build
├── mobile-new/           # React Native mobil uygulaması
│   ├── app.json          # React Native konfigürasyonu
│   ├── App.tsx           # Ana mobil uygulama componenti
│   └── package.json      # Bağımlılıklar
├── backend/              # .NET Core API
│   └── ChatAPI/
│       ├── Program.cs    # Ana uygulama giriş noktası
│       └── ChatAPI.csproj # .NET proje dosyası
└── ai-service/           # Python AI servisi
    ├── app.py           # Gradio arayüzü ve AI entegrasyonu
    └── requirements.txt  # Python bağımlılıkları


Kurulum Adımları

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


Kullanılan AI Araçları

Hugging Face Transformers
Kütüphane: transformers
Model: nlptown/bert-base-multilingual-uncased-sentiment
Kullanım: Duygu analizi pipeline'ı

Gradio
Kütüphane: gradio
Kullanım: Web arayüzü ve API endpoint


Çalışır Demo Linkleri
Web Chat: https://fullstack-ai-chat-mauve.vercel.app/

Mobile APK: [GitHub Releases'tan indirilebilir]

AI Endpoint: https://rabianrrr-turkish-emotion-analysis.hf.space

Render API: https://fullstack-ai-chat-11.onrender.com


Dosya İşlevleri
Backend/Program.cs - Tüm backend kodları (API endpoint'leri, modeller, database context, AI servis)

Frontend/App.js - React web uygulaması ana component

Mobile-new/App.tsx - React Native mobil uygulama ana component
Mobile-new/app.json - Mobil uygulama konfigürasyonu

AI-Service/app.py - Python AI servisi ve Gradio arayüzü


Proje Hakkında
Projenin geliştirme sürecinde DeepSeek AI aracı, özellikle backend mimarisinin oluşturulması ve duygu analizi modelinin yapılandırılması aşamalarında yardımcı araç olarak kullanılmıştır.
API yapısının bazı bölümlerinde ve model optimizasyonunda AI’den yönlendirme alınmış, ancak kodun önemli bir kısmı kendi teknik katkım ve manuel düzenlemelerimle geliştirilmiştir.
Bu sayede proje, hem yapay zekâ desteğiyle hız kazanmış hem de geliştirici olarak benim teknik kontrolüm altında şekillenmiştir.
