"""
Veritabanı Modülü V2 - SQLite ile kalıcı veri depolama
İşletmeler ve teklif kabulleri eklendi
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

DATABASE_PATH = "tadilat_asistan.db"


def get_connection():
    """Veritabanı bağlantısı al"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Veritabanı tablolarını oluştur"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kullanicilar (
            session_id TEXT PRIMARY KEY,
            isim TEXT NOT NULL,
            telefon TEXT NOT NULL,
            tarih TEXT NOT NULL,
            toplam_butce REAL DEFAULT 0,
            yeni INTEGER DEFAULT 1,
            secimler TEXT DEFAULT '{}',
            isler TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sohbet mesajları tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sohbetler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            rol TEXT NOT NULL,
            icerik TEXT NOT NULL,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES kullanicilar(session_id)
        )
    ''')
    
    # İşletmeler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS isletmeler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT UNIQUE NOT NULL,
            sifre TEXT NOT NULL,
            isim TEXT NOT NULL,
            telefon TEXT NOT NULL,
            adres TEXT,
            avantaj TEXT,
            avantaj_detay TEXT,
            logo_renk TEXT DEFAULT '#667eea',
            aktif INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Teklif kabulleri tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teklif_kabulleri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            isletme_id INTEGER NOT NULL,
            musteri_isim TEXT NOT NULL,
            musteri_telefon TEXT NOT NULL,
            toplam_butce REAL,
            isler TEXT,
            durum TEXT DEFAULT 'beklemede',
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES kullanicilar(session_id),
            FOREIGN KEY (isletme_id) REFERENCES isletmeler(id)
        )
    ''')
    
    # Örnek işletmeleri ekle
    ornek_isletmeler = [
        ('x', 'x', 'X İnşaat', '0532 111 22 33', 'Kadıköy, İstanbul', 'indirim', '%10 İndirim', '#e74c3c'),
        ('y', 'y', 'Y İnşaat', '0533 222 33 44', 'Beşiktaş, İstanbul', 'taksit', '12 Aya Varan Taksit', '#3498db'),
        ('z', 'z', 'Z İnşaat', '0534 333 44 55', 'Üsküdar, İstanbul', 'taksit', '6 Ay Sıfır Faiz', '#2ecc71'),
    ]
    
    for isletme in ornek_isletmeler:
        cursor.execute('''
            INSERT OR IGNORE INTO isletmeler (kullanici_adi, sifre, isim, telefon, adres, avantaj, avantaj_detay, logo_renk)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', isletme)
    
    conn.commit()
    conn.close()
    print(f"✅ Veritabanı hazır: {DATABASE_PATH}")


# ==================== KULLANICI İŞLEMLERİ ====================

def kullanici_ekle(session_id: str, isim: str, telefon: str) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        tarih = datetime.now().strftime('%d.%m.%Y %H:%M')
        
        cursor.execute('''
            INSERT INTO kullanicilar (session_id, isim, telefon, tarih)
            VALUES (?, ?, ?, ?)
        ''', (session_id, isim, telefon, tarih))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Kullanıcı ekleme hatası: {e}")
        return False


def kullanici_getir(session_id: str) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM kullanicilar WHERE session_id = ?', (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'session_id': row['session_id'],
            'isim': row['isim'],
            'telefon': row['telefon'],
            'tarih': row['tarih'],
            'toplam_butce': row['toplam_butce'],
            'yeni': bool(row['yeni']),
            'secimler': json.loads(row['secimler'] or '{}'),
            'isler': json.loads(row['isler'] or '[]')
        }
    return None


def kullanici_guncelle(session_id: str, **kwargs) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['secimler', 'isler'] and isinstance(value, (dict, list)):
                value = json.dumps(value)
            updates.append(f"{key} = ?")
            values.append(value)
        
        values.append(session_id)
        
        query = f"UPDATE kullanicilar SET {', '.join(updates)} WHERE session_id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Kullanıcı güncelleme hatası: {e}")
        return False


def tum_kullanicilari_getir(isletme_id: int = None) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT k.*, 
               (SELECT COUNT(*) FROM sohbetler WHERE session_id = k.session_id) as mesaj_sayisi
        FROM kullanicilar k
        ORDER BY k.created_at DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        'session_id': row['session_id'],
        'isim': row['isim'],
        'telefon': row['telefon'],
        'tarih': row['tarih'],
        'toplam_butce': row['toplam_butce'],
        'yeni': bool(row['yeni']),
        'mesaj_sayisi': row['mesaj_sayisi'],
        'isler': json.loads(row['isler'] or '[]')
    } for row in rows]


# ==================== SOHBET İŞLEMLERİ ====================

def sohbet_mesaji_ekle(session_id: str, rol: str, icerik: str) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sohbetler (session_id, rol, icerik)
            VALUES (?, ?, ?)
        ''', (session_id, rol, icerik))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Mesaj ekleme hatası: {e}")
        return False


def sohbet_gecmisi_getir(session_id: str) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT rol, icerik, tarih FROM sohbetler
        WHERE session_id = ?
        ORDER BY id ASC
    ''', (session_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{'rol': row['rol'], 'icerik': row['icerik']} for row in rows]


# ==================== İŞLETME İŞLEMLERİ ====================

def isletme_giris_kontrol(kullanici_adi: str, sifre: str) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM isletmeler WHERE kullanici_adi = ? AND sifre = ? AND aktif = 1
    ''', (kullanici_adi, sifre))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row['id'],
            'kullanici_adi': row['kullanici_adi'],
            'isim': row['isim'],
            'telefon': row['telefon'],
            'adres': row['adres'],
            'avantaj': row['avantaj'],
            'avantaj_detay': row['avantaj_detay'],
            'logo_renk': row['logo_renk']
        }
    return None


def tum_isletmeleri_getir() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM isletmeler WHERE aktif = 1')
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        'id': row['id'],
        'isim': row['isim'],
        'telefon': row['telefon'],
        'adres': row['adres'],
        'avantaj': row['avantaj'],
        'avantaj_detay': row['avantaj_detay'],
        'logo_renk': row['logo_renk']
    } for row in rows]


def isletme_getir(isletme_id: int) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM isletmeler WHERE id = ?', (isletme_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row['id'],
            'isim': row['isim'],
            'telefon': row['telefon'],
            'adres': row['adres'],
            'avantaj': row['avantaj'],
            'avantaj_detay': row['avantaj_detay'],
            'logo_renk': row['logo_renk']
        }
    return None


# ==================== TEKLİF KABUL İŞLEMLERİ ====================

def teklif_kabul_ekle(session_id: str, isletme_id: int, musteri_isim: str, 
                      musteri_telefon: str, toplam_butce: float, isler: list) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO teklif_kabulleri (session_id, isletme_id, musteri_isim, musteri_telefon, toplam_butce, isler)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, isletme_id, musteri_isim, musteri_telefon, toplam_butce, json.dumps(isler)))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Teklif kabul ekleme hatası: {e}")
        return False


def isletme_teklif_kabulleri_getir(isletme_id: int) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM teklif_kabulleri 
        WHERE isletme_id = ?
        ORDER BY tarih DESC
    ''', (isletme_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        'id': row['id'],
        'session_id': row['session_id'],
        'musteri_isim': row['musteri_isim'],
        'musteri_telefon': row['musteri_telefon'],
        'toplam_butce': row['toplam_butce'],
        'isler': json.loads(row['isler'] or '[]'),
        'durum': row['durum'],
        'tarih': row['tarih']
    } for row in rows]


def teklif_durumu_guncelle(teklif_id: int, durum: str) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE teklif_kabulleri SET durum = ? WHERE id = ?', (durum, teklif_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Teklif durumu güncelleme hatası: {e}")
        return False


# ==================== İSTATİSTİKLER ====================

def istatistikleri_getir(isletme_id: int = None) -> Dict:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Toplam müşteri (tüm sistem)
    cursor.execute('SELECT COUNT(*) as toplam FROM kullanicilar')
    toplam_musteri = cursor.fetchone()['toplam']
    
    # Toplam bütçe
    cursor.execute('SELECT SUM(toplam_butce) as toplam FROM kullanicilar WHERE toplam_butce > 0')
    row = cursor.fetchone()
    toplam_butce = row['toplam'] if row['toplam'] else 0
    
    # Bugünkü talepler
    bugun = datetime.now().strftime('%d.%m.%Y')
    cursor.execute('SELECT COUNT(*) as toplam FROM kullanicilar WHERE tarih LIKE ?', (f'{bugun}%',))
    bugunki = cursor.fetchone()['toplam']
    
    # Yeni talepler
    cursor.execute('SELECT COUNT(*) as toplam FROM kullanicilar WHERE yeni = 1')
    yeni_talepler = cursor.fetchone()['toplam']
    
    # İşletmeye özel istatistikler
    kabul_edilen = 0
    bekleyen = 0
    if isletme_id:
        cursor.execute('SELECT COUNT(*) as toplam FROM teklif_kabulleri WHERE isletme_id = ? AND durum = ?', (isletme_id, 'kabul_edildi'))
        kabul_edilen = cursor.fetchone()['toplam']
        
        cursor.execute('SELECT COUNT(*) as toplam FROM teklif_kabulleri WHERE isletme_id = ? AND durum = ?', (isletme_id, 'beklemede'))
        bekleyen = cursor.fetchone()['toplam']
    
    conn.close()
    
    return {
        'toplam_musteri': toplam_musteri,
        'toplam_butce': toplam_butce,
        'bugunki_talepler': bugunki,
        'yeni_talepler': yeni_talepler,
        'kabul_edilen': kabul_edilen,
        'bekleyen': bekleyen
    }


# Modül yüklendiğinde veritabanını başlat
if __name__ != "__main__":
    init_database()
