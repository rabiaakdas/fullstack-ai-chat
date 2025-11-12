using System.Text;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);

// SQLite veritabanı 
builder.Services.AddDbContext<ChatContext>(options =>
    options.UseSqlite("Data Source=chat.db"));

// HttpClient Factory - AI servisi için
builder.Services.AddHttpClient<AIService>(client => 
{
    client.BaseAddress = new Uri("https://rabianrrr-turkish-emotion-analysis.hf.space");
    client.Timeout = TimeSpan.FromSeconds(30);
});

// CORS yapılandırması
builder.Services.AddCors(options => 
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader()
              .WithExposedHeaders("*")
              .SetPreflightMaxAge(TimeSpan.FromHours(1));
    });
});

builder.Services.AddControllers();

var app = builder.Build();

// Middleware pipeline
app.UseCors("AllowAll");
app.UseAuthorization();

//VERİTABANI 
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<ChatContext>();
    
    try 
    {
        Console.WriteLine("🔧 Veritabanı kontrol ediliyor...");
        await db.Database.EnsureCreatedAsync();
        Console.WriteLine("✅ Veritabanı tabloları oluşturuldu!");
        
        if (!await db.Users.AnyAsync())
        {
            var testUser = new User { Username = "testuser", CreatedAt = DateTime.UtcNow };
            db.Users.Add(testUser);
            await db.SaveChangesAsync();
            Console.WriteLine($"✅ Test kullanıcısı eklendi: ID={testUser.Id}");
        }
        
        Console.WriteLine("🎉 VERİTABANI HAZIR!");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"❌ Veritabanı hatası: {ex.Message}");
    }
}

// ENDPOINT

//KULLANICI KAYDI
app.MapPost("/api/register", async (HttpContext httpContext, ChatContext context) => {
    try 
    {
        Console.WriteLine("📝 Register endpoint çağrıldı");
        
    
        using var reader = new StreamReader(httpContext.Request.Body, Encoding.UTF8);
        var rawBody = await reader.ReadToEndAsync();
        Console.WriteLine($"📦 Raw Body: {rawBody}");
        
        if (string.IsNullOrWhiteSpace(rawBody))
        {
            return Results.BadRequest(new { error = "Boş request body" });
        }

  
        try 
        {
            using var jsonDoc = JsonDocument.Parse(rawBody);
            var root = jsonDoc.RootElement;
            
            string username = "";
            if (root.TryGetProperty("username", out JsonElement usernameElement) && 
                usernameElement.ValueKind == JsonValueKind.String)
            {
                username = usernameElement.GetString()?.Trim() ?? "";
            }

            Console.WriteLine($"📝 Alınan username: '{username}'");
            
            if (string.IsNullOrEmpty(username) || username.Length < 2)
            {
                return Results.BadRequest(new { error = "Kullanıcı adı en az 2 karakter olmalı" });
            }
            
            // Kullanıcı kontrolü
            var existingUser = await context.Users.FirstOrDefaultAsync(u => u.Username == username);
            if (existingUser != null)
            {
                Console.WriteLine($"✅ Mevcut kullanıcı: {existingUser.Id}");
                return Results.Ok(new {
                    userId = existingUser.Id,
                    username = existingUser.Username,
                    isNew = false,
                    message = "Mevcut kullanıcı"
                });
            }
            
            // Yeni kullanıcı oluştur
            var newUser = new User { Username = username, CreatedAt = DateTime.UtcNow };
            context.Users.Add(newUser);
            await context.SaveChangesAsync();
            
            Console.WriteLine($"✅ Yeni kullanıcı oluşturuldu: {newUser.Id} - {newUser.Username}");
            
            return Results.Ok(new {
                userId = newUser.Id,
                username = newUser.Username,
                isNew = true,
                message = "Yeni kullanıcı oluşturuldu"
            });
        }
        catch (JsonException jsonEx)
        {
            Console.WriteLine($"❌ JSON parse hatası: {jsonEx.Message}");
            return Results.BadRequest(new { error = "Geçersiz JSON formatı" });
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"❌ Register hatası: {ex.Message}");
        return Results.Problem($"Register hatası: {ex.Message}");
    }
});

//MESAJ GÖNDERME - AI ENTEGRASYONLU
app.MapPost("/api/messages", async (HttpContext httpContext, ChatContext context, AIService aiService) => {
    try 
    {
        Console.WriteLine("📤 Mesaj gönder endpoint çağrıldı");
        
    
        using var reader = new StreamReader(httpContext.Request.Body, Encoding.UTF8);
        var rawBody = await reader.ReadToEndAsync();
        Console.WriteLine($"📦 Raw Body: {rawBody}");
        
        if (string.IsNullOrWhiteSpace(rawBody))
        {
            return Results.BadRequest(new { error = "Boş request body" });
        }

        try 
        {
            using var jsonDoc = JsonDocument.Parse(rawBody);
            var root = jsonDoc.RootElement;
            
            string text = "";
            int userId = 0;
            
            if (root.TryGetProperty("text", out JsonElement textElement) && textElement.ValueKind == JsonValueKind.String)
                text = textElement.GetString()?.Trim() ?? "";
                
            if (root.TryGetProperty("userId", out JsonElement userIdElement) && userIdElement.ValueKind == JsonValueKind.Number)
                userId = userIdElement.GetInt32();
        
            Console.WriteLine($"📤 Alınan mesaj: UserId={userId}, Text='{text}'");
            
            if (string.IsNullOrEmpty(text))
                return Results.BadRequest(new { error = "Mesaj metni gereklidir" });
                
            if (userId <= 0)
                return Results.BadRequest(new { error = "Geçersiz kullanıcı ID" });
            
       
            var user = await context.Users.FindAsync(userId);
            if (user == null)
                return Results.BadRequest(new { error = "Kullanıcı bulunamadı" });
            
          
            string sentiment = "neutral";
            double score = 0.5;
            
            Console.WriteLine($"🤖 AI analizi başlatılıyor: '{text}'");
            
            try 
            {
                (sentiment, score) = await aiService.AnalyzeSentimentAsync(text);
                Console.WriteLine($"✅ AI Sonuç: {sentiment} ({score})");
            }
            catch (Exception aiEx)
            {
                Console.WriteLine($"⚠️ AI hatası: {aiEx.Message}");
          
                sentiment = "neutral";
                score = 0.5;
            }
            

            var newMessage = new Message 
            {
                Text = text,
                Sentiment = sentiment,
                SentimentScore = score,
                CreatedAt = DateTime.UtcNow,
                UserId = user.Id,
                Username = user.Username
            };
            
            context.Messages.Add(newMessage);
            await context.SaveChangesAsync();
            
            Console.WriteLine($"✅ Mesaj kaydedildi: ID={newMessage.Id}, Sentiment={sentiment}");
            
            return Results.Ok(new {
                id = newMessage.Id,
                username = user.Username,
                userId = user.Id,
                text = newMessage.Text,
                sentiment = newMessage.Sentiment,
                sentimentScore = newMessage.SentimentScore,
                createdAt = newMessage.CreatedAt
            });
        }
        catch (JsonException jsonEx)
        {
            Console.WriteLine($"❌ JSON parse hatası: {jsonEx.Message}");
            return Results.BadRequest(new { error = "Geçersiz JSON formatı" });
        }
    } 
    catch (Exception ex) 
    {
        Console.WriteLine($"❌ Mesaj gönderme hatası: {ex.Message}");
        return Results.Problem($"Mesaj gönderilemedi: {ex.Message}");
    }
});

//MESAJLARI GETİR
app.MapGet("/api/messages", async (ChatContext context) => {
    try 
    {
        Console.WriteLine("📥 Mesajlar getiriliyor");
        var messages = await context.Messages
            .Include(m => m.User)
            .OrderBy(m => m.CreatedAt)
            .Select(m => new {
                id = m.Id,
                username = m.User.Username,
                userId = m.UserId,
                text = m.Text,
                sentiment = m.Sentiment,
                sentimentScore = m.SentimentScore,
                createdAt = m.CreatedAt
            })
            .ToListAsync();
            
        Console.WriteLine($"✅ {messages.Count} mesaj getirildi");
        return Results.Ok(messages);
    }
    catch (Exception ex)
    {
        Console.WriteLine($"❌ Mesaj getirme hatası: {ex.Message}");
        return Results.Problem($"Mesajlar getirilemedi: {ex.Message}");
    }
});

//KULLANICI LİSTESİ
app.MapGet("/api/users", async (ChatContext context) => {
    try 
    {
        var users = await context.Users
            .Include(u => u.Messages)
            .Select(u => new {
                id = u.Id,
                username = u.Username,
                messageCount = u.Messages.Count,
                createdAt = u.CreatedAt
            })
            .ToListAsync();
            
        return Results.Ok(users);
    }
    catch (Exception ex)
    {
        Console.WriteLine($"❌ Kullanıcı getirme hatası: {ex.Message}");
        return Results.Problem($"Kullanıcılar getirilemedi: {ex.Message}");
    }
});

//AI TEST ENDPOINT'LERİ
app.MapPost("/api/test-ai", async (AIService aiService, HttpContext httpContext) => {
    try 
    {
        Console.WriteLine("🧪 AI Test endpoint çağrıldı");
        
        // JSON'ı manuel oku
        using var reader = new StreamReader(httpContext.Request.Body, Encoding.UTF8);
        var rawBody = await reader.ReadToEndAsync();
        Console.WriteLine($"📦 AI Test Raw Body: {rawBody}");
        
        if (string.IsNullOrWhiteSpace(rawBody))
        {
            return Results.BadRequest(new { error = "Boş request body" });
        }

        // JSON parse et
        using var jsonDoc = JsonDocument.Parse(rawBody);
        var root = jsonDoc.RootElement;
        
        string testText = "Bugün çok mutluyum!";
        if (root.TryGetProperty("text", out JsonElement textElement) && textElement.ValueKind == JsonValueKind.String)
        {
            testText = textElement.GetString() ?? testText;
        }
        
        Console.WriteLine($"🔍 AI Test metni: '{testText}'");
        
        // AI analizi yap
        var (sentiment, score) = await aiService.AnalyzeSentimentAsync(testText);
        
        Console.WriteLine($"✅ AI Test sonucu: {sentiment} ({score})");
        
        return Results.Ok(new {
            testText = testText,
            sentiment = sentiment,
            score = score,
            status = "success",
            message = "AI servisi çalışıyor"
        });
    }
    catch (Exception ex)
    {
        Console.WriteLine($"❌ AI Test hatası: {ex.Message}");
        return Results.Problem($"AI test hatası: {ex.Message}");
    }
});

//AI HEALTH CHECK
app.MapGet("/api/ai-health", async (AIService aiService) => {
    try 
    {
        Console.WriteLine("🔍 AI Health check...");
        
        // Test mesajı ile AI'yi dene
        var (sentiment, score) = await aiService.AnalyzeSentimentAsync("Bugün harika bir gün!");
        
        return Results.Ok(new {
            status = "connected",
            aiService = "working",
            testResult = new { sentiment, score },
            message = "AI servisi çalışıyor",
            timestamp = DateTime.UtcNow
        });
    }
    catch (Exception ex)
    {
        return Results.Ok(new {
            status = "disconnected", 
            aiService = "not_working",
            error = ex.Message,
            message = "AI servisine bağlanılamıyor",
            timestamp = DateTime.UtcNow
        });
    }
});

// 7. DEBUG ENDPOINT
app.MapPost("/api/debug", async (HttpContext httpContext) => {
    try 
    {
        Console.WriteLine("🔍 Debug endpoint çağrıldı");
        
        using var reader = new StreamReader(httpContext.Request.Body, Encoding.UTF8);
        var rawBody = await reader.ReadToEndAsync();
        
        Console.WriteLine($"📦 Raw Body: {rawBody}");
        
        return Results.Ok(new { 
            message = "Debug successful", 
            rawBody = rawBody,
            timestamp = DateTime.UtcNow
        });
    }
    catch (Exception ex)
    {
        Console.WriteLine($"❌ Debug hatası: {ex.Message}");
        return Results.Problem($"Debug hatası: {ex.Message}");
    }
});

//TEST ENDPOINT'LERİ
app.MapGet("/", () => {
    Console.WriteLine("🏠 Root endpoint çağrıldı");
    return "🚀 BACKEND ÇALIŞIYOR! (Port 5050)";
});

app.MapGet("/api/test", () => {
    Console.WriteLine("🧪 Test endpoint çağrıldı");
    return Results.Ok(new { 
        message = "🎉 API TEST ÇALIŞIYOR!", 
        timestamp = DateTime.UtcNow,
        port = 5050
    });
});


app.Run("http://0.0.0.0:5050");

//MODELLER
public class User
{
    public int Id { get; set; }
    public string Username { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public List<Message> Messages { get; set; } = new();
}

public class Message
{
    public int Id { get; set; }
    public string Text { get; set; } = string.Empty;
    public string Sentiment { get; set; } = "neutral";
    public double SentimentScore { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public int UserId { get; set; }
    public User User { get; set; } = null!;
    public string Username { get; set; } = string.Empty;
}

public class ChatContext : DbContext
{
    public ChatContext(DbContextOptions<ChatContext> options) : base(options) { }
    
    public DbSet<Message> Messages => Set<Message>();
    public DbSet<User> Users => Set<User>();
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>()
            .HasIndex(u => u.Username)
            .IsUnique();
            
        modelBuilder.Entity<Message>()
            .HasOne(m => m.User)
            .WithMany(u => u.Messages)
            .HasForeignKey(m => m.UserId);
    }
}

//SERVİSLER
public class AIService
{
    private readonly HttpClient _httpClient;

    public AIService(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<(string sentiment, double score)> AnalyzeSentimentAsync(string text)
    {
        try
        {
            Console.WriteLine($"🤖 AI Analiz için metin: '{text}'");

            // 1. DENEME: Doğrudan JSON formatında gönder
            var requestData = new { text = text };
            var jsonContent = JsonSerializer.Serialize(requestData);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            
            Console.WriteLine("🔄 Hugging Face'e istek gönderiliyor...");
            
            // Önce /analyze endpoint'ini dene
            var response = await _httpClient.PostAsync("/analyze", content);
            
            if (response.IsSuccessStatusCode)
            {
                var responseString = await response.Content.ReadAsStringAsync();
                Console.WriteLine($"📨 AI Response: {responseString}");
                
                try
                {
                    var aiResult = JsonSerializer.Deserialize<JsonElement>(responseString);
                    
                    // Python kodunuzdaki response formatına göre parse et
                    var sentiment = aiResult.TryGetProperty("sentiment", out var s) 
                        ? s.GetString() ?? "neutral" 
                        : "neutral";
                        
                    var score = aiResult.TryGetProperty("score", out var sc) 
                        ? sc.ValueKind == JsonValueKind.Number ? sc.GetDouble() : 0.5
                        : 0.5;

                    Console.WriteLine($"✅ AI Analiz Sonucu: {sentiment} ({score})");
                    return (sentiment, score);
                }
                catch (JsonException jsonEx)
                {
                    Console.WriteLine($"❌ JSON parse hatası: {jsonEx.Message}");
                }
            }
            else
            {
                Console.WriteLine($"⚠️ /analyze endpoint hatası: {response.StatusCode}");
                
                // 2. DENEME: Gradio formatını dene
                return await TryGradioFormat(text);
            }
            
            return ("neutral", 0.5);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ AI analiz hatası: {ex.Message}");
            return ("neutral", 0.5);
        }
    }

    private async Task<(string sentiment, double score)> TryGradioFormat(string text)
    {
        try
        {
            // Gradio formatı
            var formData = new List<KeyValuePair<string, string>>
            {
                new("text", text)
            };
            
            var content = new FormUrlEncodedContent(formData);
            var response = await _httpClient.PostAsync("/", content);
            
            if (response.IsSuccessStatusCode)
            {
                var responseString = await response.Content.ReadAsStringAsync();
                Console.WriteLine($"📨 Gradio Response: {responseString.Substring(0, Math.Min(200, responseString.Length))}...");
                
                // Basit sentiment tespiti
                if (responseString.Contains("positive") || responseString.Contains("pozitif"))
                    return ("positive", 0.8);
                else if (responseString.Contains("negative") || responseString.Contains("negatif"))
                    return ("negative", 0.8);
            }
            
            return ("neutral", 0.5);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Gradio format hatası: {ex.Message}");
            return ("neutral", 0.5);
        }
    }
}
