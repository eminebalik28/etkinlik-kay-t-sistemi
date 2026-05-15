from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QStackedWidget,
    QFrame, QDialog, QFormLayout, QComboBox,
    QSpinBox, QGridLayout, QScrollArea, QSizePolicy,
    QButtonGroup, QRadioButton, QGroupBox, QSizeGrip
)
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath
from tema import get_style, ACCENT_COLORS, DEFAULT_ACCENT

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

APP_NAME = "Biletim"

# Profil avatar renk seçenekleri
AVATAR_COLORS = {
    "🔴 Kırmızı":  "#f78166",
    "🔵 Mavi":     "#58a6ff",
    "🟢 Yeşil":    "#3fb950",
    "🟣 Mor":      "#d2a8ff",
    "🟠 Turuncu":  "#ffa657",
    "🩷 Pembe":    "#ff6ec7",
    "⚫ Koyu":     "#6e7681",
    "🟡 Sarı":     "#e3b341",
}
DEFAULT_AVATAR_COLOR = "🔴 Kırmızı"


# ─── AVATAR WİDGET ───────────────────────────────────────────────────
class AvatarWidget(QWidget):
    """Kullanıcı baş harfini daire içinde gösteren mini avatar."""
    def __init__(self, harf, renk="#f78166", parent=None):
        super().__init__(parent)
        self.harf = harf.upper() if harf else "?"
        self.renk = renk
        self.setFixedSize(36, 36)

    def set_renk(self, renk):
        self.renk = renk
        self.update()

    def set_harf(self, harf):
        self.harf = harf.upper() if harf else "?"
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(1, 1, 34, 34)
        p.fillPath(path, QColor(self.renk))
        p.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 14, QFont.Bold)
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignCenter, self.harf)


# ─── DASHBOARD KARTI ────────────────────────────────────────────────
class DashCard(QFrame):
    def __init__(self, icon, baslik, deger, renk):
        super().__init__()
        self.setObjectName("card")
        self.setFixedHeight(110)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)

        top = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet(f"font-size: 28px; background: transparent; border: none;")
        self.lbl_val = QLabel(str(deger))
        self.lbl_val.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {renk}; background: transparent; border: none;")
        self.lbl_val.setAlignment(Qt.AlignRight)
        top.addWidget(lbl_icon)
        top.addStretch()
        top.addWidget(self.lbl_val)

        lbl_title = QLabel(baslik)
        lbl_title.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: 600; text-transform: uppercase; background: transparent; border: none;")
        lay.addLayout(top)
        lay.addWidget(lbl_title)


# ─── AYARLAR DİYALOGU ────────────────────────────────────────────────
class AyarlarDialog(QDialog):
    theme_changed        = pyqtSignal(str)   # "dark" / "light"
    accent_changed       = pyqtSignal(str)   # renk adı
    name_changed         = pyqtSignal(str)   # yeni kullanıcı adı
    avatar_color_changed = pyqtSignal(str)   # avatar renk hex

    def __init__(self, db, kadi, current_theme, current_accent, current_avatar_color, parent=None):
        super().__init__(parent)
        self.db = db
        self.kadi = kadi
        self.current_theme        = current_theme
        self.current_accent       = current_accent
        self.current_avatar_color = current_avatar_color
        self.setWindowTitle(f"⚙️ {APP_NAME} — Hesap Ayarları")
        self.setMinimumSize(640, 700)
        self.resize(700, 760)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 32, 36, 32)
        root.setSpacing(18)

        # — Başlık
        lbl_title = QLabel(f"⚙️ Hesap Ayarları")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: 800;")
        root.addWidget(lbl_title)

        # — Kullanıcı Adı Değiştir
        grp_ad = QGroupBox("Kullanıcı Adı Değiştir")
        form_ad = QFormLayout(grp_ad)
        form_ad.setSpacing(12)
        self.txt_yeni_ad = QLineEdit()
        self.txt_yeni_ad.setPlaceholderText(f"Mevcut: {self.kadi}")
        self.txt_sifre_ad = QLineEdit()
        self.txt_sifre_ad.setPlaceholderText("Şifrenizi girin (doğrulama için)")
        self.txt_sifre_ad.setEchoMode(QLineEdit.Password)
        btn_ad = QPushButton("✅ Kaydet")
        btn_ad.setObjectName("primary_btn")
        btn_ad.clicked.connect(self._kadi_degistir)
        form_ad.addRow("Yeni Ad:", self.txt_yeni_ad)
        form_ad.addRow("Şifre:", self.txt_sifre_ad)
        form_ad.addRow(btn_ad)
        root.addWidget(grp_ad)

        # — Şifre Değiştir
        grp_sifre = QGroupBox("Şifre Değiştir")
        form_sifre = QFormLayout(grp_sifre)
        form_sifre.setSpacing(12)
        self.txt_eski_sifre = QLineEdit()
        self.txt_eski_sifre.setPlaceholderText("Mevcut şifre")
        self.txt_eski_sifre.setEchoMode(QLineEdit.Password)
        self.txt_yeni_sifre = QLineEdit()
        self.txt_yeni_sifre.setPlaceholderText("Yeni şifre")
        self.txt_yeni_sifre.setEchoMode(QLineEdit.Password)
        btn_sifre = QPushButton("✅ Şifreyi Güncelle")
        btn_sifre.setObjectName("primary_btn")
        btn_sifre.clicked.connect(self._sifre_degistir)
        form_sifre.addRow("Eski Şifre:", self.txt_eski_sifre)
        form_sifre.addRow("Yeni Şifre:", self.txt_yeni_sifre)
        form_sifre.addRow(btn_sifre)
        root.addWidget(grp_sifre)

        # — Görünüm
        grp_gorunum = QGroupBox("Görünüm")
        gorunum_lay = QVBoxLayout(grp_gorunum)
        gorunum_lay.setSpacing(14)

        # Koyu/Açık tema
        tema_lay = QHBoxLayout()
        self.radio_dark  = QRadioButton("🌙 Koyu Tema")
        self.radio_light = QRadioButton("☀️ Açık Tema")
        if self.current_theme == "dark":
            self.radio_dark.setChecked(True)
        else:
            self.radio_light.setChecked(True)
        self.radio_dark.toggled.connect(self._tema_sec)
        tema_lay.addWidget(self.radio_dark)
        tema_lay.addWidget(self.radio_light)
        tema_lay.addStretch()
        gorunum_lay.addLayout(tema_lay)

        # — Profil Fotoğrafı Rengi
        lbl_avatar = QLabel("Profil Fotoğrafı Rengi:")
        lbl_avatar.setStyleSheet("font-weight: 600; margin-top: 6px;")
        gorunum_lay.addWidget(lbl_avatar)

        avatar_preview_row = QHBoxLayout()
        self._avatar_preview = AvatarWidget(self.kadi[0] if self.kadi else "?", self.current_avatar_color)
        lbl_av_hint = QLabel("← Önizleme")
        lbl_av_hint.setStyleSheet("color: #8b949e; font-size: 11px;")
        avatar_preview_row.addWidget(self._avatar_preview)
        avatar_preview_row.addWidget(lbl_av_hint)
        avatar_preview_row.addStretch()
        gorunum_lay.addLayout(avatar_preview_row)

        avatar_grid = QGridLayout()
        avatar_grid.setSpacing(8)
        self._avatar_butonlari = {}
        for idx, (ad, hex_c) in enumerate(AVATAR_COLORS.items()):
            btn = QPushButton(ad)
            btn.setCheckable(True)
            btn.setChecked(hex_c == self.current_avatar_color)
            btn.setFixedHeight(38)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_c}20; border: 2px solid {hex_c};
                    border-radius: 8px; padding: 6px 10px; font-weight: 600;
                    color: {hex_c};
                }}
                QPushButton:checked {{
                    background-color: {hex_c}; color: #0d1117; border-color: {hex_c};
                }}
                QPushButton:hover {{ background-color: {hex_c}40; }}
            """)
            btn.clicked.connect(lambda ch, h=hex_c, a=ad: self._avatar_renk_sec(h, a))
            avatar_grid.addWidget(btn, idx // 4, idx % 4)
            self._avatar_butonlari[ad] = btn
        gorunum_lay.addLayout(avatar_grid)

        root.addWidget(grp_gorunum)

        # Kapat
        btn_kapat = QPushButton("Kapat")
        btn_kapat.setFixedHeight(42)
        btn_kapat.clicked.connect(self.accept)
        root.addWidget(btn_kapat)

    def _kadi_degistir(self):
        yeni = self.txt_yeni_ad.text().strip()
        sifre = self.txt_sifre_ad.text()
        if not yeni:
            QMessageBox.warning(self, "Hata", "Yeni kullanıcı adı boş olamaz!")
            return
        ok, msg = self.db.kullanici_adi_degistir(self.kadi, yeni, sifre)
        if ok:
            QMessageBox.information(self, "Başarılı ✅", msg)
            self.kadi = yeni
            self._avatar_preview.set_harf(yeni[0] if yeni else "?")
            self.name_changed.emit(yeni)
            self.txt_yeni_ad.clear()
            self.txt_sifre_ad.clear()
        else:
            QMessageBox.warning(self, "Hata", msg)

    def _sifre_degistir(self):
        eski = self.txt_eski_sifre.text()
        yeni = self.txt_yeni_sifre.text()
        if not yeni or len(yeni) < 4:
            QMessageBox.warning(self, "Hata", "Yeni şifre en az 4 karakter olmalı!")
            return
        ok, msg = self.db.sifre_degistir(self.kadi, eski, yeni)
        if ok:
            QMessageBox.information(self, "Başarılı ✅", msg)
            self.txt_eski_sifre.clear()
            self.txt_yeni_sifre.clear()
        else:
            QMessageBox.warning(self, "Hata", msg)

    def _tema_sec(self):
        t = "dark" if self.radio_dark.isChecked() else "light"
        self.current_theme = t
        self.theme_changed.emit(t)

    def _avatar_renk_sec(self, hex_c, ad):
        for a, btn in self._avatar_butonlari.items():
            btn.setChecked(a == ad)
        self._avatar_preview.set_renk(hex_c)
        self.current_avatar_color = hex_c
        self.avatar_color_changed.emit(hex_c)


# ─── ETKİNLİK EKLEME DİYALOGU ───────────────────────────────────────
class EtkinlikEkleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Etkinlik Ekle")
        self.setFixedSize(480, 580)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        lay = QFormLayout(self)
        lay.setContentsMargins(25, 25, 25, 25)
        lay.setSpacing(10)

        self.txt_ad = QLineEdit()
        self.txt_ad.setPlaceholderText("Etkinlik adı")
        self.cmb_kat = QComboBox()
        self.cmb_kat.addItems(["Teknoloji", "Müzik", "İş Dünyası", "Sağlık", "Sanat", "Spor", "Eğitim", "Diğer"])
        self.txt_tarih = QLineEdit()
        self.txt_tarih.setPlaceholderText("GG-AA-YYYY")
        self.txt_saat = QLineEdit()
        self.txt_saat.setPlaceholderText("SS:DD")
        self.txt_konum = QLineEdit()
        self.txt_konum.setPlaceholderText("Şehir, Mekan")
        self.spn_kap = QSpinBox()
        self.spn_kap.setRange(1, 10000)
        self.spn_kap.setValue(100)

        lay.addRow("Etkinlik Adı:", self.txt_ad)
        lay.addRow("Kategori:", self.cmb_kat)
        lay.addRow("Tarih:", self.txt_tarih)
        lay.addRow("Saat:", self.txt_saat)
        lay.addRow("Konum:", self.txt_konum)
        lay.addRow("Kapasite:", self.spn_kap)

        # Fiyat alanları
        from PyQt5.QtWidgets import QDoubleSpinBox
        lbl_fiyat = QLabel("— Bilet Fiyatları (₺) —")
        lbl_fiyat.setStyleSheet("font-weight: 700; margin-top: 8px; color: #8b949e;")
        lay.addRow(lbl_fiyat)

        self.spn_son_yet = QDoubleSpinBox(); self.spn_son_yet.setRange(0, 99999); self.spn_son_yet.setDecimals(2); self.spn_son_yet.setSuffix(" ₺"); self.spn_son_yet.setValue(200)
        self.spn_son_ogr = QDoubleSpinBox(); self.spn_son_ogr.setRange(0, 99999); self.spn_son_ogr.setDecimals(2); self.spn_son_ogr.setSuffix(" ₺"); self.spn_son_ogr.setValue(120)
        self.spn_sarka_yet = QDoubleSpinBox(); self.spn_sarka_yet.setRange(0, 99999); self.spn_sarka_yet.setDecimals(2); self.spn_sarka_yet.setSuffix(" ₺"); self.spn_sarka_yet.setValue(120)
        self.spn_sarka_ogr = QDoubleSpinBox(); self.spn_sarka_ogr.setRange(0, 99999); self.spn_sarka_ogr.setDecimals(2); self.spn_sarka_ogr.setSuffix(" ₺"); self.spn_sarka_ogr.setValue(70)

        lay.addRow("Sahne Önü – Yetişkin:", self.spn_son_yet)
        lay.addRow("Sahne Önü – Öğrenci:", self.spn_son_ogr)
        lay.addRow("Sahne Arkası – Yetişkin:", self.spn_sarka_yet)
        lay.addRow("Sahne Arkası – Öğrenci:", self.spn_sarka_ogr)

        btn_box = QHBoxLayout()
        btn_kaydet = QPushButton("✅ Kaydet")
        btn_kaydet.setObjectName("primary_btn")
        btn_iptal = QPushButton("İptal")
        btn_kaydet.clicked.connect(self.accept)
        btn_iptal.clicked.connect(self.reject)
        btn_box.addWidget(btn_iptal)
        btn_box.addWidget(btn_kaydet)
        lay.addRow(btn_box)

    def get_data(self):
        return (
            self.txt_ad.text(),
            self.cmb_kat.currentText(),
            self.txt_tarih.text(),
            self.txt_saat.text(),
            self.txt_konum.text(),
            self.spn_kap.value(),
            self.spn_son_yet.value(),
            self.spn_son_ogr.value(),
            self.spn_sarka_yet.value(),
            self.spn_sarka_ogr.value(),
        )


# ─── REZERVASYON DİYALOGU ────────────────────────────────────────────
class RezervasyanDialog(QDialog):
    """Koltuk tipi ve bilet kategorisi seçimi + fiyat özeti."""
    def __init__(self, etkinlik_data, parent=None):
        super().__init__(parent)
        # etkinlik_data: (id, ad, kat, tarih, saat, konum, kap, katil, durum,
        #                  son_yet, son_ogr, sarka_yet, sarka_ogr)
        self.etkinlik_data = etkinlik_data
        self.fiyatlar = {
            ("Sahne Önü",   "Yetişkin"): etkinlik_data[9],
            ("Sahne Önü",   "Öğrenci"):  etkinlik_data[10],
            ("Sahne Arkası","Yetişkin"): etkinlik_data[11],
            ("Sahne Arkası","Öğrenci"):  etkinlik_data[12],
        }
        self.setWindowTitle("🎫 Bilet Seçimi")
        self.setFixedSize(420, 420)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(16)

        # Etkinlik bilgisi
        lbl_baslik = QLabel(f"<b>{self.etkinlik_data[1]}</b>")
        lbl_baslik.setStyleSheet("font-size: 16px;")
        lay.addWidget(lbl_baslik)

        lbl_det = QLabel(f"📅 {self.etkinlik_data[3]}  ⏰ {self.etkinlik_data[4]}  📍 {self.etkinlik_data[5]}")
        lbl_det.setStyleSheet("color: #8b949e; font-size: 12px;")
        lbl_det.setWordWrap(True)
        lay.addWidget(lbl_det)

        # Koltuk tipi
        grp_koltuk = QGroupBox("Koltuk Tipi")
        koltuk_lay = QHBoxLayout(grp_koltuk)
        self.radio_son   = QRadioButton("🎭 Sahne Önü")
        self.radio_sarka = QRadioButton("🪑 Sahne Arkası")
        self.radio_son.setChecked(True)
        self.radio_son.toggled.connect(self._fiyat_guncelle)
        self.radio_sarka.toggled.connect(self._fiyat_guncelle)
        koltuk_lay.addWidget(self.radio_son)
        koltuk_lay.addWidget(self.radio_sarka)
        lay.addWidget(grp_koltuk)

        # Bilet kategorisi
        grp_kat = QGroupBox("Bilet Kategorisi")
        kat_lay = QHBoxLayout(grp_kat)
        self.radio_yetiskin = QRadioButton("👤 Yetişkin")
        self.radio_ogrenci  = QRadioButton("🎓 Öğrenci")
        self.radio_yetiskin.setChecked(True)
        self.radio_yetiskin.toggled.connect(self._fiyat_guncelle)
        self.radio_ogrenci.toggled.connect(self._fiyat_guncelle)
        kat_lay.addWidget(self.radio_yetiskin)
        kat_lay.addWidget(self.radio_ogrenci)
        lay.addWidget(grp_kat)

        # Fiyat özeti kartı
        fiyat_frame = QFrame()
        fiyat_frame.setObjectName("card")
        fiyat_lay = QVBoxLayout(fiyat_frame)
        fiyat_lay.setContentsMargins(16, 12, 16, 12)
        lbl_f_baslik = QLabel("Ücret")
        lbl_f_baslik.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: 700;")
        self.lbl_fiyat = QLabel("0 ₺")
        self.lbl_fiyat.setStyleSheet("font-size: 28px; font-weight: 800;")
        fiyat_lay.addWidget(lbl_f_baslik)
        fiyat_lay.addWidget(self.lbl_fiyat)
        lay.addWidget(fiyat_frame)

        self._fiyat_guncelle()

        # Butonlar
        btn_row = QHBoxLayout()
        btn_iptal = QPushButton("İptal")
        btn_onayla = QPushButton("✅ Rezervasyonu Onayla")
        btn_onayla.setObjectName("primary_btn")
        btn_iptal.clicked.connect(self.reject)
        btn_onayla.clicked.connect(self.accept)
        btn_row.addWidget(btn_iptal)
        btn_row.addWidget(btn_onayla)
        lay.addLayout(btn_row)

    def _fiyat_guncelle(self):
        k = self._get_koltuk()
        b = self._get_kategori()
        f = self.fiyatlar.get((k, b), 0)
        self.lbl_fiyat.setText(f"{f:,.2f} ₺")

    def _get_koltuk(self):
        return "Sahne Önü" if self.radio_son.isChecked() else "Sahne Arkası"

    def _get_kategori(self):
        return "Yetişkin" if self.radio_yetiskin.isChecked() else "Öğrenci"

    def get_secim(self):
        k = self._get_koltuk()
        b = self._get_kategori()
        f = self.fiyatlar.get((k, b), 0)
        return k, b, f


# ─── GİRİŞ EKRANI ────────────────────────────────────────────────────
class LoginWindow(QWidget):
    login_success = pyqtSignal(str)
    go_to_register = pyqtSignal()

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setStyleSheet(get_style("dark"))
        self.setWindowTitle(f"{APP_NAME} - Giriş")
        self.setFixedSize(1200, 800)
        self._build()

    def _build(self):
        root = QHBoxLayout(self)

        left = QFrame()
        left.setStyleSheet("background-color: #161b22; border: none; border-right: 1px solid #21262d;")
        left.setFixedWidth(480)
        left_lay = QVBoxLayout(left)
        left_lay.setAlignment(Qt.AlignCenter)
        lbl_logo = QLabel("🎫")
        lbl_logo.setStyleSheet("font-size: 72px; background: transparent;")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_brand = QLabel(APP_NAME)
        lbl_brand.setStyleSheet("font-size: 36px; font-weight: 800; color: #f78166; background: transparent;")
        lbl_brand.setAlignment(Qt.AlignCenter)
        lbl_sub = QLabel("Etkinlik & Bilet Yönetim Sistemi")
        lbl_sub.setStyleSheet("font-size: 14px; color: #8b949e; background: transparent;")
        lbl_sub.setAlignment(Qt.AlignCenter)
        left_lay.addWidget(lbl_logo)
        left_lay.addWidget(lbl_brand)
        left_lay.addWidget(lbl_sub)

        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setAlignment(Qt.AlignCenter)
        right_lay.setSpacing(10)

        lbl_hosgeldin = QLabel("Hoş Geldiniz")
        lbl_hosgeldin.setStyleSheet("font-size: 22px; font-weight: 700;")
        lbl_hosgeldin.setAlignment(Qt.AlignCenter)

        self.txt_kadi = QLineEdit()
        self.txt_kadi.setPlaceholderText("Kullanıcı Adı")
        self.txt_kadi.setFixedWidth(320)
        self.txt_sifre = QLineEdit()
        self.txt_sifre.setPlaceholderText("Şifre")
        self.txt_sifre.setEchoMode(QLineEdit.Password)
        self.txt_sifre.setFixedWidth(320)

        btn_uye = QPushButton("👤 Üye Girişi")
        btn_uye.setFixedWidth(320)
        btn_uye.setObjectName("primary_btn")
        btn_uye.clicked.connect(lambda: self._kontrol("uye"))
        btn_admin = QPushButton("🔑 Admin Girişi")
        btn_admin.setFixedWidth(320)
        btn_admin.clicked.connect(lambda: self._kontrol("admin"))
        btn_kayit = QPushButton("Hesabın yok mu? Kayıt Ol →")
        btn_kayit.setFixedWidth(320)
        btn_kayit.setStyleSheet("border: none; color: #f78166; background: transparent; font-weight: 600;")
        btn_kayit.clicked.connect(self.go_to_register.emit)

        for w in [lbl_hosgeldin, self.txt_kadi, self.txt_sifre, btn_uye, btn_admin, btn_kayit]:
            right_lay.addWidget(w, alignment=Qt.AlignCenter)

        root.addWidget(left)
        root.addWidget(right)

    def _kontrol(self, rol):
        if self.db.giris_kontrol(self.txt_kadi.text(), self.txt_sifre.text(), rol):
            self.login_success.emit(rol)
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış!")


# ─── KAYIT EKRANI ─────────────────────────────────────────────────────
class RegisterWindow(QWidget):
    go_to_login = pyqtSignal()

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setStyleSheet(get_style("dark"))
        self.setWindowTitle(f"{APP_NAME} - Kayıt Ol")
        self.setFixedSize(1200, 800)
        self._build()

    def _build(self):
        root = QHBoxLayout(self)

        left = QFrame()
        left.setStyleSheet("background-color: #161b22; border: none; border-right: 1px solid #21262d;")
        left.setFixedWidth(480)
        left_lay = QVBoxLayout(left)
        left_lay.setAlignment(Qt.AlignCenter)
        lbl = QLabel("🎫")
        lbl.setStyleSheet("font-size: 72px; background: transparent;")
        lbl.setAlignment(Qt.AlignCenter)
        lbl2 = QLabel(APP_NAME)
        lbl2.setStyleSheet("font-size: 36px; font-weight: 800; color: #f78166; background: transparent;")
        lbl2.setAlignment(Qt.AlignCenter)
        left_lay.addWidget(lbl)
        left_lay.addWidget(lbl2)

        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setAlignment(Qt.AlignCenter)
        right_lay.setSpacing(10)

        lbl_baslik = QLabel("Hesap Oluştur")
        lbl_baslik.setStyleSheet("font-size: 22px; font-weight: 700;")
        lbl_baslik.setAlignment(Qt.AlignCenter)
        self.txt_kadi = QLineEdit()
        self.txt_kadi.setPlaceholderText("Kullanıcı Adı")
        self.txt_kadi.setFixedWidth(320)
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("E-posta (ornek@gmail.com)")
        self.txt_email.setFixedWidth(320)
        self.txt_sifre = QLineEdit()
        self.txt_sifre.setPlaceholderText("Şifre")
        self.txt_sifre.setEchoMode(QLineEdit.Password)
        self.txt_sifre.setFixedWidth(320)

        btn_kayit = QPushButton("✅ Kayıt Ol")
        btn_kayit.setFixedWidth(320)
        btn_kayit.setObjectName("primary_btn")
        btn_kayit.clicked.connect(self._kayit)
        btn_geri = QPushButton("← Giriş Yap")
        btn_geri.setFixedWidth(320)
        btn_geri.setStyleSheet("border: none; color: #f78166; background: transparent; font-weight: 600;")
        btn_geri.clicked.connect(self.go_to_login.emit)

        for w in [lbl_baslik, self.txt_kadi, self.txt_email, self.txt_sifre, btn_kayit, btn_geri]:
            right_lay.addWidget(w, alignment=Qt.AlignCenter)

        root.addWidget(left)
        root.addWidget(right)

    def _kayit(self):
        kadi = self.txt_kadi.text().strip()
        email = self.txt_email.text().strip()
        sifre = self.txt_sifre.text()
        if not kadi or not email or not sifre:
            QMessageBox.warning(self, "Hata", "Tüm alanları doldurun!")
            return
        if "@" not in email or "." not in email.split("@")[-1]:
            QMessageBox.warning(self, "Hata", "Geçerli bir e-posta adresi girin! (@ işareti zorunludur)")
            return
        if self.db.kayit_ol(kadi, sifre):
            QMessageBox.information(self, "Başarılı", "Kayıt tamamlandı!")
            self.go_to_login.emit()
        else:
            QMessageBox.warning(self, "Hata", "Bu kullanıcı adı zaten kullanımda!")


# ─── ANA PENCERE ──────────────────────────────────────────────────────
class MainWindow(QWidget):
    logout_signal = pyqtSignal()

    def __init__(self, db, rol, kadi):
        super().__init__()
        self.db = db
        self.rol = rol
        self.kadi = kadi
        self.theme = "dark"
        self.accent = DEFAULT_ACCENT
        self.avatar_color = AVATAR_COLORS[DEFAULT_AVATAR_COLOR]
        self.setWindowTitle(f"{APP_NAME} — {kadi} ({rol})")
        self.setMinimumSize(1000, 650)
        self.resize(1300, 820)
        self.setStyleSheet(get_style(self.theme, self.accent))
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── SIDEBAR ──────────────────────────────────────
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setObjectName("sidebar")
        self._update_sidebar_style()
        sb_lay = QVBoxLayout(self.sidebar)
        sb_lay.setContentsMargins(12, 0, 12, 12)
        sb_lay.setSpacing(4)

        # Logo + uygulama adı
        lbl_logo = QLabel(f"🎫 {APP_NAME}")
        lbl_logo.setObjectName("app_logo")
        lbl_logo.setStyleSheet("font-size: 17px; font-weight: 800; color: #f78166; padding: 20px 10px 14px 10px; border-bottom: 1px solid #21262d; background: transparent;")
        sb_lay.addWidget(lbl_logo)

        # Avatar + kullanıcı adı butonu
        user_row = QHBoxLayout()
        user_row.setSpacing(8)
        self.avatar = AvatarWidget(self.kadi[0] if self.kadi else "?", self.avatar_color)
        self.btn_user = QPushButton(f" {self.kadi}")
        self.btn_user.setObjectName("user_btn")
        self.btn_user.setToolTip("Hesap Ayarları")
        self.btn_user.clicked.connect(self._ayarlari_ac)
        user_row.addWidget(self.avatar)
        user_row.addWidget(self.btn_user)
        sb_lay.addLayout(user_row)
        sb_lay.addSpacing(6)

        nav_items = [
            ("📊", "Dashboard",         self._go_dash),
            ("🗓️", "Etkinlikler",       self._go_etkinlikler),
            ("🎫", "Biletlerim",         self._go_biletler),
            ("📤", "Rezervasyon Al",     self._go_rezervasyon),
        ]
        if self.rol == "admin":
            nav_items += [
                ("👥", "Katılımcılar",  self._go_katilimcilar),
                ("📋", "Tüm Rezerv.",   self._go_tum_rezerv),
            ]

        self.nav_buttons = []
        for icon, label, fn in nav_items:
            btn = QPushButton(f"{icon}  {label}")
            btn.setStyleSheet("""
                QPushButton { text-align: left; padding: 10px 14px; border-radius: 8px;
                              background: transparent; border: none; color: #8b949e; font-weight: 600; }
                QPushButton:hover { background-color: #21262d; color: #e6edf3; }
                QPushButton:checked { background-color: #1f3550; color: #f78166; }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(fn)
            sb_lay.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_lay.addStretch()

        btn_ayarlar = QPushButton("⚙️  Ayarlar")
        btn_ayarlar.setStyleSheet("text-align: left; padding: 10px 14px; border-radius: 8px; background: transparent; border: none; color: #8b949e; font-weight: 600;")
        btn_ayarlar.clicked.connect(self._ayarlari_ac)
        sb_lay.addWidget(btn_ayarlar)

        btn_logout = QPushButton("🚪  Çıkış Yap")
        btn_logout.setObjectName("danger_btn")
        btn_logout.clicked.connect(self.logout_signal.emit)
        sb_lay.addWidget(btn_logout)

        # ── İÇERİK ALANI ─────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(20, 20, 20, 20)

        self._build_dash()        # 0
        self._build_etkinlikler() # 1
        self._build_biletler()    # 2
        self._build_rezervasyon() # 3
        if self.rol == "admin":
            self._build_katilimcilar() # 4
            self._build_tum_rezerv()   # 5

        root.addWidget(self.sidebar)
        root.addWidget(self.stack)
        self._go_dash()

    def _update_sidebar_style(self):
        """Tema değişince sidebar arka planını da güncelle."""
        if self.theme == "dark":
            from tema import ACCENT_COLORS
            colors = ACCENT_COLORS.get(self.accent, ACCENT_COLORS[DEFAULT_ACCENT])
            bg = colors["dark_bg2"]
            bdr = colors["dark_border"]
        else:
            from tema import ACCENT_COLORS
            colors = ACCENT_COLORS.get(self.accent, ACCENT_COLORS[DEFAULT_ACCENT])
            bg = colors["light_bg2"]
            bdr = colors["light_border"]
        self.sidebar.setStyleSheet(f"background-color: {bg}; border-right: 1px solid {bdr};")

    def _set_active(self, idx):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == idx)
        self.stack.setCurrentIndex(idx)

    # ── DASHBOARD ─────────────────────────────────────────────
    def _build_dash(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 24, 24, 24)

        lbl = QLabel("📊 Dashboard")
        lbl.setObjectName("page_title")
        lay.addWidget(lbl)

        self.cards_lay = QHBoxLayout()
        self.card_etk   = DashCard("🗓️", "Toplam Etkinlik",    0, "#58a6ff")
        self.card_bilet = DashCard("🎫", "Toplam Bilet",       0, "#3fb950")
        self.card_kat   = DashCard("👥", "Katılımcı Sayısı",   0, "#d2a8ff")
        for c in [self.card_etk, self.card_bilet, self.card_kat]:
            self.cards_lay.addWidget(c)
        lay.addLayout(self.cards_lay)

        mid = QHBoxLayout()

        chart_frame = QFrame()
        chart_frame.setObjectName("card")
        chart_frame.setFixedHeight(300)
        chart_lay = QVBoxLayout(chart_frame)
        self.figure = Figure(figsize=(4, 3), dpi=90)
        self.canvas = FigureCanvas(self.figure)
        chart_lay.addWidget(QLabel("Kategori Dağılımı"))
        chart_lay.addWidget(self.canvas)
        mid.addWidget(chart_frame, 3)

        upcoming_frame = QFrame()
        upcoming_frame.setObjectName("card")
        upcoming_frame.setFixedHeight(300)
        up_lay = QVBoxLayout(upcoming_frame)
        up_lay.addWidget(QLabel("⚡ Yaklaşan Etkinlikler"))
        self.tbl_upcoming = QTableWidget(0, 4)
        self.tbl_upcoming.setHorizontalHeaderLabels(["Etkinlik", "Tarih", "Saat", "Konum"])
        self.tbl_upcoming.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_upcoming.setAlternatingRowColors(True)
        up_lay.addWidget(self.tbl_upcoming)
        mid.addWidget(upcoming_frame, 4)

        lay.addLayout(mid)
        self.stack.addWidget(page)

    def _go_dash(self):
        self._set_active(0)
        t, b, f, k = self.db.istatistikleri_getir()
        self.card_etk.lbl_val.setText(str(t))
        self.card_bilet.lbl_val.setText(str(b))
        self.card_kat.lbl_val.setText(str(k))

        self.figure.clear()
        veriler = self.db.kategori_dagilimi_getir()
        if veriler:
            ax = self.figure.add_subplot(111)
            from tema import ACCENT_COLORS
            colors = ACCENT_COLORS.get(self.accent, ACCENT_COLORS[DEFAULT_ACCENT])
            bg = colors["dark_bg"] if self.theme == "dark" else colors["light_bg"]
            fc = 'white' if self.theme == "dark" else '#1f2328'
            self.figure.patch.set_facecolor(bg)
            ax.set_facecolor(bg)
            lbls = [v[0] for v in veriler]
            sizes = [v[1] for v in veriler]
            pie_colors = ['#58a6ff','#3fb950','#f78166','#d2a8ff','#ffa657','#ff7b72','#79c0ff']
            ax.pie(sizes, labels=lbls, autopct='%1.0f%%',
                   textprops={'color': fc, 'fontsize': 9},
                   colors=pie_colors[:len(lbls)], startangle=90,
                   wedgeprops={'edgecolor': bg, 'linewidth': 2})
        self.canvas.draw()

        self.tbl_upcoming.setRowCount(0)
        for row, data in enumerate(self.db.yaklasan_etkinlikler()):
            self.tbl_upcoming.insertRow(row)
            for i in range(4):
                self.tbl_upcoming.setItem(row, i, QTableWidgetItem(str(data[i])))

    # ── ETKİNLİKLER ───────────────────────────────────────────
    def _build_etkinlikler(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 24, 24, 24)
        lbl = QLabel("🗓️ Etkinlikler")
        lbl.setObjectName("page_title")
        lay.addWidget(lbl)

        top = QHBoxLayout()
        self.txt_ara = QLineEdit()
        self.txt_ara.setPlaceholderText("🔍  Etkinlik, kategori veya konum ara...")
        self.txt_ara.textChanged.connect(self._liste)
        top.addWidget(self.txt_ara)
        if self.rol == "admin":
            btn_ekle = QPushButton("➕ Etkinlik Ekle")
            btn_ekle.setObjectName("primary_btn")
            btn_ekle.clicked.connect(self._etkinlik_ekle)
            top.addWidget(btn_ekle)
        lay.addLayout(top)

        cols = ["ID", "Etkinlik Adı", "Kategori", "Tarih", "Saat", "Konum", "Kap.", "Katıl.", "Durum",
                "S.Önü Yet.(₺)", "S.Önü Öğr.(₺)", "S.Arka Yet.(₺)", "S.Arka Öğr.(₺)"]
        self.tbl_etk = QTableWidget(0, len(cols))
        self.tbl_etk.setHorizontalHeaderLabels(cols)
        self.tbl_etk.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_etk.setAlternatingRowColors(True)
        lay.addWidget(self.tbl_etk)

        if self.rol == "admin":
            admin_bar = QHBoxLayout()
            btn_sil = QPushButton("🗑️ Seçili Sil")
            btn_sil.setObjectName("danger_btn")
            btn_sil.clicked.connect(self._etkinlik_sil)
            btn_iptal = QPushButton("⛔ İptal Et")
            btn_iptal.clicked.connect(self._etkinlik_iptal)
            admin_bar.addWidget(btn_sil)
            admin_bar.addWidget(btn_iptal)
            admin_bar.addStretch()
            lay.addLayout(admin_bar)

        self.stack.addWidget(page)

    def _go_etkinlikler(self):
        self._set_active(1)
        self._liste()

    def _liste(self):
        self.tbl_etk.setRowCount(0)
        metin = self.txt_ara.text() if hasattr(self, 'txt_ara') else ""
        veriler = self.db.etkinlik_ara(metin)
        for row, data in enumerate(veriler):
            self.tbl_etk.insertRow(row)
            for i in range(13):
                item = QTableWidgetItem(str(data[i]))
                if i == 8:
                    if data[i] == "İptal":
                        item.setForeground(QColor("#f85149"))
                    elif data[i] == "Aktif":
                        item.setForeground(QColor("#3fb950"))
                self.tbl_etk.setItem(row, i, item)


    def _etkinlik_ekle(self):
        dlg = EtkinlikEkleDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if not data[0] or not data[2] or not data[4]:
                QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")
                return
            self.db.etkinlik_ekle(*data)
            self._liste()

    def _etkinlik_sil(self):
        row = self.tbl_etk.currentRow()
        if row < 0:
            return
        eid = int(self.tbl_etk.item(row, 0).text())
        ead = self.tbl_etk.item(row, 1).text()
        reply = QMessageBox.question(self, "Onayla", f"'{ead}' etkinliği silinecek. Emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.etkinlik_sil(eid)
            self._liste()

    def _etkinlik_iptal(self):
        row = self.tbl_etk.currentRow()
        if row < 0:
            return
        eid = int(self.tbl_etk.item(row, 0).text())
        self.db.etkinlik_iptal_et(eid)
        self._liste()


    # ── BİLETLERİM ────────────────────────────────────────────
    def _build_biletler(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 24, 24, 24)
        lbl = QLabel("🎫 Biletlerim")
        lbl.setObjectName("page_title")
        lay.addWidget(lbl)
        self.tbl_bilet = QTableWidget(0, 9)
        self.tbl_bilet.setHorizontalHeaderLabels(["ID", "Etkinlik", "Tarih", "Saat", "Konum", "Bilet Kodu", "Koltuk", "Kategori", "Fiyat (₺)"])
        self.tbl_bilet.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_bilet.setAlternatingRowColors(True)
        lay.addWidget(self.tbl_bilet)
        btn_iptal = QPushButton("❌ Rezervasyonu İptal Et")
        btn_iptal.setObjectName("danger_btn")
        btn_iptal.clicked.connect(self._rezervasyon_iptal)
        lay.addWidget(btn_iptal)
        self.stack.addWidget(page)

    def _go_biletler(self):
        self._set_active(2)
        self.tbl_bilet.setRowCount(0)
        for row, data in enumerate(self.db.kullanici_rezervasyonlari(self.kadi)):
            self.tbl_bilet.insertRow(row)
            for i in range(9):
                val = data[i]
                if i == 8:
                    val = f"{float(val):,.2f} ₺"
                self.tbl_bilet.setItem(row, i, QTableWidgetItem(str(val)))

    def _rezervasyon_iptal(self):
        row = self.tbl_bilet.currentRow()
        if row < 0:
            return
        eid = int(self.tbl_bilet.item(row, 0).text())
        ead = self.tbl_bilet.item(row, 1).text()
        reply = QMessageBox.question(self, "Onayla", f"'{ead}' rezervasyonu iptal edilsin mi?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.rezervasyon_iptal(eid, self.kadi)
            self._go_biletler()

    # ── REZERVASYON AL ────────────────────────────────────────
    def _build_rezervasyon(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 24, 24, 24)
        lbl = QLabel("📤 Rezervasyon Al")
        lbl.setObjectName("page_title")
        lay.addWidget(lbl)
        lbl_info = QLabel("Müsait etkinlikleri seçin ve rezervasyon yapın.")
        lbl_info.setStyleSheet("color: #8b949e; margin-bottom: 8px;")
        lay.addWidget(lbl_info)
        self.tbl_rez = QTableWidget(0, 12)
        self.tbl_rez.setHorizontalHeaderLabels([
            "ID", "Etkinlik", "Kategori", "Tarih", "Saat", "Konum", "Kap.", "Katıl.",
            "S.Önü Yet.(₺)", "S.Önü Öğr.(₺)", "S.Arka Yet.(₺)", "S.Arka Öğr.(₺)"
        ])
        self.tbl_rez.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_rez.setAlternatingRowColors(True)
        lay.addWidget(self.tbl_rez)
        btn = QPushButton("✅ Rezervasyon Yap")
        btn.setObjectName("primary_btn")
        btn.clicked.connect(self._rezervasyon_yap)
        lay.addWidget(btn)
        self.stack.addWidget(page)

    def _go_rezervasyon(self):
        self._set_active(3)
        self.tbl_rez.setRowCount(0)
        for row, data in enumerate([e for e in self.db.etkinlikleri_getir() if e[8] == "Aktif" and e[7] < e[6]]):
            self.tbl_rez.insertRow(row)
            for i in range(12):
                self.tbl_rez.setItem(row, i, QTableWidgetItem(str(data[i])))

    def _rezervasyon_yap(self):
        row = self.tbl_rez.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir etkinlik seçin!")
            return
        # Etkinliğin tüm verisini al
        aktif_etk = [e for e in self.db.etkinlikleri_getir() if e[8] == "Aktif" and e[7] < e[6]]
        etkinlik_data = aktif_etk[row]
        dlg = RezervasyanDialog(etkinlik_data, self)
        if dlg.exec_() != QDialog.Accepted:
            return
        koltuk_tipi, bilet_kategorisi, fiyat = dlg.get_secim()
        eid = etkinlik_data[0]
        ok, mesaj = self.db.rezervasyon_yap(eid, self.kadi, koltuk_tipi, bilet_kategorisi, fiyat)
        if ok:
            QMessageBox.information(
                self, "Başarılı! 🎫",
                f"Rezervasyon tamamlandı!\n\n"
                f"Koltuk: {koltuk_tipi}\n"
                f"Kategori: {bilet_kategorisi}\n"
                f"Ücret: {fiyat:,.2f} ₺\n\n"
                f"Bilet Kodunuz:\n{mesaj}"
            )
            self._go_rezervasyon()
        else:
            QMessageBox.warning(self, "Hata", mesaj)

    # ── KATILIMCILAR (Admin) ───────────────────────────────────
    def _build_katilimcilar(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 24, 24, 24)
        lbl = QLabel("👥 Katılımcı Yönetimi")
        lbl.setObjectName("page_title")
        lay.addWidget(lbl)

        top = QHBoxLayout()
        lbl_sec = QLabel("Etkinlik seçin:")
        self.cmb_etk = QComboBox()
        self.cmb_etk.setMinimumWidth(300)
        btn_getir = QPushButton("🔍 Listele")
        btn_getir.setObjectName("primary_btn")
        btn_getir.clicked.connect(self._katilimci_listele)
        top.addWidget(lbl_sec)
        top.addWidget(self.cmb_etk)
        top.addWidget(btn_getir)
        top.addStretch()
        lay.addLayout(top)

        self.tbl_kat = QTableWidget(0, 3)
        self.tbl_kat.setHorizontalHeaderLabels(["Kullanıcı Adı", "Rezervasyon Tarihi", "Bilet Kodu"])
        self.tbl_kat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_kat.setAlternatingRowColors(True)
        lay.addWidget(self.tbl_kat)
        self.stack.addWidget(page)

    def _go_katilimcilar(self):
        self._set_active(4)
        self.cmb_etk.clear()
        self._etkinlik_listesi = self.db.etkinlikleri_getir()
        for e in self._etkinlik_listesi:
            self.cmb_etk.addItem(f"{e[1]} ({e[3]})", e[0])

    def _katilimci_listele(self):
        eid = self.cmb_etk.currentData()
        if eid is None:
            return
        self.tbl_kat.setRowCount(0)
        for row, data in enumerate(self.db.etkinlik_katilimcilari(eid)):
            self.tbl_kat.insertRow(row)
            for i in range(3):
                self.tbl_kat.setItem(row, i, QTableWidgetItem(str(data[i])))

    # ── TÜM REZERVASYONLAR (Admin) ────────────────────────────
    def _build_tum_rezerv(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 24, 24, 24)
        lbl = QLabel("📋 Tüm Rezervasyonlar")
        lbl.setObjectName("page_title")
        lay.addWidget(lbl)
        self.tbl_tum_rez = QTableWidget(0, 7)
        self.tbl_tum_rez.setHorizontalHeaderLabels(["Etkinlik", "Kullanıcı", "Tarih", "Bilet Kodu", "Koltuk", "Kategori", "Fiyat (₺)"])
        self.tbl_tum_rez.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_tum_rez.setAlternatingRowColors(True)
        lay.addWidget(self.tbl_tum_rez)
        self.stack.addWidget(page)

    def _go_tum_rezerv(self):
        self._set_active(5)
        self.tbl_tum_rez.setRowCount(0)
        for row, data in enumerate(self.db.tum_rezervasyonlar()):
            self.tbl_tum_rez.insertRow(row)
            for i in range(7):
                val = data[i]
                if i == 6:
                    val = f"{float(val):,.2f} ₺"
                self.tbl_tum_rez.setItem(row, i, QTableWidgetItem(str(val)))

    # ── AYARLAR ───────────────────────────────────────────────
    def _ayarlari_ac(self):
        dlg = AyarlarDialog(
            self.db, self.kadi,
            self.theme, self.accent,
            self.avatar_color,
            parent=self
        )
        dlg.theme_changed.connect(self._uygula_tema)
        dlg.accent_changed.connect(self._uygula_accent)
        dlg.name_changed.connect(self._kullanici_adi_guncelle)
        dlg.avatar_color_changed.connect(self._uygula_avatar_renk)
        dlg.exec_()

    def _uygula_tema(self, tema):
        self.theme = tema
        self.setStyleSheet(get_style(self.theme, self.accent))
        self._update_sidebar_style()
        self._go_dash()

    def _uygula_accent(self, accent):
        self.accent = accent
        self.setStyleSheet(get_style(self.theme, self.accent))
        self._update_sidebar_style()
        self._go_dash()

    def _uygula_avatar_renk(self, hex_c):
        self.avatar_color = hex_c
        self.avatar.set_renk(hex_c)

    def _kullanici_adi_guncelle(self, yeni_kadi):
        self.kadi = yeni_kadi
        self.btn_user.setText(f" {yeni_kadi}")
        self.avatar.set_harf(yeni_kadi[0] if yeni_kadi else "?")
        self.setWindowTitle(f"{APP_NAME} — {yeni_kadi} ({self.rol})")