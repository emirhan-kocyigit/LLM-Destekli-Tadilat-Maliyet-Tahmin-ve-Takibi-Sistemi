
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, send_from_directory
from flask_cors import CORS
import json
import os
import uuid
from datetime import datetime
from functools import wraps

from LLM import TadilatAsistani, KategoriEslestirici
import database as db

app = Flask(__name__)
app.secret_key = 'tadilat-asistan-secret-key-2025'
CORS(app)

CSV_PATH = os.environ.get('CSV_PATH', r"C:\Users\PC\Desktop\Hakan Hoca\yenicsv\düzenlenmişfiyat.csv")

TADILAT_IMAGE_PATH = r"C:\Users\PC\Desktop\Hakan Hoca\tadilat.png"

db.init_database()

asistanlar = {}

def get_asistan(session_id: str) -> TadilatAsistani:
    if session_id not in asistanlar:
        asistanlar[session_id] = TadilatAsistani(CSV_PATH)
    return asistanlar[session_id]

def isletme_giris_gerekli(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('isletme_giris'):
            return redirect(url_for('giris_sayfasi'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/static/tadilat.png')
def serve_tadilat_image():
    return send_from_directory(TADILAT_IMAGE_PATH, 'tadilat.png')


GIRIS_SAYFASI = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏠 Ev Tadilat Asistanı</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Poppins', sans-serif;
            min-height: 100vh;
            background: #f8f9fa;
        }
        .page-container {
            display: flex;
            min-height: 100vh;
        }
        
        /* Sol Panel - Tanıtım */
        .left-panel {
            flex: 1;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        .left-panel::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
            animation: pulse 15s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        .left-content {
            position: relative;
            z-index: 1;
            max-width: 500px;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 40px;
        }
        .brand-icon {
            width: 70px;
            height: 70px;
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
        }
        .brand h1 {
            font-size: 2rem;
            font-weight: 700;
        }
        .tagline {
            font-size: 1.5rem;
            font-weight: 300;
            margin-bottom: 30px;
            line-height: 1.6;
        }
        .features {
            margin-bottom: 40px;
        }
        .feature {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        .feature-icon {
            width: 50px;
            height: 50px;
            background: rgba(255,255,255,0.2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }
        .feature-text h3 { font-size: 1rem; font-weight: 600; }
        .feature-text p { font-size: 0.85rem; opacity: 0.9; }
        
        .mascot-container {
            text-align: center;
            margin-top: 30px;
        }
        .mascot-img {
            max-width: 250px;
            filter: drop-shadow(0 20px 40px rgba(0,0,0,0.3));
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
        }
        
        /* Sağ Panel - Form */
        .right-panel {
            flex: 1;
            padding: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
        }
        .form-container {
            max-width: 450px;
            width: 100%;
        }
        .form-header {
            text-align: center;
            margin-bottom: 40px;
        }
        .form-header h2 {
            font-size: 1.8rem;
            color: #333;
            margin-bottom: 10px;
        }
        .form-header p {
            color: #666;
            font-size: 0.95rem;
        }
        
        .tabs {
            display: flex;
            margin-bottom: 30px;
            background: #f0f0f0;
            border-radius: 12px;
            padding: 5px;
        }
        .tab {
            flex: 1;
            padding: 14px;
            text-align: center;
            cursor: pointer;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s;
            font-size: 0.95rem;
        }
        .tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        .tab:not(.active):hover { background: #e0e0e0; }
        
        .form-section { display: none; }
        .form-section.active { display: block; }
        
        .form-group { margin-bottom: 20px; }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #444;
            font-size: 0.95rem;
        }
        .form-group input {
            width: 100%;
            padding: 16px 20px;
            border: 2px solid #e8e8e8;
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s;
            font-family: inherit;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        }
        .form-group input::placeholder { color: #aaa; }
        
        .btn {
            width: 100%;
            padding: 18px;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .error {
            background: #fee;
            color: #c00;
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
            font-size: 0.9rem;
        }
        
        /* Responsive */
        @media (max-width: 900px) {
            .page-container { flex-direction: column; }
            .left-panel { padding: 40px 30px; }
            .right-panel { padding: 40px 30px; }
            .mascot-img { max-width: 180px; }
        }
    </style>
</head>
<body>
    <div class="page-container">
        <!-- Sol Panel -->
        <div class="left-panel">
            <div class="left-content">
                <div class="brand">
                    <div class="brand-icon">🏠</div>
                    <h1>Tadilat Asistanı</h1>
                </div>
                
                <p class="tagline">
                    Yapay zeka destekli tadilat bütçe hesaplama sistemi ile evinizi hayalinizdeki gibi yenileyin!
                </p>
                
                <div class="features">
                    <div class="feature">
                        <div class="feature-icon">🤖</div>
                        <div class="feature-text">
                            <h3>Akıllı Fiyat Tahmini</h3>
                            <p>AI ile anında maliyet hesaplama</p>
                        </div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🎨</div>
                        <div class="feature-text">
                            <h3>Ürün Seçenekleri</h3>
                            <p>Bütçenize uygun malzeme seçimi</p>
                        </div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🏢</div>
                        <div class="feature-text">
                            <h3>Güvenilir İşletmeler</h3>
                            <p>Onaylı firmalardan teklif alın</p>
                        </div>
                    </div>
                </div>
                
                <div class="mascot-container">
                    <img src="/static/tadilat.png" alt="Tadilat Ustası" class="mascot-img" 
                         onerror="this.style.display='none'">
                </div>
            </div>
        </div>
        
        <!-- Sağ Panel -->
        <div class="right-panel">
            <div class="form-container">
                <div class="form-header">
                    <h2>Hoş Geldiniz</h2>
                    <p>Teklif almak veya işletme panelinize giriş yapmak için devam edin</p>
                </div>
                
                <div class="tabs">
                    <div class="tab active" onclick="showTab('kullanici')">👤 Teklif Al</div>
                    <div class="tab" onclick="showTab('isletme')">🏢 İşletme Girişi</div>
                </div>
                
                <div class="error" id="errorMsg"></div>
                
                <!-- Kullanıcı Formu -->
                <div class="form-section active" id="kullanici-form">
                    <form onsubmit="kullaniciGiris(event)">
                        <div class="form-group">
                            <label>👤 Adınız Soyadınız</label>
                            <input type="text" id="kullanici_isim" placeholder="Örn: Ahmet Yılmaz" required>
                        </div>
                        <div class="form-group">
                            <label>📱 Telefon Numaranız</label>
                            <input type="tel" id="kullanici_telefon" placeholder="Örn: 0532 123 45 67" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Teklif Almaya Başla →</button>
                    </form>
                </div>
                
                <!-- İşletme Formu -->
                <div class="form-section" id="isletme-form">
                    <form onsubmit="isletmeGiris(event)">
                        <div class="form-group">
                            <label>👤 Kullanıcı Adı</label>
                            <input type="text" id="isletme_kullanici" placeholder="Kullanıcı adınız" required>
                        </div>
                        <div class="form-group">
                            <label>🔑 Şifre</label>
                            <input type="password" id="isletme_sifre" placeholder="••••••" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Giriş Yap</button>
                    </form>
                    <p style="text-align:center; margin-top:20px; color:#888; font-size:0.85rem;">
                        Demo: x/x, y/y veya z/z
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.form-section').forEach(f => f.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab + '-form').classList.add('active');
            document.getElementById('errorMsg').style.display = 'none';
        }
        
        function showError(msg) {
            const el = document.getElementById('errorMsg');
            el.textContent = msg;
            el.style.display = 'block';
        }
        
        async function kullaniciGiris(e) {
            e.preventDefault();
            const isim = document.getElementById('kullanici_isim').value;
            const telefon = document.getElementById('kullanici_telefon').value;
            
            try {
                const response = await fetch('/api/kullanici-giris', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({isim, telefon})
                });
                const data = await response.json();
                if (data.success) {
                    window.location.href = '/chat?session=' + data.session_id;
                } else {
                    showError(data.error || 'Bir hata oluştu');
                }
            } catch (err) { showError('Bağlantı hatası'); }
        }
        
        async function isletmeGiris(e) {
            e.preventDefault();
            const kullanici = document.getElementById('isletme_kullanici').value;
            const sifre = document.getElementById('isletme_sifre').value;
            
            try {
                const response = await fetch('/api/isletme-giris', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({kullanici_adi: kullanici, sifre: sifre})
                });
                const data = await response.json();
                if (data.success) {
                    window.location.href = '/panel';
                } else {
                    showError(data.error || 'Giriş başarısız');
                }
            } catch (err) { showError('Bağlantı hatası'); }
        }
    </script>
</body>
</html>
'''

CHAT_SAYFASI = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏠 Tadilat Asistanı</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 20px; }
        .header h1 { font-size: 1.8rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
        .user-info {
            background: rgba(255,255,255,0.2);
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            margin-top: 10px;
            font-size: 0.9rem;
        }
        .chat-container {
            background: white;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .quick-actions {
            padding: 12px 20px;
            background: #f8f9fa;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            border-bottom: 1px solid #eee;
        }
        .quick-btn {
            padding: 10px 18px;
            background: white;
            border: 2px solid #e8e8e8;
            border-radius: 25px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s;
            font-family: inherit;
            font-weight: 500;
        }
        .quick-btn:hover { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border-color: transparent; 
        }
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .message { margin-bottom: 15px; display: flex; flex-direction: column; }
        .message.user { align-items: flex-end; }
        .message.assistant { align-items: flex-start; }
        .message-bubble {
            max-width: 85%;
            padding: 14px 20px;
            border-radius: 20px;
            line-height: 1.6;
            font-size: 0.95rem;
        }
        .message.user .message-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 6px;
        }
        .message.assistant .message-bubble {
            background: white;
            color: #333;
            border-bottom-left-radius: 6px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        }
        .message-time { font-size: 0.75rem; color: #999; margin-top: 5px; }
        
        /* Fiyat Raporu */
        .price-report {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-radius: 16px;
            padding: 20px;
            margin-top: 15px;
        }
        .price-report h4 { color: #155724; margin-bottom: 15px; font-size: 1.1rem; }
        .price-item {
            background: white;
            padding: 12px 16px;
            border-radius: 12px;
            margin-bottom: 10px;
            border-left: 4px solid #28a745;
        }
        .price-item .detail { font-weight: 600; color: #333; font-size: 0.95rem; }
        .price-item .note { font-size: 0.85rem; color: #666; margin-top: 5px; }
        .price-total {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 20px;
            border-radius: 16px;
            margin-top: 15px;
            text-align: center;
        }
        .price-total .amount { font-size: 2rem; font-weight: 700; }
        .price-total .duration { font-size: 1rem; opacity: 0.9; margin-top: 8px; }
        
        /* İşletme Seçimi Butonu */
        .get-quote-btn {
            width: 100%;
            padding: 16px;
            margin-top: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .get-quote-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        /* Seçenek Kartları */
        .selection-options {
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            border-radius: 16px;
            padding: 20px;
            margin-top: 15px;
        }
        .selection-options h4 { color: #e65100; margin-bottom: 12px; }
        .selection-items {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 10px;
        }
        .option-card {
            background: white;
            padding: 14px 12px;
            border-radius: 12px;
            border: 2px solid #eee;
            cursor: pointer;
            transition: all 0.2s;
            text-align: center;
        }
        .option-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }
        .option-card.budget { border-color: #4caf50; }
        .option-card.standard { border-color: #2196f3; }
        .option-card.premium { border-color: #9c27b0; }
        .option-card.selected { border-color: #ff9800 !important; background: #fff3e0 !important; }
        .option-name { font-weight: 600; font-size: 0.85rem; margin-bottom: 6px; color: #333; }
        .option-price { font-size: 0.95rem; font-weight: 700; color: #e65100; }
        
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 12px;
        }
        .chat-input {
            flex: 1;
            padding: 16px 24px;
            border: 2px solid #e8e8e8;
            border-radius: 30px;
            font-size: 1rem;
            outline: none;
            font-family: inherit;
        }
        .chat-input:focus { border-color: #667eea; }
        .send-btn {
            padding: 16px 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 30px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            font-family: inherit;
        }
        .send-btn:hover { box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4); }
        
        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 12px 18px;
            background: white;
            border-radius: 20px;
            width: fit-content;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .typing-dot {
            width: 8px; height: 8px;
            background: #667eea;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
        
        .back-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            padding: 12px 24px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            font-family: inherit;
            backdrop-filter: blur(10px);
        }
        .back-btn:hover { background: rgba(255,255,255,0.3); }
        
        /* İşletme Seçim Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.6);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(5px);
        }
        .modal.active { display: flex; }
        .modal-content {
            background: white;
            border-radius: 24px;
            max-width: 600px;
            width: 90%;
            max-height: 85vh;
            overflow-y: auto;
            animation: modalSlide 0.3s ease;
        }
        @keyframes modalSlide {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .modal-header {
            padding: 25px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .modal-header h2 { font-size: 1.4rem; color: #333; }
        .modal-close {
            background: #f0f0f0;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 1.3rem;
            cursor: pointer;
            color: #666;
        }
        .modal-close:hover { background: #e0e0e0; }
        .modal-body { padding: 25px; }
        
        .isletme-card {
            background: #f8f9fa;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 15px;
            border: 2px solid transparent;
            cursor: pointer;
            transition: all 0.3s;
        }
        .isletme-card:hover {
            border-color: #667eea;
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .isletme-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 12px;
        }
        .isletme-logo {
            width: 55px;
            height: 55px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: white;
            font-weight: 700;
        }
        .isletme-info h3 { font-size: 1.1rem; color: #333; margin-bottom: 3px; }
        .isletme-info p { font-size: 0.85rem; color: #888; }
        .isletme-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 10px;
        }
        .badge-indirim { background: #ffeaea; color: #e74c3c; }
        .badge-taksit { background: #e8f4fd; color: #3498db; }
        
        .isletme-detay {
            display: none;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
        }
        .isletme-detay.active { display: block; }
        .isletme-detay p { margin-bottom: 8px; font-size: 0.95rem; }
        .isletme-telefon {
            font-size: 1.3rem;
            font-weight: 700;
            color: #28a745;
            margin: 15px 0;
        }
        .contact-btns { display: flex; gap: 10px; margin-top: 15px; }
        .contact-btn {
            flex: 1;
            padding: 14px;
            border-radius: 12px;
            text-align: center;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s;
        }
        .contact-btn.whatsapp { background: #25D366; color: white; }
        .contact-btn.phone { background: #667eea; color: white; }
        .contact-btn:hover { transform: translateY(-2px); }
        
        .success-message {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            padding: 30px;
            border-radius: 16px;
            text-align: center;
        }
        .success-message h3 { color: #155724; margin-bottom: 15px; font-size: 1.3rem; }
        .success-message p { color: #155724; font-size: 1rem; }
    </style>
</head>
<body>
    <button class="back-btn" onclick="window.location.href='/'">← Geri</button>
    
    <div class="container">
        <div class="header">
            <h1>🏠 Tadilat Asistanı</h1>
            <div class="user-info">👤 {{ kullanici_isim }} | 📱 {{ kullanici_telefon }}</div>
        </div>
        
        <div class="chat-container">
            <div class="quick-actions">
                <button class="quick-btn" onclick="sendQuickMessage('Mutfak tadilatı yapmak istiyorum')">🍳 Mutfak</button>
                <button class="quick-btn" onclick="sendQuickMessage('Banyo yenilemek istiyorum')">🚿 Banyo</button>
                <button class="quick-btn" onclick="sendQuickMessage('Duvar boyası yaptırmak istiyorum')">🎨 Duvar Boyası</button>
                <button class="quick-btn" onclick="sendQuickMessage('Tavan boyası yaptırmak istiyorum')">🖌️ Tavan Boyası</button>
                <button class="quick-btn" onclick="sendQuickMessage('Zemin döşemesi yaptırmak istiyorum')">🏠 Zemin</button>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message assistant">
                    <div class="message-bubble">
                        Merhaba <strong>{{ kullanici_isim }}</strong>! 👋<br><br>
                        Ben tadilat asistanınızım. Evinizde yapmak istediğiniz işleri anlatın, size detaylı fiyat ve süre tahmini çıkarayım.
                    </div>
                </div>
            </div>
            
            <div class="chat-input-container">
                <input type="text" class="chat-input" id="userInput" 
                       placeholder="Tadilat isteğinizi yazın..." 
                       onkeypress="handleKeyPress(event)">
                <button class="send-btn" id="sendBtn" onclick="sendMessage()">Gönder</button>
            </div>
        </div>
    </div>
    
    <!-- İşletme Seçim Modal -->
    <div class="modal" id="isletmeModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>🏢 İşletme Seçin</h2>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body" id="isletmeList">
            </div>
        </div>
    </div>
    
    <script>
        const sessionId = '{{ session_id }}';
        let seciliUrunler = {};
        let sonTeklifButce = 0;
        let sonIsler = [];
        let isletmeler = [];
        
        function getCurrentTime() {
            return new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
        }
        
        function addMessage(content, isUser = false) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
            messageDiv.innerHTML = `
                <div class="message-bubble">${content}</div>
                <span class="message-time">${getCurrentTime()}</span>
            `;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function addTypingIndicator() {
            const chatMessages = document.getElementById('chatMessages');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message assistant';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = `
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            `;
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function removeTypingIndicator() {
            const indicator = document.getElementById('typingIndicator');
            if (indicator) indicator.remove();
        }
        
        function formatPriceReport(data) {
            if (!data.rapor || data.rapor.length === 0) return '';
            
            sonTeklifButce = data.toplam_maliyet;
            sonIsler = data.rapor;
            
            let html = '<div class="price-report"><h4>📊 Fiyat Analizi</h4>';
            
            data.rapor.forEach(item => {
                html += `
                    <div class="price-item">
                        <div class="detail">${item.detay}</div>
                        ${item.not_ ? `<div class="note">${item.not_}</div>` : ''}
                    </div>
                `;
            });
            
            html += `
                <div class="price-total">
                    <div class="amount">💰 ${data.toplam_maliyet.toLocaleString('tr-TR', {minimumFractionDigits: 2})} TL</div>
                    <div class="duration">⏱️ Tahmini Süre: ${data.toplam_gun.toFixed(1)} İş Günü</div>
                </div>
            `;
            
            // Seçim gereken kalemler
            if (data.secim_gereken && data.secim_gereken.length > 0) {
                html += '<div class="selection-options"><h4>🎯 Ürün Seçenekleri</h4>';
                data.secim_gereken.forEach(item => {
                    html += `<div style="margin-bottom:15px;">
                        <strong>${item.kalem.replace('_', ' ').toUpperCase()}</strong> 
                        <span style="color:#888">(${item.min_fiyat.toFixed(0)}-${item.max_fiyat.toFixed(0)} TL)</span>
                        <div class="selection-items" style="margin-top:10px;">`;
                    item.secenekler.forEach((sec, idx) => {
                        const fiyatClass = idx === 0 ? 'budget' : (idx >= item.secenekler.length - 1 ? 'premium' : 'standard');
                        html += `
                            <div class="option-card ${fiyatClass}" onclick="selectProduct('${item.kalem}', '${item.oda}', '${sec.poz_no}', '${sec.kisa_isim}', ${sec.fiyat})">
                                <div class="option-name">${sec.kisa_isim}</div>
                                <div class="option-price">${sec.fiyat.toFixed(2)} TL</div>
                            </div>
                        `;
                    });
                    html += '</div></div>';
                });
                html += '</div>';
            }
            
            // Teklif Al Butonu
            html += `<button class="get-quote-btn" onclick="showIsletmeler()">🏢 İşletmelerden Teklif Al</button>`;
            
            html += '</div>';
            return html;
        }
        
        async function selectProduct(kalem, oda, pozNo, isim, fiyat) {
            seciliUrunler[kalem + '_' + oda] = {poz_no: pozNo, fiyat: fiyat};
            
            addMessage(`<strong>${kalem.replace('_', ' ')}</strong> için <strong>${isim}</strong> seçtim`, true);
            addTypingIndicator();
            
            try {
                const response = await fetch('/api/secim', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ session_id: sessionId, kalem, oda, poz_no: pozNo, fiyat })
                });
                const data = await response.json();
                removeTypingIndicator();
                
                let responseHtml = data.cevap || '✅ Seçiminiz kaydedildi.';
                if (data.rapor) responseHtml += formatPriceReport(data);
                addMessage(responseHtml);
            } catch (error) {
                removeTypingIndicator();
                addMessage('❌ Bir hata oluştu.');
            }
        }
        
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message) return;
            
            addMessage(message, true);
            input.value = '';
            addTypingIndicator();
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message, session_id: sessionId, secimler: seciliUrunler })
                });
                const data = await response.json();
                removeTypingIndicator();
                
                let responseHtml = data.cevap || '';
                if (data.rapor) responseHtml += formatPriceReport(data);
                addMessage(responseHtml);
            } catch (error) {
                removeTypingIndicator();
                addMessage('❌ Bir hata oluştu.');
            }
        }
        
        function sendQuickMessage(text) {
            document.getElementById('userInput').value = text;
            sendMessage();
        }
        
        function handleKeyPress(e) {
            if (e.key === 'Enter') sendMessage();
        }
        
        // İşletme Seçimi
        async function showIsletmeler() {
            const response = await fetch('/api/isletmeler');
            isletmeler = await response.json();
            
            let html = '';
            isletmeler.forEach((isl, idx) => {
                const badgeClass = isl.avantaj === 'indirim' ? 'badge-indirim' : 'badge-taksit';
                const badgeIcon = isl.avantaj === 'indirim' ? '🎁' : '💳';
                html += `
                    <div class="isletme-card" onclick="toggleIsletme(${idx})">
                        <div class="isletme-header">
                            <div class="isletme-logo" style="background:${isl.logo_renk}">${isl.isim.charAt(0)}</div>
                            <div class="isletme-info">
                                <h3>${isl.isim}</h3>
                                <p>📍 ${isl.adres}</p>
                            </div>
                        </div>
                        <span class="isletme-badge ${badgeClass}">${badgeIcon} ${isl.avantaj_detay}</span>
                        
                        <div class="isletme-detay" id="isletme-${idx}">
                            <p class="isletme-telefon">📞 ${isl.telefon}</p>
                            <div class="contact-btns">
                                <a href="https://wa.me/90${isl.telefon.replace(/\\s/g, '').replace(/^0/, '')}" target="_blank" class="contact-btn whatsapp">📱 WhatsApp</a>
                                <a href="tel:${isl.telefon}" class="contact-btn phone">📞 Ara</a>
                            </div>
                            <button onclick="event.stopPropagation(); teklifKabul(${isl.id}, '${isl.isim}')" style="width:100%;margin-top:15px;padding:14px;background:#28a745;color:white;border:none;border-radius:12px;font-size:1rem;font-weight:600;cursor:pointer;">
                                ✅ Bu İşletmeyi Seç
                            </button>
                        </div>
                    </div>
                `;
            });
            
            document.getElementById('isletmeList').innerHTML = html;
            document.getElementById('isletmeModal').classList.add('active');
        }
        
        function toggleIsletme(idx) {
            const el = document.getElementById('isletme-' + idx);
            const wasActive = el.classList.contains('active');
            
            document.querySelectorAll('.isletme-detay').forEach(d => d.classList.remove('active'));
            
            if (!wasActive) {
                el.classList.add('active');
            }
        }
        
        async function teklifKabul(isletmeId, isletmeIsim) {
            try {
                await fetch('/api/teklif-kabul', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        session_id: sessionId,
                        isletme_id: isletmeId,
                        toplam_butce: sonTeklifButce,
                        isler: sonIsler
                    })
                });
                
                document.getElementById('isletmeList').innerHTML = `
                    <div class="success-message">
                        <h3>🎉 Tebrikler!</h3>
                        <p><strong>${isletmeIsim}</strong> ile iletişime geçebilirsiniz.<br><br>
                        İşletme sizinle en kısa sürede iletişime geçecektir.</p>
                    </div>
                `;
            } catch (error) {
                alert('Bir hata oluştu');
            }
        }
        
        function closeModal() {
            document.getElementById('isletmeModal').classList.remove('active');
        }
    </script>
</body>
</html>
'''

ISLETME_PANEL = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏢 {{ isletme_isim }} - Panel</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Poppins', sans-serif; background: #f5f7fa; min-height: 100vh; }
        .header {
            background: linear-gradient(135deg, {{ logo_renk }} 0%, {{ logo_renk }}cc 100%);
            color: white;
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 1.5rem; }
        .btn-logout {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-family: inherit;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 30px; }
        
        .tabs { display: flex; gap: 10px; margin-bottom: 30px; }
        .tab-btn {
            padding: 14px 28px;
            background: white;
            border: 2px solid #e8e8e8;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            font-family: inherit;
            transition: all 0.2s;
        }
        .tab-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: transparent;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        .stat-card h3 { color: #888; font-size: 0.85rem; margin-bottom: 8px; }
        .stat-card .value { font-size: 2rem; font-weight: 700; }
        .stat-card .value.green { color: #28a745; }
        .stat-card .value.blue { color: #667eea; }
        .stat-card .value.orange { color: #fd7e14; }
        
        .card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            overflow: hidden;
        }
        .card-header {
            padding: 20px 25px;
            border-bottom: 1px solid #eee;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .customer-item {
            padding: 20px 25px;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            transition: background 0.2s;
        }
        .customer-item:hover { background: #f9f9f9; }
        .customer-info h4 { font-size: 1rem; margin-bottom: 5px; }
        .customer-info p { color: #888; font-size: 0.85rem; }
        .customer-meta { text-align: right; }
        .customer-meta .budget { font-size: 1.2rem; font-weight: 700; color: #28a745; }
        .badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 8px;
        }
        .badge.new { background: #e3f2fd; color: #1976d2; }
        .badge.accepted { background: #d4edda; color: #155724; }
        
        .empty-state { text-align: center; padding: 60px 20px; color: #888; }
        .empty-state span { font-size: 4rem; display: block; margin-bottom: 15px; }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        .modal.active { display: flex; }
        .modal-content {
            background: white;
            border-radius: 20px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        .modal-header {
            padding: 20px 25px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .modal-close {
            background: #f0f0f0;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
        }
        .modal-body { padding: 25px; }
        .chat-log {
            background: #f5f5f5;
            border-radius: 12px;
            padding: 15px;
            max-height: 250px;
            overflow-y: auto;
        }
        .chat-msg { margin-bottom: 10px; padding: 10px 15px; border-radius: 10px; }
        .chat-msg.user { background: #667eea; color: white; margin-left: 20%; }
        .chat-msg.assistant { background: white; margin-right: 20%; }
        .contact-btns { display: flex; gap: 10px; margin-top: 20px; }
        .contact-btn {
            flex: 1;
            padding: 14px;
            border-radius: 12px;
            text-align: center;
            text-decoration: none;
            font-weight: 600;
        }
        .contact-btn.whatsapp { background: #25D366; color: white; }
        .contact-btn.phone { background: #667eea; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏢 {{ isletme_isim }}</h1>
        <button class="btn-logout" onclick="window.location.href='/cikis'">Çıkış Yap</button>
    </div>
    
    <div class="container">
        <div class="tabs">
            <button class="tab-btn active" onclick="showTabContent('talepler', this)">📋 Tüm Talepler</button>
            <button class="tab-btn" onclick="showTabContent('kabul', this)">✅ Teklif Kabul Edenler</button>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>📊 Toplam Talep</h3>
                <div class="value blue" id="totalRequests">0</div>
            </div>
            <div class="stat-card">
                <h3>✅ Kabul Edilen</h3>
                <div class="value green" id="acceptedCount">0</div>
            </div>
            <div class="stat-card">
                <h3>💰 Toplam Değer</h3>
                <div class="value" id="totalValue">0 TL</div>
            </div>
        </div>
        
        <div class="tab-content active" id="talepler-content">
            <div class="card">
                <div class="card-header">📋 Müşteri Talepleri</div>
                <div id="customerList"></div>
            </div>
        </div>
        
        <div class="tab-content" id="kabul-content">
            <div class="card">
                <div class="card-header">✅ Teklifi Kabul Eden Müşteriler</div>
                <div id="acceptedList"></div>
            </div>
        </div>
    </div>
    
    <div class="modal" id="detailModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Müşteri Detayı</h2>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body" id="modalBody"></div>
        </div>
    </div>
    
    <script>
        const isletmeId = {{ isletme_id }};
        let customersData = [];
        let acceptedData = [];
        
        function showTabContent(tab, btn) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(tab + '-content').classList.add('active');
        }
        
        async function loadData() {
            const statsRes = await fetch('/api/isletme-istatistik');
            const stats = await statsRes.json();
            document.getElementById('totalRequests').textContent = stats.toplam_musteri;
            document.getElementById('acceptedCount').textContent = stats.kabul_edilen;
            document.getElementById('totalValue').textContent = stats.toplam_butce.toLocaleString('tr-TR') + ' TL';
            
            const custRes = await fetch('/api/musteriler');
            customersData = (await custRes.json()).musteriler || [];
            renderCustomers();
            
            const accRes = await fetch('/api/teklif-kabulleri');
            acceptedData = (await accRes.json()).teklifler || [];
            renderAccepted();
        }
        
        function renderCustomers() {
            const container = document.getElementById('customerList');
            if (customersData.length === 0) {
                container.innerHTML = '<div class="empty-state"><span>📭</span><p>Henüz talep yok</p></div>';
                return;
            }
            container.innerHTML = customersData.map((c, idx) => `
                <div class="customer-item" onclick="showDetail(${idx}, 'customer')">
                    <div class="customer-info">
                        <h4>${c.isim} ${c.yeni ? '<span class="badge new">Yeni</span>' : ''}</h4>
                        <p>📱 ${c.telefon} • 💬 ${c.mesaj_sayisi || 0} mesaj</p>
                    </div>
                    <div class="customer-meta">
                        <div class="budget">${c.toplam_butce ? c.toplam_butce.toLocaleString('tr-TR') + ' TL' : '-'}</div>
                        <div style="color:#888;font-size:0.8rem">${c.tarih}</div>
                    </div>
                </div>
            `).join('');
        }
        
        function renderAccepted() {
            const container = document.getElementById('acceptedList');
            if (acceptedData.length === 0) {
                container.innerHTML = '<div class="empty-state"><span>📭</span><p>Henüz kabul eden yok</p></div>';
                return;
            }
            container.innerHTML = acceptedData.map((a, idx) => `
                <div class="customer-item" onclick="showDetail(${idx}, 'accepted')">
                    <div class="customer-info">
                        <h4>${a.musteri_isim} <span class="badge accepted">Kabul Etti</span></h4>
                        <p>📱 ${a.musteri_telefon}</p>
                    </div>
                    <div class="customer-meta">
                        <div class="budget">${a.toplam_butce ? a.toplam_butce.toLocaleString('tr-TR') + ' TL' : '-'}</div>
                    </div>
                </div>
            `).join('');
        }
        
        async function showDetail(idx, type) {
            const data = type === 'customer' ? customersData[idx] : acceptedData[idx];
            const isim = data.isim || data.musteri_isim;
            const telefon = data.telefon || data.musteri_telefon;
            
            document.getElementById('modalTitle').textContent = isim;
            
            let html = `
                <p><strong>📱 Telefon:</strong> ${telefon}</p>
                <p><strong>💰 Bütçe:</strong> ${(data.toplam_butce || 0).toLocaleString('tr-TR')} TL</p>
            `;
            
            if (type === 'customer' && data.session_id) {
                const sohbetRes = await fetch('/api/sohbet/' + data.session_id);
                const sohbet = (await sohbetRes.json()).sohbet || [];
                html += '<h4 style="margin:20px 0 10px">💬 Sohbet</h4><div class="chat-log">';
                sohbet.forEach(m => html += `<div class="chat-msg ${m.rol}">${m.icerik}</div>`);
                html += '</div>';
            }
            
            const tel = telefon.replace(/\\s/g, '').replace(/^0/, '');
            html += `
                <div class="contact-btns">
                    <a href="https://wa.me/90${tel}" target="_blank" class="contact-btn whatsapp">📱 WhatsApp</a>
                    <a href="tel:${telefon}" class="contact-btn phone">📞 Ara</a>
                </div>
            `;
            
            document.getElementById('modalBody').innerHTML = html;
            document.getElementById('detailModal').classList.add('active');
        }
        
        function closeModal() {
            document.getElementById('detailModal').classList.remove('active');
        }
        
        loadData();
        setInterval(loadData, 30000);
    </script>
</body>
</html>
'''

@app.route('/')
def giris_sayfasi():
    return render_template_string(GIRIS_SAYFASI)

@app.route('/chat')
def chat_sayfasi():
    session_id = request.args.get('session')
    if not session_id:
        return redirect(url_for('giris_sayfasi'))
    
    kullanici = db.kullanici_getir(session_id)
    if not kullanici:
        return redirect(url_for('giris_sayfasi'))
    
    return render_template_string(CHAT_SAYFASI, 
                                  session_id=session_id,
                                  kullanici_isim=kullanici['isim'],
                                  kullanici_telefon=kullanici['telefon'])

@app.route('/panel')
@isletme_giris_gerekli
def isletme_panel():
    isletme = db.isletme_getir(session.get('isletme_id'))
    return render_template_string(ISLETME_PANEL, 
                                  isletme_id=isletme['id'],
                                  isletme_isim=isletme['isim'],
                                  logo_renk=isletme['logo_renk'])

@app.route('/cikis')
def cikis():
    session.clear()
    return redirect(url_for('giris_sayfasi'))



@app.route('/api/kullanici-giris', methods=['POST'])
def api_kullanici_giris():
    data = request.json
    isim = data.get('isim', '').strip()
    telefon = data.get('telefon', '').strip()
    
    if not isim or not telefon:
        return jsonify({'success': False, 'error': 'İsim ve telefon gerekli'})
    
    session_id = str(uuid.uuid4())[:8]
    
    if db.kullanici_ekle(session_id, isim, telefon):
        return jsonify({'success': True, 'session_id': session_id})
    return jsonify({'success': False, 'error': 'Kayıt başarısız'})


@app.route('/api/isletme-giris', methods=['POST'])
def api_isletme_giris():
    data = request.json
    kullanici_adi = data.get('kullanici_adi', '')
    sifre = data.get('sifre', '')
    
    isletme = db.isletme_giris_kontrol(kullanici_adi, sifre)
    if isletme:
        session['isletme_giris'] = True
        session['isletme_id'] = isletme['id']
        session['isletme_isim'] = isletme['isim']
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Kullanıcı adı veya şifre hatalı'})


@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    message = data.get('message', '')
    session_id = data.get('session_id', '')
    secimler = data.get('secimler', {})
    
    kullanici = db.kullanici_getir(session_id)
    if not message or not kullanici:
        return jsonify({'error': 'Geçersiz istek'}), 400
    
    try:
        asistan = get_asistan(session_id)
        
        if secimler:
            asistan.kullanici_secimleri = secimler
        
        sonuc = asistan.llm_islem_belirle(message)
        
        db.sohbet_mesaji_ekle(session_id, 'user', message)
        db.sohbet_mesaji_ekle(session_id, 'assistant', sonuc.get('cevap', ''))
        
        response = {
            'durum': sonuc.get('durum', 'eksik_bilgi'),
            'cevap': sonuc.get('cevap', ''),
        }
        
        if sonuc.get('durum') == 'hazir' and sonuc.get('isler'):
            rapor, maliyet, sure, secim_gereken = asistan.fiyatlandir(sonuc['isler'])
            
            db.kullanici_guncelle(session_id, toplam_butce=maliyet, isler=sonuc['isler'])
            
            response['rapor'] = [{'detay': r.detay, 'not_': r.not_} for r in rapor]
            response['toplam_maliyet'] = maliyet
            response['toplam_gun'] = round(sure / 8, 1)
            response['secim_gereken'] = secim_gereken
        
        return jsonify(response)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'cevap': f'Hata: {str(e)}'}), 500


@app.route('/api/secim', methods=['POST'])
def api_urun_secimi():
    data = request.json
    session_id = data.get('session_id', '')
    kalem = data.get('kalem', '')
    oda = data.get('oda', '')
    poz_no = data.get('poz_no', '')
    fiyat = data.get('fiyat', 0)
    
    kullanici = db.kullanici_getir(session_id)
    if not kullanici:
        return jsonify({'error': 'Geçersiz oturum'}), 400
    
    try:
        asistan = get_asistan(session_id)
        asistan.kullanici_secimleri[f"{kalem}_{oda}"] = {'poz_no': poz_no, 'fiyat': fiyat}
        
        if hasattr(asistan, 'son_isler') and asistan.son_isler:
            rapor, maliyet, sure, secim_gereken = asistan.fiyatlandir(asistan.son_isler)
            db.kullanici_guncelle(session_id, toplam_butce=maliyet)
            
            return jsonify({
                'cevap': '✅ Seçiminiz kaydedildi.',
                'rapor': [{'detay': r.detay, 'not_': r.not_} for r in rapor],
                'toplam_maliyet': maliyet,
                'toplam_gun': round(sure / 8, 1),
                'secim_gereken': secim_gereken
            })
        
        return jsonify({'cevap': '✅ Seçiminiz kaydedildi.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/isletmeler', methods=['GET'])
def api_isletmeler():
    return jsonify(db.tum_isletmeleri_getir())


@app.route('/api/teklif-kabul', methods=['POST'])
def api_teklif_kabul():
    data = request.json
    session_id = data.get('session_id', '')
    isletme_id = data.get('isletme_id', 0)
    toplam_butce = data.get('toplam_butce', 0)
    isler = data.get('isler', [])
    
    kullanici = db.kullanici_getir(session_id)
    if not kullanici:
        return jsonify({'error': 'Geçersiz oturum'}), 400
    
    db.teklif_kabul_ekle(session_id, isletme_id, kullanici['isim'], kullanici['telefon'], toplam_butce, isler)
    return jsonify({'success': True})


@app.route('/api/musteriler', methods=['GET'])
@isletme_giris_gerekli
def api_musteriler():
    return jsonify({'musteriler': db.tum_kullanicilari_getir()})


@app.route('/api/teklif-kabulleri', methods=['GET'])
@isletme_giris_gerekli
def api_teklif_kabulleri():
    isletme_id = session.get('isletme_id')
    return jsonify({'teklifler': db.isletme_teklif_kabulleri_getir(isletme_id)})


@app.route('/api/sohbet/<session_id>', methods=['GET'])
@isletme_giris_gerekli
def api_sohbet_gecmisi(session_id):
    return jsonify({'sohbet': db.sohbet_gecmisi_getir(session_id)})


@app.route('/api/isletme-istatistik', methods=['GET'])
@isletme_giris_gerekli
def api_isletme_istatistik():
    isletme_id = session.get('isletme_id')
    return jsonify(db.istatistikleri_getir(isletme_id))


@app.route('/api/musteri-goruldu', methods=['POST'])
@isletme_giris_gerekli
def api_musteri_goruldu():
    data = request.json
    db.kullanici_guncelle(data.get('session_id', ''), yeni=0)
    return jsonify({'success': True})


if __name__ == '__main__':
    print("=" * 60)
    print("🏠 Ev Tadilat Fiyat Tahmin Web Uygulaması V4")
    print("=" * 60)
    print(f"📁 CSV: {CSV_PATH}")
    print(f"🖼️  Resim: {TADILAT_IMAGE_PATH}")
    print(f"🗄️  Veritabanı: {db.DATABASE_PATH}")
    print("🌐 URL: http://localhost:5000")
    print("-" * 60)
    print("🏢 İşletme Girişleri:")
    print("   X İnşaat: x / x (%10 İndirim)")
    print("   Y İnşaat: y / y (12 Ay Taksit)")
    print("   Z İnşaat: z / z (6 Ay Sıfır Faiz)")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
