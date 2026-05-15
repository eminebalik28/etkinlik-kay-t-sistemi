class Etkinlik:
    def __init__(self, id, ad, kategori, tarih, saat, konum, kapasite, katilimci_sayisi, durum):
        self.id = id
        self.ad = ad
        self.kategori = kategori
        self.tarih = tarih
        self.saat = saat
        self.konum = konum
        self.kapasite = kapasite
        self.katilimci_sayisi = katilimci_sayisi
        self.durum = durum

class Kullanici:
    def __init__(self, id, kadi, rol):
        self.id = id
        self.kadi = kadi
        self.rol = rol

class Rezervasyon:
    def __init__(self, id, etkinlik_id, kullanici_adi, rezervasyon_tarihi, bilet_kodu):
        self.id = id
        self.etkinlik_id = etkinlik_id
        self.kullanici_adi = kullanici_adi
        self.rezervasyon_tarihi = rezervasyon_tarihi
        self.bilet_kodu = bilet_kodu