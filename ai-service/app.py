import os
import json
from flask import Flask, request, jsonify
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Hugging Face Spaces ortam değişkenleri
HF_SPACE = os.environ.get('HF_SPACE', False)
SPACE_NAME = os.environ.get('SPACE_NAME', 'turkish-sentiment-analysis')

print("🤖 Türkçe Duygu Analizi Modeli Yükleniyor...")
print(f"📍 Ortam: {'Hugging Face Space' if HF_SPACE else 'Local'}")


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

@app.route('/analyze', methods=['POST', 'GET'])
def analyze_endpoint():
    """
    Ana duygu analizi endpoint'i - Özel ifade desteği ile
    """
    try:
        if request.method == 'GET':
            return jsonify({
                "message": "🇹🇷 Türkçe Duygu Analizi API v4.0",
                "version": "4.0.0",
                "description": "Özel ifade desteği ile gelişmiş duygu analizi",
                "usage": "POST isteği ile {'text': 'analiz edilecek metin'} gönderin",
                "special_features": [
                    "'fena değil' → pozitif",
                    "'normalim' → nötr", 
                    "Net duygu önceliği"
                ]
            })
        
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        if not data:
            return jsonify({"error": "JSON verisi gerekli"}), 400
        
        text = data.get('text', '') or data.get('input', '') or data.get('message', '')
        
        if not text:
            return jsonify({"error": "Analiz için metin gerekli"}), 400
        
        print(f"📥 İstek alındı: '{text}'")
        
        result = analyze_sentiment(text)
        
        if "error" in result:
            return jsonify(result), 500
            
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Sunucu hatası: {e}")
        return jsonify({"error": f"Sunucu hatası: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Servis durum kontrolü
    """
    return jsonify({
        "status": "healthy",
        "service": "Turkish Sentiment Analysis API v4.0",
        "model_loaded": sentiment_pipeline is not None,
        "version": "4.0.0",
        "language": "turkish",
        "special_features": [
            "'fena değil' → pozitif tespiti",
            "'normalim' → nötr tespiti",
            "Net duygu ifade önceliği"
        ]
    })

@app.route('/test-special', methods=['GET'])
def test_special_cases():
    """
    Özel durumları test et
    """
    test_cases = [
        {"text": "fena değil", "expected": "positive", "description": "Olumsuz kelime içeren pozitif ifade"},
        {"text": "normalim", "expected": "neutral", "description": "Net nötr ifade"},
        {"text": "çok mutluyum", "expected": "positive", "description": "Net pozitif ifade"},
        {"text": "üzgünüm", "expected": "negative", "description": "Net negatif ifade"},
        {"text": "idare eder", "expected": "neutral", "description": "Nötr ifade"},
        {"text": "kötü değil", "expected": "positive", "description": "Olumsuz kelime içeren pozitif"}
    ]
    
    results = []
    correct_count = 0
    
    for test in test_cases:
        print(f"\n🧪 Test: '{test['text']}'")
        result = analyze_sentiment(test["text"])
        
        actual = result.get("sentiment")
        expected = test["expected"]
        is_correct = actual == expected
        
        if is_correct:
            correct_count += 1
            status = "✅"
        else:
            status = "❌"
        
        results.append({
            "text": test["text"],
            "expected": expected,
            "actual": actual,
            "score": result.get("score"),
            "confidence": result.get("confidence"),
            "reason": result.get("analysis", {}).get("decision_reason"),
            "description": test["description"],
            "status": status,
            "is_correct": is_correct
        })
    
    accuracy = round((correct_count / len(test_cases)) * 100, 1)
    
    return jsonify({
        "test_type": "special_cases_accuracy",
        "total_tests": len(test_cases),
        "correct_predictions": correct_count,
        "accuracy": f"%{accuracy}",
        "results": results
    })

@app.route('/batch', methods=['POST'])
def batch_analyze():
    """
    Toplu metin analizi
    """
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({"error": "'texts' listesi gerekli"}), 400
        
        texts = data['texts']
        
        if not isinstance(texts, list) or len(texts) > 10:
            return jsonify({"error": "Maksimum 10 metin gönderilebilir"}), 400
        
        results = []
        for text in texts:
            if isinstance(text, str) and text.strip():
                result = analyze_sentiment(text)
                results.append(result)
            else:
                results.append({"error": "Geçersiz metin"})
        
        return jsonify({
            "count": len(results),
            "results": results
        })
        
    except Exception as e:
        return jsonify({"error": f"Toplu analiz hatası: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def home():
    """
    Ana sayfa
    """
    return jsonify({
        "message": "🇹🇷 Türkçe Duygu Analizi API v4.0",
        "version": "4.0.0",
        "description": "Özel ifade desteği ile gelişmiş duygu analizi",
        "key_improvements": [
            "✅ 'fena değil' → pozitif olarak tanınır",
            "✅ 'normalim' → nötr olarak tanınır", 
            "✅ Net duygu ifadelerine öncelik verilir",
            "✅ Olumsuz kelime içeren pozitif ifadeler desteklenir"
        ],
        "endpoints": {
            "POST /analyze": "Tekil metin analizi",
            "POST /batch": "Toplu analiz (max 10)",
            "GET /health": "Servis durumu",
            "GET /test-special": "Özel durum testi",
            "GET /": "Bu sayfa"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 7860))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"\n🚀 Türkçe Duygu Analizi API v4.0 Başlatılıyor...")
    print(f"📍 Port: {port}")
    print(f"🎯 ÖZEL ÖZELLİKLER:")
    print(f"   ✓ 'fena değil' → POZİTİF")
    print(f"   ✓ 'normalim' → NÖTR") 
    print(f"   ✓ Net duygu ifadelerine öncelik")
    print(f"📚 Endpoints:")
    print(f"   POST /analyze       - Duygu analizi")
    print(f"   GET  /test-special  - Özel durum testi")
    print(f"   GET  /health        - Servis durumu")
    
    app.run(host="0.0.0.0", port=port, debug=debug)