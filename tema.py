# Kullanıcının seçebileceği aksan renkleri
ACCENT_COLORS = {
    "🔴 Kırmızı":   {"key": "red",    "dark_accent": "#f78166", "dark_hover": "#ff9580", "light_accent": "#cf222e", "light_hover": "#a40e26",
                     "dark_bg": "#130d0b", "dark_bg2": "#1c1210", "dark_border": "#2d1a17",
                     "light_bg": "#fff8f7", "light_bg2": "#fff0ee", "light_border": "#f5c6c0"},
    "🔵 Mavi":      {"key": "blue",   "dark_accent": "#58a6ff", "dark_hover": "#79c0ff", "light_accent": "#0969da", "light_hover": "#0550ae",
                     "dark_bg": "#0b0d13", "dark_bg2": "#10141c", "dark_border": "#162030",
                     "light_bg": "#f7f9ff", "light_bg2": "#eef3ff", "light_border": "#c0d4f5"},
    "🟢 Yeşil":     {"key": "green",  "dark_accent": "#3fb950", "dark_hover": "#56d364", "light_accent": "#1a7f37", "light_hover": "#116329",
                     "dark_bg": "#0b130d", "dark_bg2": "#101c12", "dark_border": "#162d1a",
                     "light_bg": "#f7fff8", "light_bg2": "#eefff0", "light_border": "#c0f0c8"},
    "🟣 Mor":       {"key": "purple", "dark_accent": "#d2a8ff", "dark_hover": "#e0c0ff", "light_accent": "#8250df", "light_hover": "#6639ba",
                     "dark_bg": "#110d13", "dark_bg2": "#18101c", "dark_border": "#25162d",
                     "light_bg": "#fdf7ff", "light_bg2": "#f6eeff", "light_border": "#ddc0f5"},
    "🟠 Turuncu":   {"key": "orange", "dark_accent": "#ffa657", "dark_hover": "#ffb77c", "light_accent": "#bc4c00", "light_hover": "#953800",
                     "dark_bg": "#130f0b", "dark_bg2": "#1c1610", "dark_border": "#2d2016",
                     "light_bg": "#fffaf7", "light_bg2": "#fff3ea", "light_border": "#f5d9c0"},
    "🩷 Pembe":     {"key": "pink",   "dark_accent": "#ff6ec7", "dark_hover": "#ff91d4", "light_accent": "#bf3989", "light_hover": "#99286e",
                     "dark_bg": "#130b11", "dark_bg2": "#1c1018", "dark_border": "#2d1625",
                     "light_bg": "#fff7fb", "light_bg2": "#ffeeF7", "light_border": "#f5c0e0"},
}

DEFAULT_ACCENT = "🔴 Kırmızı"


def get_style(mode="dark", accent_name=None):
    if accent_name is None:
        accent_name = DEFAULT_ACCENT
    colors = ACCENT_COLORS.get(accent_name, ACCENT_COLORS[DEFAULT_ACCENT])

    if mode == "dark":
        acc  = colors["dark_accent"]
        acc2 = colors["dark_hover"]
        bg   = colors["dark_bg"]
        bg2  = colors["dark_bg2"]
        bdr  = colors["dark_border"]
        return f"""
            QWidget {{
                background-color: {bg};
                color: #e6edf3;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 13px;
            }}
            QLabel#user_name {{
                font-size: 15px; font-weight: 800; color: {acc};
                padding: 18px 10px; border-bottom: 1px solid {bdr};
                margin-bottom: 12px;
            }}
            QLabel#page_title {{
                font-size: 20px; font-weight: 800; color: #e6edf3;
                padding: 5px 0px 15px 0px;
            }}
            QLineEdit {{
                padding: 11px 14px; border: 1px solid {bdr};
                border-radius: 8px; background-color: {bg2};
                color: #e6edf3; margin-bottom: 5px;
            }}
            QLineEdit:focus {{ border: 1px solid {acc}; }}
            QPushButton {{
                background-color: {bg2}; color: #e6edf3;
                padding: 10px 16px; border-radius: 8px;
                font-weight: 600; border: 1px solid {bdr}; margin: 2px;
            }}
            QPushButton:hover {{ background-color: {bdr}; border-color: {acc}; }}
            QPushButton#primary_btn {{
                background-color: {acc}; color: {bg};
                border: none; font-weight: 700;
            }}
            QPushButton#primary_btn:hover {{ background-color: {acc2}; }}
            QPushButton#danger_btn {{
                background-color: #da3633; color: white; border: none;
            }}
            QPushButton#danger_btn:hover {{ background-color: #f85149; }}
            QPushButton#user_btn {{
                text-align: left; padding: 10px 14px; border-radius: 8px;
                background: transparent; border: none; color: {acc};
                font-weight: 700; font-size: 15px;
            }}
            QPushButton#user_btn:hover {{ background-color: {bg2}; }}
            QTableWidget {{
                background-color: {bg}; gridline-color: {bg2};
                border: 1px solid {bdr}; border-radius: 8px;
                alternate-background-color: {bg2};
            }}
            QTableWidget::item {{ padding: 8px; }}
            QTableWidget::item:selected {{ background-color: {acc}30; color: #e6edf3; }}
            QHeaderView::section {{
                background-color: {bg2}; color: #8b949e;
                padding: 10px; border: none;
                border-bottom: 1px solid {bdr};
                font-weight: 700; font-size: 11px;
            }}
            QScrollBar:vertical {{ border: none; background: {bg}; width: 7px; }}
            QScrollBar::handle:vertical {{ background: {bdr}; border-radius: 4px; }}
            QComboBox {{
                padding: 10px 14px; border: 1px solid {bdr};
                border-radius: 8px; background-color: {bg2}; color: #e6edf3;
            }}
            QComboBox:focus {{ border-color: {acc}; }}
            QComboBox QAbstractItemView {{
                background-color: {bg2}; border: 1px solid {bdr};
                selection-background-color: {acc}40;
            }}
            QFrame#card {{
                background-color: {bg2}; border: 1px solid {bdr};
                border-radius: 12px;
            }}
            QGroupBox {{
                border: 1px solid {bdr}; border-radius: 8px;
                margin-top: 12px; padding-top: 8px;
                font-weight: 700; color: #8b949e;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 12px; padding: 0 4px;
            }}
            QRadioButton {{ color: #e6edf3; background: transparent; spacing: 8px; }}
            QRadioButton::indicator {{ width: 16px; height: 16px; border-radius: 8px; border: 2px solid {bdr}; background: {bg2}; }}
            QRadioButton::indicator:checked {{ border-color: {acc}; background: {acc}; }}
            QSpinBox {{
                padding: 10px 14px; border: 1px solid {bdr};
                border-radius: 8px; background-color: {bg2}; color: #e6edf3;
            }}
            QSpinBox:focus {{ border-color: {acc}; }}
        """
    else:
        acc  = colors["light_accent"]
        acc2 = colors["light_hover"]
        bg   = colors["light_bg"]
        bg2  = colors["light_bg2"]
        bdr  = colors["light_border"]
        return f"""
            QWidget {{
                background-color: {bg}; color: #1f2328;
                font-family: 'Segoe UI', 'Arial', sans-serif; font-size: 13px;
            }}
            QLabel#user_name {{
                font-size: 15px; font-weight: 800; color: {acc};
                padding: 18px 10px; border-bottom: 1px solid {bdr}; margin-bottom: 12px;
            }}
            QLabel#page_title {{
                font-size: 20px; font-weight: 800; color: #1f2328;
                padding: 5px 0px 15px 0px;
            }}
            QLineEdit {{
                padding: 11px 14px; border: 1px solid {bdr};
                border-radius: 8px; background-color: #ffffff; color: #1f2328;
            }}
            QLineEdit:focus {{ border: 1px solid {acc}; }}
            QPushButton {{
                background-color: {bg}; color: #1f2328;
                padding: 10px 16px; border-radius: 8px;
                font-weight: 600; border: 1px solid {bdr}; margin: 2px;
            }}
            QPushButton:hover {{ background-color: {bg2}; border-color: {acc}; }}
            QPushButton#primary_btn {{
                background-color: {acc}; color: white;
                border: none; font-weight: 700;
            }}
            QPushButton#primary_btn:hover {{ background-color: {acc2}; }}
            QPushButton#danger_btn {{
                background-color: #da3633; color: white; border: none;
            }}
            QPushButton#user_btn {{
                text-align: left; padding: 10px 14px; border-radius: 8px;
                background: transparent; border: none; color: {acc};
                font-weight: 700; font-size: 15px;
            }}
            QPushButton#user_btn:hover {{ background-color: {bg2}; }}
            QTableWidget {{
                background-color: #ffffff; gridline-color: {bg2};
                border: 1px solid {bdr}; border-radius: 8px;
                alternate-background-color: {bg};
            }}
            QTableWidget::item:selected {{ background-color: {acc}25; color: #1f2328; }}
            QHeaderView::section {{
                background-color: {bg}; color: #636c76;
                padding: 10px; border: none; border-bottom: 1px solid {bdr};
                font-weight: 700; font-size: 11px;
            }}
            QScrollBar:vertical {{ border: none; background: {bg}; width: 7px; }}
            QScrollBar::handle:vertical {{ background: {bdr}; border-radius: 4px; }}
            QComboBox {{
                padding: 10px 14px; border: 1px solid {bdr};
                border-radius: 8px; background-color: #ffffff; color: #1f2328;
            }}
            QFrame#card {{
                background-color: #ffffff; border: 1px solid {bdr}; border-radius: 12px;
            }}
            QGroupBox {{
                border: 1px solid {bdr}; border-radius: 8px;
                margin-top: 12px; padding-top: 8px;
                font-weight: 700; color: #636c76;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; }}
            QRadioButton {{ color: #1f2328; background: transparent; spacing: 8px; }}
            QRadioButton::indicator {{ width: 16px; height: 16px; border-radius: 8px; border: 2px solid {bdr}; background: #ffffff; }}
            QRadioButton::indicator:checked {{ border-color: {acc}; background: {acc}; }}
            QSpinBox {{
                padding: 10px 14px; border: 1px solid {bdr};
                border-radius: 8px; background-color: #ffffff; color: #1f2328;
            }}
        """