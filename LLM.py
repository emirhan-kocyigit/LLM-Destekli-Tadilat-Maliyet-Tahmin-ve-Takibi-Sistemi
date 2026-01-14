
import pandas as pd
from groq import Groq
import json
import os
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

class Durum(Enum):
    EKSIK_BILGI = "eksik_bilgi"
    HAZIR = "hazir"
    SECIM_GEREKLI = "secim_gerekli"

@dataclass
class IsKalemi:
    kalem: str
    oda: str
    miktar: float
    birim: str
    tahmini_saat: float
    secenekler: Optional[List[Dict]] = None

@dataclass
class FiyatSonucu:
    detay: str
    malzeme_maliyeti: float
    iscilik_maliyeti: float
    sure: float
    not_: Optional[str] = None


class KategoriEslestirici:
    """CSV'deki kategorileri ve ürünleri akıllıca eşleştirir"""
    
    KATEGORI_DESENLERI = {
        "seramik": {
            "dahil": r"yer karosu|duvar karosu|seramik kaplama|fayans kaplama",
            "haric": r"ustası|ustas",
            "varsayilan_birim": "m2",
            "varsayilan_fiyat": 180.0
        },
        "musluk": {
            "dahil": r"musluk|batarya|eviye bataryası|lavabo bataryası|banyo bataryası",
            "haric": r"ustası|ustas|gasil|yer ocağı|dedektör|ana saat",
            "varsayilan_birim": "Ad",
            "varsayilan_fiyat": 282.50
        },
        "tezgah": {
            "dahil": r"tezgah altı dolabı|tezgah üstü dolabı|mutfak tezgah",
            "haric": None,
            "varsayilan_birim": "m2",
            "varsayilan_fiyat": 7500.0
        },
        "mutfak_dolabi": {
            "dahil": r"mutfak.*dolabı|dolabı.*mutfak|tezgah altı dolabı|tezgah üstü dolabı",
            "haric": None,
            "varsayilan_birim": "m2",
            "varsayilan_fiyat": 7500.0
        },
        "priz": {
            "dahil": r"priz sortisi|güvenlik hatlı priz",
            "haric": r"alan|katkı|geçirmezlik|geciktirici|oksijen|vakum|azot|gaz|karbondioksit",
            "varsayilan_birim": "Ad",
            "varsayilan_fiyat": 1500.0
        },
        "elektrik": {
            "dahil": r"elektrik.*sortisi|aydınlatma|lamba sortisi|anahtar sortisi",
            "haric": r"ustası|ustas",
            "varsayilan_birim": "Ad",
            "varsayilan_fiyat": 1000.0
        },
        "lavabo": {
            "dahil": r"lavabo(?!.*batarya)(?!.*musluk)",
            "haric": r"sifon|batarya|musluk",
            "varsayilan_birim": "Ad",
            "varsayilan_fiyat": 313.13
        },
        "klozet": {
            "dahil": r"klozet|alafranga.*hela|alaturka.*tuvalet|hela taşı|rezervuarlı.*tuvalet|asma klozet",
            "haric": r"yıkayıcı|tutunma|çağrı|panel|buton|wc.*banyo",
            "varsayilan_birim": "Ad",
            "varsayilan_fiyat": 900.0
        },
        "dus": {
            "dahil": r"duş teknesi|duş kabini|küvet|boy küveti|oturmalı küvet|akrilik.*küvet",
            "haric": r"batarya|musluk|panel",
            "varsayilan_birim": "Ad",
            "varsayilan_fiyat": 1500.0
        },
        "duvar_boyasi": {
            "dahil": r"iç cephe boya|silikonlu.*mat.*iç|duvar.*boya|yarı mat.*iç",
            "haric": r"sac|panel|galvaniz|trapez|ahşap|demir|çelik|metal|dış cephe|tavan",
            "varsayilan_birim": "m2",
            "varsayilan_fiyat": 185.0
        },
        "tavan_boyasi": {
            "dahil": r"tavan boya|tavan.*iki kat",
            "haric": r"dış cephe",
            "varsayilan_birim": "m2",
            "varsayilan_fiyat": 180.0
        },
        "boya": {
            "dahil": r"iç cephe boya|tavan boya|badana.*yapılması|silikonlu.*mat|plastik boya|saten boya|duvar.*boya",
            "haric": r"sac|panel|galvaniz|trapez|ahşap|demir|çelik|metal|dış cephe",
            "varsayilan_birim": "m2",
            "varsayilan_fiyat": 200.0
        },
        "badana": {
            "dahil": r"badana.*yapılması|kireç badana",
            "haric": r"dış cephe",
            "varsayilan_birim": "m2",
            "varsayilan_fiyat": 210.0
        },
        "alci": {
            "dahil": r"alçı.*levha|alçı.*blok|asma tavan|kartonpiyer",
            "haric": None,
            "varsayilan_birim": "m2",
            "varsayilan_fiyat": 150.0
        },
        "kapi": {
            "dahil": r"iç kapı|dış kapı|kapı.*montaj",
            "haric": r"pencere|doğrama",
            "varsayilan_birim": "Ad",
            "varsayilan_fiyat": 2000.0
        },
        "pencere": {
            "dahil": r"pencere|pvc.*doğrama|alüminyum.*doğrama",
            "haric": r"kapı",
            "varsayilan_birim": "m2",
            "varsayilan_fiyat": 1500.0
        },
        "parke": {
            "dahil": r"laminat parke|parke döşeme|ahşap parke|masif parke",
            "haric": r"taşı|taþý|beton|çimento|granit|andezit|bazalt|kaldırım",
            "varsayilan_birim": "m2",
            "varsayilan_fiyat": 490.0
        },
        "laminat": {
            "dahil": r"laminat parke|laminat.*döşeme",
            "haric": r"mdf|levha|kapı",
            "varsayilan_birim": "m2",
            "varsayilan_fiyat": 490.0
        },
    }
    
    SECIM_GEREKTIREN_KALEMLER = ["musluk", "mutfak_dolabi", "lavabo", "klozet", "dus", "kapi", "pencere", "boya", "duvar_boyasi", "tavan_boyasi", "seramik", "parke", "laminat"]
    
    ISCILIK_TAHMINLERI = {
        "seramik": 0.8,
        "musluk": 1.5,
        "tezgah": 2.0,
        "mutfak_dolabi": 2.5,
        "priz": 1.0,
        "elektrik": 0.5,
        "lavabo": 1.5,
        "klozet": 2.0,
        "dus": 3.0,
        "boya": 0.15,
        "duvar_boyasi": 0.15,
        "tavan_boyasi": 0.12,
        "badana": 0.1,
        "alci": 0.5,
        "kapi": 2.0,
        "pencere": 1.5,
        "parke": 0.4,
        "laminat": 0.3,
    }

class TadilatAsistani:
    def __init__(self, csv_path: str):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.df = self._yukle_csv(csv_path)
        self.usta_saat_ucreti = 250.0
        self.chat_history = []
        self.kullanici_secimleri = {} 
        self.son_isler = []  
        
        self._urun_onbellegi = self._olustur_urun_onbellegi()
        
    def _yukle_csv(self, csv_path: str) -> pd.DataFrame:
        df = pd.read_csv(csv_path, sep=';', encoding='latin-1')
        df.columns = ['Kategori', 'Poz_No', 'Tanim', 'Birim', 'Fiyat']
        df['Fiyat'] = pd.to_numeric(df['Fiyat'], errors='coerce').fillna(0)
        return df
    
    def _olustur_urun_onbellegi(self) -> Dict[str, pd.DataFrame]:
        onbellek = {}
        for kategori, desen_bilgi in KategoriEslestirici.KATEGORI_DESENLERI.items():
            dahil_pattern = desen_bilgi["dahil"]
            haric_pattern = desen_bilgi.get("haric")
            
            filtre = self.df[self.df['Tanim'].str.contains(dahil_pattern, case=False, na=False, regex=True)]
            if haric_pattern:
                filtre = filtre[~filtre['Tanim'].str.contains(haric_pattern, case=False, na=False, regex=True)]
            filtre = filtre[filtre['Fiyat'] > 0]
            onbellek[kategori] = filtre
        return onbellek
    
    def _bul_urunler(self, kalem: str) -> Tuple[pd.DataFrame, str, Dict]:
        kalem_lower = kalem.lower().replace("_", " ")
        
        for kategori, desen_bilgi in KategoriEslestirici.KATEGORI_DESENLERI.items():
            kategori_normalized = kategori.replace("_", " ")
            if kategori_normalized in kalem_lower or kalem_lower in kategori_normalized:
                urunler = self._urun_onbellegi.get(kategori, pd.DataFrame())
                return urunler, kategori, desen_bilgi
        
        for kategori, desen_bilgi in KategoriEslestirici.KATEGORI_DESENLERI.items():
            dahil_words = desen_bilgi["dahil"].replace("|", " ").replace(".*", " ").replace("(?!.*", "").replace(")", "").split()
            if any(word.lower() in kalem_lower for word in dahil_words if len(word) > 3):
                urunler = self._urun_onbellegi.get(kategori, pd.DataFrame())
                return urunler, kategori, desen_bilgi
        
        filtre = self.df[self.df['Tanim'].str.contains(kalem, case=False, na=False)]
        filtre = filtre[filtre['Fiyat'] > 0]
        
        varsayilan_bilgi = {
            "dahil": kalem,
            "haric": None,
            "varsayilan_birim": "Ad",
            "varsayilan_fiyat": 0
        }
        return filtre, "genel", varsayilan_bilgi

    def _urun_secenekleri_olustur(self, urunler: pd.DataFrame, max_secenek: int = 5) -> List[Dict]:
        if urunler.empty:
            return []
        
        urunler_sirali = urunler.sort_values('Fiyat')
        secenekler = []
        fiyatlar = urunler_sirali['Fiyat'].unique()
        
        if len(fiyatlar) >= 3:
            alt = urunler_sirali[urunler_sirali['Fiyat'] <= fiyatlar[len(fiyatlar)//3]].head(2)
            orta = urunler_sirali[(urunler_sirali['Fiyat'] > fiyatlar[len(fiyatlar)//3]) & 
                                  (urunler_sirali['Fiyat'] <= fiyatlar[2*len(fiyatlar)//3])].head(2)
            ust = urunler_sirali[urunler_sirali['Fiyat'] > fiyatlar[2*len(fiyatlar)//3]].head(1)
            
            for df in [alt, orta, ust]:
                for _, row in df.iterrows():
                    kisa_isim = self._kisa_isim_olustur(row['Tanim'])
                    secenekler.append({
                        "poz_no": str(row['Poz_No']),
                        "tanim": row['Tanim'],
                        "kisa_isim": kisa_isim,
                        "fiyat": row['Fiyat'],
                        "birim": row['Birim'] if pd.notna(row['Birim']) else "Ad"
                    })
        else:
            for _, row in urunler_sirali.head(max_secenek).iterrows():
                kisa_isim = self._kisa_isim_olustur(row['Tanim'])
                secenekler.append({
                    "poz_no": str(row['Poz_No']),
                    "tanim": row['Tanim'],
                    "kisa_isim": kisa_isim,
                    "fiyat": row['Fiyat'],
                    "birim": row['Birim'] if pd.notna(row['Birim']) else "Ad"
                })
        
        return secenekler[:max_secenek]
    
    def _kisa_isim_olustur(self, tanim: str) -> str:
        if pd.isna(tanim):
            return "Standart"
        
        tanim = str(tanim)
        
        
        if 'laminat' in tanim.lower() or 'parke' in tanim.lower():
            if 'AC1' in tanim: return "Ekonomik Laminat (AC1)"
            if 'AC3' in tanim: return "Standart Laminat (AC3)"
            if 'AC4' in tanim: return "Dayanıklı Laminat (AC4)"
            if 'AC5' in tanim: return "Premium Laminat (AC5)"
            return "Laminat Parke"
        
        
        if 'karo' in tanim.lower() or 'seramik' in tanim.lower() or 'fayans' in tanim.lower():
            boyut = ""
            if '60' in tanim: boyut = "60cm "
            elif '45' in tanim: boyut = "45cm "
            elif '40' in tanim: boyut = "40cm "
            elif '33' in tanim or '30' in tanim: boyut = "30cm "
            elif '20' in tanim: boyut = "20cm "
            
            tip = "Yer" if 'yer' in tanim.lower() else "Duvar"
            renk = "Renkli" if 'renkli' in tanim.lower() else "Beyaz"
            return f"{boyut}{tip} Karosu ({renk})"
        
        
        if 'musluk' in tanim.lower() or 'batarya' in tanim.lower():
            if 'eviye' in tanim.lower(): return "Eviye Bataryası"
            if 'lavabo' in tanim.lower(): return "Lavabo Bataryası"
            if 'banyo' in tanim.lower(): return "Banyo Bataryası"
            if 'duş' in tanim.lower() or 'duþ' in tanim.lower(): return "Duş Bataryası"
            if 'tek kumanda' in tanim.lower(): return "Tek Kumandalı Batarya"
            if 'çift kumanda' in tanim.lower(): return "Çift Kumandalı Batarya"
            if 'ara musluk' in tanim.lower(): return "Ara Musluk"
            return "Standart Musluk"
        
        
        if 'dolap' in tanim.lower() or 'dolabı' in tanim.lower():
            if 'tezgah altı' in tanim.lower() or 'tezgah altý' in tanim.lower(): 
                return "Alt Dolap (Tezgah Altı)"
            if 'tezgah üstü' in tanim.lower(): 
                return "Üst Dolap (Asma)"
            return "Mutfak Dolabı"
        
        
        if 'lavabo' in tanim.lower():
            if 'oval' in tanim.lower(): return "Oval Lavabo"
            if 'kare' in tanim.lower(): return "Kare Lavabo"
            boyut_match = re.search(r'(\d+)x(\d+)', tanim)
            if boyut_match:
                return f"Lavabo ({boyut_match.group(1)}x{boyut_match.group(2)} cm)"
            return "Standart Lavabo"
        
        
        if 'klozet' in tanim.lower() or 'hela' in tanim.lower() or 'tuvalet' in tanim.lower():
            if 'asma' in tanim.lower(): return "Asma Klozet"
            if 'gömme rezervuar' in tanim.lower(): return "Gömme Rezervuarlı Klozet"
            if 'alafranga' in tanim.lower(): return "Alafranga Klozet"
            if 'alaturka' in tanim.lower(): return "Alaturka Tuvalet"
            return "Standart Klozet"
        
        
        if 'küvet' in tanim.lower() or 'duş' in tanim.lower() or 'duþ' in tanim.lower():
            if 'oturmalı' in tanim.lower() or 'oturmalý' in tanim.lower(): return "Oturmalı Küvet"
            if 'boy' in tanim.lower(): return "Boy Küveti"
            if 'akrilik' in tanim.lower(): return "Akrilik Küvet"
            return "Standart Küvet"
        
        
        if 'boya' in tanim.lower():
            if 'tavan' in tanim.lower(): return "Tavan Boyası"
            if 'silikonlu' in tanim.lower() and 'mat' in tanim.lower(): return "Silikonlu Mat Boya"
            if 'ipek mat' in tanim.lower() or 'ipeksi' in tanim.lower(): return "İpek Mat Boya"
            if 'yarı mat' in tanim.lower() or 'yarý mat' in tanim.lower(): return "Yarı Mat Boya"
            if 'antibakteriyel' in tanim.lower(): return "Antibakteriyel Boya"
            return "İç Cephe Boyası"
        
        
        if 'priz' in tanim.lower():
            if 'güvenlik' in tanim.lower(): return "Topraklı Priz"
            return "Standart Priz"
        
        return tanim[:30] + "..." if len(tanim) > 30 else tanim

    def _hesapla_ortalama_fiyat(self, urunler: pd.DataFrame) -> Tuple[float, float, float]:
        if urunler.empty:
            return 0, 0, 0
        fiyatlar = urunler[urunler['Fiyat'] > 0]['Fiyat']
        if fiyatlar.empty:
            return 0, 0, 0
        return fiyatlar.mean(), fiyatlar.min(), fiyatlar.max()

    def _kategori_listesi_olustur(self) -> str:
        kategoriler = []
        for kategori, urunler in self._urun_onbellegi.items():
            if not urunler.empty:
                ort, min_, max_ = self._hesapla_ortalama_fiyat(urunler)
                desen_bilgi = KategoriEslestirici.KATEGORI_DESENLERI.get(kategori, {})
                birim = desen_bilgi.get("varsayilan_birim", "Ad")
                kategoriler.append(f"- {kategori}: {len(urunler)} ürün, {min_:.0f}-{max_:.0f} TL/{birim}")
        return "\n".join(kategoriler)

    def llm_islem_belirle(self, kullanici_mesaji: str) -> Dict:
        self.chat_history.append({"role": "user", "content": kullanici_mesaji})
        
        kategori_bilgisi = self._kategori_listesi_olustur()
        
        system_prompt = f"""
Sen profesyonel bir inşaat maliyet uzmanısın.

GÖREVİN: Kullanıcının tadilat isteklerini analiz etmek ve fiyat tahmini için gerekli bilgileri toplamak.

KATEGORİLER:
{kategori_bilgisi}

ÖNEMLİ: "duvar_boyasi" ve "tavan_boyasi" AYRI kategorilerdir. Kullanıcı sadece "boya" derse hangisini istediğini sor.

KURALLAR:
1. Miktar (m2 veya adet) belirtilmediyse sor.
2. Oda/mekan belirtilmediyse sor.
3. "boya" denildiğinde duvar mı tavan mı sor.
4. Bilgiler tamamsa işleri listele.

ÇIKTI (JSON):
{{
    "durum": "eksik_bilgi" | "hazir",
    "cevap": "Mesaj",
    "isler": [
        {{"kalem": "duvar_boyasi", "oda": "salon", "miktar": 60, "birim": "m2", "tahmini_saat": 9}}
    ]
}}

Kalem isimleri: seramik, musluk, tezgah, mutfak_dolabi, priz, elektrik, lavabo, klozet, dus, duvar_boyasi, tavan_boyasi, boya, badana, alci, kapi, pencere, parke, laminat
"""

        messages = [{"role": "system", "content": system_prompt}] + self.chat_history

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            yanit_json = json.loads(completion.choices[0].message.content)
            self.chat_history.append({"role": "assistant", "content": yanit_json.get('cevap', '')})
            
            
            if yanit_json.get('isler'):
                self.son_isler = yanit_json['isler']
            
            return yanit_json
            
        except Exception as e:
            return {
                "durum": "eksik_bilgi",
                "cevap": f"Bir hata oluştu, lütfen tekrar deneyin: {str(e)}",
                "isler": []
            }

    def fiyatlandir(self, isler: List[Dict]) -> Tuple[List[FiyatSonucu], float, float, List[Dict]]:
        rapor = []
        toplam_maliyet = 0
        toplam_sure = 0
        secim_gereken_kalemler = []

        for item in isler:
            kalem = item.get('kalem', '')
            oda = item.get('oda', 'genel')
            
            
            miktar = item.get('miktar', 1)
            if isinstance(miktar, str):
                try:
                    miktar = float(miktar.replace(',', '.').replace('m2', '').replace('m²', '').strip())
                except:
                    miktar = 1
            miktar = float(miktar) if miktar else 1
            
            tahmini_saat = item.get('tahmini_saat', 0)
            if isinstance(tahmini_saat, str):
                try:
                    tahmini_saat = float(tahmini_saat)
                except:
                    tahmini_saat = 0
            
            secim_gerekli = kalem in KategoriEslestirici.SECIM_GEREKTIREN_KALEMLER
            
            urunler, kategori, desen_bilgi = self._bul_urunler(kalem)
            
            
            if tahmini_saat <= 0:
                iscilik_orani = KategoriEslestirici.ISCILIK_TAHMINLERI.get(kategori, 1.0)
                tahmini_saat = miktar * iscilik_orani
            
            
            secim_key = f"{kalem}_{oda}"
            kullanici_secimi = self.kullanici_secimleri.get(secim_key)
            
            birim_fiyat = 0
            not_ = None
            
            if kullanici_secimi:
                birim_fiyat = kullanici_secimi['fiyat']
                not_ = f"✅ Seçtiğiniz ürün fiyatı uygulandı"
            elif urunler.empty:
                varsayilan_fiyat = desen_bilgi.get("varsayilan_fiyat", 0)
                if varsayilan_fiyat > 0:
                    birim_fiyat = varsayilan_fiyat
                    not_ = f"ℹ️ Varsayılan fiyat kullanıldı"
            elif secim_gerekli and len(urunler) > 1:
                
                ort_fiyat, min_fiyat, max_fiyat = self._hesapla_ortalama_fiyat(urunler)
                birim_fiyat = ort_fiyat
                
                secenekler = self._urun_secenekleri_olustur(urunler)
                secim_gereken_kalemler.append({
                    "kalem": kalem,
                    "oda": oda,
                    "miktar": miktar,
                    "secenekler": secenekler,
                    "ortalama_fiyat": ort_fiyat,
                    "min_fiyat": min_fiyat,
                    "max_fiyat": max_fiyat
                })
                
                not_ = f"💡 Ortalama fiyat ({min_fiyat:.0f}-{max_fiyat:.0f} TL). Seçim yapabilirsiniz."
            else:
                if not urunler.empty:
                    birim_fiyat = urunler['Fiyat'].median()

            malzeme_maliyeti = birim_fiyat * miktar
            iscilik_maliyeti = tahmini_saat * self.usta_saat_ucreti
            
            toplam_maliyet += (malzeme_maliyeti + iscilik_maliyeti)
            toplam_sure += tahmini_saat
            
            rapor.append(FiyatSonucu(
                detay=f"{oda.upper()} - {kalem}: {malzeme_maliyeti:,.2f} TL Malzeme + {iscilik_maliyeti:,.2f} TL İşçilik",
                malzeme_maliyeti=malzeme_maliyeti,
                iscilik_maliyeti=iscilik_maliyeti,
                sure=tahmini_saat,
                not_=not_
            ))
            
        return rapor, toplam_maliyet, toplam_sure, secim_gereken_kalemler

    def sifirla(self):
        self.chat_history = []
        self.kullanici_secimleri = {}
        self.son_isler = []
