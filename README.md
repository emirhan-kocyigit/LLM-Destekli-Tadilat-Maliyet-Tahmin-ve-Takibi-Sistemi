# 🏠 Ev Tadilat Fiyat Tahmin Asistanı

Yapay zeka destekli ev tadilat maliyet hesaplama web uygulaması.

## 🚀 Kurulum

### 1. Gereksinimleri Yükleyin

```bash
pip install -r requirements.txt
```

### 2. Dosya Yapısı

```
proje/
├── tadilat_asistani.py  # Ana asistan sınıfı
├── app.py               # Flask web uygulaması
├── data.csv             # Fiyat verileri (düzenlenmişfiyat.csv)
├── requirements.txt     # Python bağımlılıkları
└── README.md           # Bu dosya
```

### 3. Çalıştırma

```bash
# CSV dosya yolunu ayarlayın (opsiyonel)
export CSV_PATH="./data.csv"

# Uygulamayı başlatın
python app.py
```

Tarayıcınızda `http://localhost:5000` adresini açın.

## 📦 Özellikler

### ✅ Akıllı Fiyatlandırma
- **Seramik/Fayans**: m² bazlı hesaplama (149-317 TL/m²)
- **Musluk/Batarya**: Adet bazlı, seçeneklerle (63-1088 TL)
- **Priz Montajı**: Elektrik sortisi dahil (971-2015 TL)
- **Mutfak Dolabı**: m² bazlı (6565-8368 TL/m²)
- **Lavabo/Klozet**: Adet bazlı seçeneklerle
- **Boya İşleri**: m² bazlı işçilik

### ✅ Yapay Zeka Destekli Konuşma
- Eksik bilgileri otomatik sorar
- Doğal dil anlama
- Çoklu iş kalemlerini takip eder
- Önceki konuşmayı hatırlar

### ✅ Seçim Gerektiren Kalemler
Bazı ürünler için (musluk, dolap, lavabo vb.) sistem:
1. Ortalama fiyatla tahmin verir
2. Fiyat aralığını gösterir
3. Alternatif ürün seçenekleri sunar

## 🔧 Konfigürasyon

### Groq API Key
`tadilat_asistani.py` dosyasında API anahtarınızı değiştirin:

```python
GROQ_API_KEY = "your-api-key-here"
```

### Usta Saatlik Ücreti
```python
self.usta_saat_ucreti = 250.0  # TL/saat
```

### Yeni Kategori Ekleme
`KategoriEslestirici.KATEGORI_DESENLERI` sözlüğüne yeni kategori ekleyebilirsiniz:

```python
"yeni_kategori": {
    "dahil": r"anahtar|kelime|pattern",
    "haric": r"haric_edilecek|kelimeler",
    "varsayilan_birim": "m2",
    "varsayilan_fiyat": 100.0
}
```

## 📊 Örnek Kullanım

**Kullanıcı:** Mutfağımın fayanslarını yenilemek istiyorum

**Asistan:** Lütfen mutfak seramiklerinin toplam kaç m² olduğunu belirtiniz.

**Kullanıcı:** 35 m2

**Asistan:** 
```
📊 Fiyat Analizi

MUTFAK - seramik: 5,810.00 TL Malzeme + 7,000.00 TL İşçilik

💰 TOPLAM: 12,810.00 TL
⏱️ Tahmini Süre: 3.5 İş Günü
```

## 🔄 API Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/` | GET | Ana sayfa (Web UI) |
| `/api/chat` | POST | Sohbet mesajı gönder |
| `/api/reset` | POST | Sohbeti sıfırla |
| `/api/kategoriler` | GET | Mevcut kategorileri listele |

### Chat API Örneği

```javascript
fetch('/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        message: "Mutfak tadilatı istiyorum",
        session_id: "unique-session-id"
    })
});
```

## 📝 Lisans

MIT License

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/yenilik`)
3. Commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Push edin (`git push origin feature/yenilik`)
5. Pull Request açın
