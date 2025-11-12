import os
import json
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch
import gradio as gr

print("🤖 Türkçe Duygu Analizi Modeli Yükleniyor...")

sentiment_pipeline = None

try:
    # Türkçe duygu analizi modeli
    model_name = "savasy/bert-base-turkish-sentiment-cased"
    
    # Model ve tokenizer'ı yükle
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    # Pipeline oluştur
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model=model,
        tokenizer=tokenizer,
        device=0 if torch.cuda.is_available() else -1
    )
    
    print("✅ Türkçe AI modeli başarıyla yüklendi!")
    if torch.cuda.is_available():
        print("🎯 GPU kullanılıyor")
    else:
        print("⚡ CPU kullanılıyor")
        
except Exception as e:
    print(f"❌ Model yükleme hatası: {e}")
    sentiment_pipeline = None

def analyze_sentiment(text):
    """
    Geliştirilmiş Türkçe duygu analizi - İfade tamamlama desteği ile
    """
    try:
        if sentiment_pipeline is None:
            return {"error": "Model yüklenemedi"}
        
        cleaned_text = text.strip()[:500]
        
        if not cleaned_text:
            return {"error": "Geçersiz metin"}
        
        #Önce model analizi
        result = sentiment_pipeline(cleaned_text)[0]
        print(f"🔍 Model Analiz: '{cleaned_text}' -> {result}")
        
        label = result['label']
        original_score = result['score']
        
        text_lower = cleaned_text.lower()
        
        #NET DUYGU İFADELERİ
        strong_positive_phrases = [
            'çok mutluyum', 'mutluyum', 'mutluluk', 'neşeliyim', 'sevinçliyim',
            'harika', 'mükemmel', 'süper', 'müthiş', 'muhteşem', 'fevkalade',
            'seni seviyorum', 'aşığım', 'bayıldım', 'hoşlandım', 'beğendim',
            'heyecanlıyım', 'coşkuluyum', 'enerjik', 'keyifli', 'neşeli',
            'çok iyi', 'harika bir', 'mükemmel bir'
        ]
        
        strong_negative_phrases = [
            'üzgünüm', 'mutsuzum', 'kederliyim', 'hüzünlüyüm',
            'kötüyüm', 'kötü hissediyorum', 'rahatsızım', 'hasta',
            'nefret ediyorum', 'tiksinme', 'iğrenme', 'hoşlanmıyorum',
            'korkuyorum', 'endişeliyim', 'kaygılıyım', 'panik',
            'sinirliyim', 'kızgınım', 'öfkeliyim', 'hırslı',
            'bıktım', 'sıkıldım', 'yoruldum', 'bitkinim', 'tükenmiş',
            'çok kötü', 'berbat', 'korkunç'
        ]
        
        # OLUMSUZLUK EKLERİ İÇEREN İFADELER - BUNLARI POZİTİF YAP
        negative_word_positive_phrases = [
            'fena değil', 'kötü değil', 'berbat değil', 'korkunç değil'
        ]
        
        # Net duygu kontrolü - TAM EŞLEŞME
        has_strong_positive = any(phrase in text_lower for phrase in strong_positive_phrases)
        has_strong_negative = any(phrase in text_lower for phrase in strong_negative_phrases)
        has_negative_word_positive = any(phrase in text_lower for phrase in negative_word_positive_phrases)
        
        #NÖTR BELİRTEÇLERİ
        neutral_phrases = [
            'normal', 'normalim', 'normal bir', 'ortalama', 'standart', 
            'sıradan', 'olağan', 'düz', 'vasat', 'idare eder', 
            'eh işte', 'şöyle böyle', 'yeterli', 'yetişir', 
            'kabul edilebilir', 'makul', 'ortalama bir'
        ]
        
        # Çok kısa/etkisiz mesajlar
        short_neutral_phrases = ['ok', 'tamam', 'anladım', 'olur', 'peki', 'sağol', 'merhaba', 'selam']
        
        has_neutral_phrases = any(phrase in text_lower for phrase in neutral_phrases)
        is_short_neutral = any(phrase == text_lower.strip() for phrase in short_neutral_phrases)
        is_very_short = len(cleaned_text.split()) <= 2
        is_low_confidence = original_score < 0.7
        
        # KARAR VERME MANTIĞI 
        if has_negative_word_positive:
            sentiment = "positive"
            turkish_label = "pozitif"
            adjusted_score = 0.75  
            reason = "negative_word_positive_phrase"
            
        elif has_strong_positive:
            # NET POZİTİF
            sentiment = "positive"
            turkish_label = "pozitif"
            adjusted_score = max(original_score, 0.85)
            reason = "strong_positive_phrase"
            
        elif has_strong_negative:
            # NET NEGATİF
            sentiment = "negative"
            turkish_label = "negatif"
            adjusted_score = max(original_score, 0.85)
            reason = "strong_negative_phrase"
            
        elif has_neutral_phrases:
            # NÖTR İFADELER
            sentiment = "neutral"
            turkish_label = "nötr"
            adjusted_score = 0.5 + (original_score - 0.5) * 0.2  # 0.4-0.6
            reason = "neutral_phrase"
            
        elif is_low_confidence and (is_short_neutral or is_very_short):
            # KISA MESAJ + DÜŞÜK KESİNLİK
            sentiment = "neutral"
            turkish_label = "nötr"
            adjusted_score = 0.5
            reason = "short_text_low_confidence"
            
        elif 'positive' in label.lower() or 'pozitif' in label.lower():
            # MODEL POZİTİF
            sentiment = "positive"
            turkish_label = "pozitif"
            adjusted_score = original_score
            reason = "model_positive"
            
        elif 'negative' in label.lower() or 'negatif' in label.lower():
            # MODEL NEGATİF
            sentiment = "negative"
            turkish_label = "negatif"
            adjusted_score = original_score
            reason = "model_negative"
            
        else:
            # DİĞER
            sentiment = "neutral"
            turkish_label = "nötr"
            adjusted_score = 0.5
            reason = "fallback_neutral"
        
        #Skor sınırlamaları
        adjusted_score = max(0.1, min(0.99, adjusted_score))
        
        # Zengin response
        emoji_map = {
            "positive": "😊",
            "negative": "😔", 
            "neutral": "😐"
        }
        
        color_map = {
            "positive": "#10B981",
            "negative": "#EF4444",
            "neutral": "#6B7280"
        }
        
        response_data = {
            "text": cleaned_text,
            "sentiment": sentiment,
            "turkish_label": turkish_label,
            "score": round(adjusted_score, 4),
            "original_score": round(original_score, 4),
            "confidence": f"%{round(adjusted_score * 100, 1)}",
            "emoji": emoji_map.get(sentiment, "😐"),
            "color": color_map.get(sentiment, "#6B7280"),
            "model": "bert-base-turkish-sentiment-cased",
            "language": "turkish",
            "analysis": {
                "decision_reason": reason,
                "has_strong_emotion": has_strong_positive or has_strong_negative,
                "has_special_phrase": has_negative_word_positive,
                "word_count": len(cleaned_text.split())
            }
        }
        
        print(f"✅ Final: {sentiment} (%{round(adjusted_score * 100, 1)}) - Sebep: {reason}")
        
        return response_data
        
    except Exception as e:
        print(f"❌ Analiz hatası: {e}")
        return {"error": f"Analiz başarısız: {str(e)}"}

# Gradio arayüzü için ana fonksiyon
def gradio_analyze(text):
    """Gradio için ana analiz fonksiyonu"""
    result = analyze_sentiment(text)
    return result

# Gradio arayüzünü oluştur
demo = gr.Interface(
    fn=gradio_analyze,
    inputs=gr.Textbox(
        label="📝 Metni Girin", 
        placeholder="Duygu analizi yapılacak Türkçe metni yazın...",
        lines=3
    ),
    outputs=gr.JSON(label="🎯 Analiz Sonucu"),
    title="🤖 Türkçe Duygu Analizi - AI Chat Projesi",
    description=""" 
    🇹🇷 **Türkçe metinlerin duygu durumunu analiz eder**
    
    🎯 **Özel Özellikler:**
    • 'fena değil' → **Pozitif** olarak tanınır
    • 'normalim' → **Nötr** olarak tanınır  
    • Net duygu ifadelerine öncelik verilir
    
    🔍 **Örnekler:** 'Çok mutluyum!', 'Fena değil', 'Üzgünüm'
    """,
    examples=[
        ["Bugün çok mutluyum, harika bir gün!"],
        ["Fena değil, idare eder"],
        ["Üzgünüm bugün her şey ters gidiyor"],
        ["Normal bir gün, sıradan"],
        ["Bu proje mükemmel olmuş!"],
        ["Kötü değil aslında"]
    ]
)

# API endpoint simülasyonu (opsiyonel)
def api_simulate(text):
    """API benzeri response için"""
    result = analyze_sentiment(text)
    return result

# Uygulamayı başlat
if __name__ == "__main__":
    print(f"\n🚀 Türkçe Duygu Analizi Gradio UI Başlatılıyor...")
    print(f"🎯 ÖZEL ÖZELLİKLER:")
    print(f"   ✓ 'fena değil' → POZİTİF")
    print(f"   ✓ 'normalim' → NÖTR") 
    print(f"   ✓ Net duygu ifadelerine öncelik")
    
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)
