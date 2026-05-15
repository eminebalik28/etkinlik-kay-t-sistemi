import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="eventpro.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Kullanıcılar
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id INTEGER PRIMARY KEY,
                kadi TEXT UNIQUE,
                sifre TEXT,
                rol TEXT
            )
        """)

        # Etkinlikler
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS etkinlikler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT,
                kategori TEXT,
                tarih TEXT,
                saat TEXT,
                konum TEXT,
                kapasite INTEGER,
                katilimci_sayisi INTEGER DEFAULT 0,
                durum TEXT DEFAULT 'Aktif',
                fiyat_sahne_on_yetiskin REAL DEFAULT 0,
                fiyat_sahne_on_ogrenci REAL DEFAULT 0,
                fiyat_sahne_arka_yetiskin REAL DEFAULT 0,
                fiyat_sahne_arka_ogrenci REAL DEFAULT 0
            )
        """)

        # Rezervasyonlar (Bilet)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rezervasyonlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etkinlik_id INTEGER,
                kullanici_adi TEXT,
                rezervasyon_tarihi TEXT,
                bilet_kodu TEXT UNIQUE,
                koltuk_tipi TEXT DEFAULT 'Sahne Önü',
                bilet_kategorisi TEXT DEFAULT 'Yetişkin',
                fiyat REAL DEFAULT 0,
                FOREIGN KEY(etkinlik_id) REFERENCES etkinlikler(id)
            )
        """)

        # Favoriler
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS favoriler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etkinlik_id INTEGER,
                kullanici_adi TEXT,
                UNIQUE(etkinlik_id, kullanici_adi)
            )
        """)

        # --- Migration: Eski DB'ye eksik sütunları ekle ---
        self._migrate()

        # Varsayılan admin
        self.cursor.execute("INSERT OR IGNORE INTO kullanicilar (kadi, sifre, rol) VALUES ('admin', 'admin123', 'admin')")

        # Örnek etkinlikler
        # Örnek etkinlikler (ad, kategori, tarih, saat, konum, kapasite, s_on_yet, s_on_ogr, s_arka_yet, s_arka_ogr)
        ornek = [
            ("TechSummit 2025", "Teknoloji", "15-06-2025", "10:00", "İstanbul Kongre Merkezi", 500, 750, 450, 400, 250),
            ("Jazz Gecesi", "Müzik", "20-06-2025", "20:00", "Babylon İstanbul", 200, 350, 200, 200, 120),
            ("Startup Zirvesi", "İş Dünyası", "25-06-2025", "09:00", "Zorlu PSM", 300, 600, 350, 350, 200),
            ("Yoga Festivali", "Sağlık", "01-07-2025", "08:00", "Maçka Parkı", 150, 150, 80, 100, 60),
            ("Fotoğraf Atölyesi", "Sanat", "05-07-2025", "14:00", "SALT Galata", 50, 250, 150, 150, 90),
            ("Yapay Zeka Konferansı", "Teknoloji", "10-07-2025", "09:30", "Sabancı Üniversitesi", 400, 500, 300, 300, 180),
        ]
        for e in ornek:
            self.cursor.execute(
                "INSERT OR IGNORE INTO etkinlikler (ad, kategori, tarih, saat, konum, kapasite, fiyat_sahne_on_yetiskin, fiyat_sahne_on_ogrenci, fiyat_sahne_arka_yetiskin, fiyat_sahne_arka_ogrenci) VALUES (?,?,?,?,?,?,?,?,?,?)", e
            )

        self.conn.commit()

    def _migrate(self):
        """Mevcut veritabanına eksik sütunları ekler (eski DB uyumluluğu)."""
        # etkinlikler tablosu için yeni fiyat sütunları
        etk_yeni_sutunlar = [
            ("fiyat_sahne_on_yetiskin",  "REAL DEFAULT 0"),
            ("fiyat_sahne_on_ogrenci",   "REAL DEFAULT 0"),
            ("fiyat_sahne_arka_yetiskin","REAL DEFAULT 0"),
            ("fiyat_sahne_arka_ogrenci", "REAL DEFAULT 0"),
        ]
        self.cursor.execute("PRAGMA table_info(etkinlikler)")
        mevcut_etk = {row[1] for row in self.cursor.fetchall()}
        for sutun, tanim in etk_yeni_sutunlar:
            if sutun not in mevcut_etk:
                self.cursor.execute(f"ALTER TABLE etkinlikler ADD COLUMN {sutun} {tanim}")

        # rezervasyonlar tablosu için yeni sütunlar
        rez_yeni_sutunlar = [
            ("koltuk_tipi",       "TEXT DEFAULT 'Sahne Önü'"),
            ("bilet_kategorisi",  "TEXT DEFAULT 'Yetişkin'"),
            ("fiyat",             "REAL DEFAULT 0"),
        ]
        self.cursor.execute("PRAGMA table_info(rezervasyonlar)")
        mevcut_rez = {row[1] for row in self.cursor.fetchall()}
        for sutun, tanim in rez_yeni_sutunlar:
            if sutun not in mevcut_rez:
                self.cursor.execute(f"ALTER TABLE rezervasyonlar ADD COLUMN {sutun} {tanim}")

        self.conn.commit()

    # --- DASHBOARD ---
    def istatistikleri_getir(self):
        self.cursor.execute("SELECT COUNT(*) FROM etkinlikler")
        toplam = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM rezervasyonlar")
        toplam_bilet = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM favoriler")
        toplam_fav = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(DISTINCT kullanici_adi) FROM rezervasyonlar")
        toplam_katilimci = self.cursor.fetchone()[0]
        return toplam, toplam_bilet, toplam_fav, toplam_katilimci

    def kategori_dagilimi_getir(self):
        self.cursor.execute("SELECT kategori, COUNT(*) FROM etkinlikler GROUP BY kategori")
        return self.cursor.fetchall()

    def yaklasan_etkinlikler(self):
        self.cursor.execute("SELECT ad, tarih, saat, konum FROM etkinlikler ORDER BY tarih LIMIT 5")
        return self.cursor.fetchall()

    # --- ETKİNLİK ---
    def etkinlik_ara(self, metin):
        q = "SELECT id, ad, kategori, tarih, saat, konum, kapasite, katilimci_sayisi, durum, fiyat_sahne_on_yetiskin, fiyat_sahne_on_ogrenci, fiyat_sahne_arka_yetiskin, fiyat_sahne_arka_ogrenci FROM etkinlikler WHERE (ad LIKE ? OR kategori LIKE ? OR konum LIKE ?)"
        self.cursor.execute(q, [f"%{metin}%"]*3)
        return self.cursor.fetchall()

    def etkinlikleri_getir(self):
        self.cursor.execute("SELECT id, ad, kategori, tarih, saat, konum, kapasite, katilimci_sayisi, durum, fiyat_sahne_on_yetiskin, fiyat_sahne_on_ogrenci, fiyat_sahne_arka_yetiskin, fiyat_sahne_arka_ogrenci FROM etkinlikler")
        return self.cursor.fetchall()

    def etkinlik_ekle(self, ad, kategori, tarih, saat, konum, kapasite,
                      fiyat_son_yet=0, fiyat_son_ogr=0, fiyat_sarka_yet=0, fiyat_sarka_ogr=0):
        self.cursor.execute(
            "INSERT INTO etkinlikler (ad, kategori, tarih, saat, konum, kapasite, fiyat_sahne_on_yetiskin, fiyat_sahne_on_ogrenci, fiyat_sahne_arka_yetiskin, fiyat_sahne_arka_ogrenci) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (ad, kategori, tarih, saat, konum, kapasite, fiyat_son_yet, fiyat_son_ogr, fiyat_sarka_yet, fiyat_sarka_ogr)
        )
        self.conn.commit()

    def etkinlik_sil(self, etkinlik_id):
        self.cursor.execute("DELETE FROM rezervasyonlar WHERE etkinlik_id=?", (etkinlik_id,))
        self.cursor.execute("DELETE FROM favoriler WHERE etkinlik_id=?", (etkinlik_id,))
        self.cursor.execute("DELETE FROM etkinlikler WHERE id=?", (etkinlik_id,))
        self.conn.commit()

    def etkinlik_iptal_et(self, etkinlik_id):
        self.cursor.execute("UPDATE etkinlikler SET durum='İptal' WHERE id=?", (etkinlik_id,))
        self.conn.commit()

    # --- REZERVASYON / BİLET ---
    def rezervasyon_yap(self, etkinlik_id, kullanici_adi, koltuk_tipi="Sahne Önü", bilet_kategorisi="Yetişkin", fiyat=0):
        # Dolu mu kontrol
        self.cursor.execute("SELECT kapasite, katilimci_sayisi FROM etkinlikler WHERE id=?", (etkinlik_id,))
        row = self.cursor.fetchone()
        if not row or row[1] >= row[0]:
            return False, "Etkinlik dolu!"
        # Zaten kayıtlı mı
        self.cursor.execute("SELECT id FROM rezervasyonlar WHERE etkinlik_id=? AND kullanici_adi=?", (etkinlik_id, kullanici_adi))
        if self.cursor.fetchone():
            return False, "Zaten kayıtlısınız!"
        bilet_kodu = f"EVT-{etkinlik_id}-{kullanici_adi.upper()}-{datetime.now().strftime('%H%M%S')}"
        tarih = datetime.now().strftime("%d-%m-%Y %H:%M")
        self.cursor.execute(
            "INSERT INTO rezervasyonlar (etkinlik_id, kullanici_adi, rezervasyon_tarihi, bilet_kodu, koltuk_tipi, bilet_kategorisi, fiyat) VALUES (?,?,?,?,?,?,?)",
            (etkinlik_id, kullanici_adi, tarih, bilet_kodu, koltuk_tipi, bilet_kategorisi, fiyat)
        )
        self.cursor.execute("UPDATE etkinlikler SET katilimci_sayisi = katilimci_sayisi + 1 WHERE id=?", (etkinlik_id,))
        self.conn.commit()
        return True, bilet_kodu

    def rezervasyon_iptal(self, etkinlik_id, kullanici_adi):
        self.cursor.execute("DELETE FROM rezervasyonlar WHERE etkinlik_id=? AND kullanici_adi=?", (etkinlik_id, kullanici_adi))
        self.cursor.execute("UPDATE etkinlikler SET katilimci_sayisi = katilimci_sayisi - 1 WHERE id=?", (etkinlik_id,))
        self.conn.commit()

    def kullanici_rezervasyonlari(self, kadi):
        q = """SELECT e.id, e.ad, e.tarih, e.saat, e.konum, r.bilet_kodu, r.koltuk_tipi, r.bilet_kategorisi, r.fiyat
               FROM etkinlikler e JOIN rezervasyonlar r ON e.id = r.etkinlik_id
               WHERE r.kullanici_adi = ?"""
        self.cursor.execute(q, (kadi,))
        return self.cursor.fetchall()

    # --- KATILIMCİ YÖNETİMİ (Admin) ---
    def etkinlik_katilimcilari(self, etkinlik_id):
        q = """SELECT r.kullanici_adi, r.rezervasyon_tarihi, r.bilet_kodu
               FROM rezervasyonlar r WHERE r.etkinlik_id = ?"""
        self.cursor.execute(q, (etkinlik_id,))
        return self.cursor.fetchall()

    def tum_rezervasyonlar(self):
        q = """SELECT e.ad, r.kullanici_adi, r.rezervasyon_tarihi, r.bilet_kodu, r.koltuk_tipi, r.bilet_kategorisi, r.fiyat
               FROM rezervasyonlar r JOIN etkinlikler e ON r.etkinlik_id = e.id
               ORDER BY r.rezervasyon_tarihi DESC"""
        self.cursor.execute(q)
        return self.cursor.fetchall()

    # --- FAVORİ ---
    def favori_degistir(self, etkinlik_id, kullanici_adi):
        self.cursor.execute("SELECT id FROM favoriler WHERE etkinlik_id=? AND kullanici_adi=?", (etkinlik_id, kullanici_adi))
        if self.cursor.fetchone():
            self.cursor.execute("DELETE FROM favoriler WHERE etkinlik_id=? AND kullanici_adi=?", (etkinlik_id, kullanici_adi))
        else:
            self.cursor.execute("INSERT INTO favoriler (etkinlik_id, kullanici_adi) VALUES (?,?)", (etkinlik_id, kullanici_adi))
        self.conn.commit()

    def favori_etkinlikler(self, kadi):
        q = """SELECT e.id, e.ad, e.kategori, e.tarih, e.konum
               FROM etkinlikler e JOIN favoriler f ON e.id = f.etkinlik_id
               WHERE f.kullanici_adi = ?"""
        self.cursor.execute(q, (kadi,))
        return self.cursor.fetchall()

    # --- GİRİŞ / KAYIT ---
    def giris_kontrol(self, kadi, sifre, rol):
        self.cursor.execute("SELECT * FROM kullanicilar WHERE kadi=? AND sifre=? AND rol=?", (kadi, sifre, rol))
        return self.cursor.fetchone() is not None

    def kayit_ol(self, kadi, sifre):
        try:
            self.cursor.execute("INSERT INTO kullanicilar (kadi, sifre, rol) VALUES (?,?,'uye')", (kadi, sifre))
            self.conn.commit()
            return True
        except:
            return False

    # --- KULLANICI AYARLARI ---
    def kullanici_adi_degistir(self, eski_kadi, yeni_kadi, sifre):
        """Kullanıcı adını günceller; tüm ilişkili kayıtları da günceller."""
        # Şifre doğrulama
        self.cursor.execute("SELECT rol FROM kullanicilar WHERE kadi=? AND sifre=?", (eski_kadi, sifre))
        row = self.cursor.fetchone()
        if not row:
            return False, "Şifre yanlış!"
        # Yeni ad kullanımda mı?
        self.cursor.execute("SELECT id FROM kullanicilar WHERE kadi=?", (yeni_kadi,))
        if self.cursor.fetchone():
            return False, "Bu kullanıcı adı zaten kullanımda!"
        try:
            self.cursor.execute("UPDATE kullanicilar SET kadi=? WHERE kadi=?", (yeni_kadi, eski_kadi))
            self.cursor.execute("UPDATE rezervasyonlar SET kullanici_adi=? WHERE kullanici_adi=?", (yeni_kadi, eski_kadi))
            self.cursor.execute("UPDATE favoriler SET kullanici_adi=? WHERE kullanici_adi=?", (yeni_kadi, eski_kadi))
            self.conn.commit()
            return True, "Kullanıcı adı başarıyla güncellendi!"
        except Exception as e:
            return False, str(e)

    def sifre_degistir(self, kadi, eski_sifre, yeni_sifre):
        self.cursor.execute("SELECT id FROM kullanicilar WHERE kadi=? AND sifre=?", (kadi, eski_sifre))
        if not self.cursor.fetchone():
            return False, "Mevcut şifre yanlış!"
        self.cursor.execute("UPDATE kullanicilar SET sifre=? WHERE kadi=?", (yeni_sifre, kadi))
        self.conn.commit()
        return True, "Şifre başarıyla güncellendi!"