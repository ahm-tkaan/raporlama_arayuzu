#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tezgah Duruş Analizi GUI uygulaması ana giriş noktası.
"""

import sys
import os
import logging

# Modül yollarını ayarla
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)  # Ana dizini Python yoluna ekle

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale
from app.views.main_window import MainWindow

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tezgah_durus_gui.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """
    Uygulama çalışma ortamını hazırlar.
    """
    # Klasör yapısını oluştur
    directories = [
        "data/raw",
        "data/processed",
        "reports",
        "Raporlar",
        "Raporlar/Genel",
        "Raporlar/Kısımlar/Son Hafta",
        "Raporlar/Kısımlar/4 haftalık",
        "Raporlar/Kısımlar/Son Hafta Tezgah Başına Ortalama",
        "Raporlar/Tezgahlar/Son Hafta",
        "Raporlar/Tezgahlar/4 haftalık",
        "Raporlar/Tee/Genel",
        "Raporlar/Tee/Kısımlar",
        "Raporlar/Tee/Tezgahlar"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    logger.info("Çalışma ortamı hazırlandı.")

def main():
    """
    Uygulama ana fonksiyonu.
    """
    # Uygulama çalışma ortamını hazırla
    setup_environment()
    
    # PyQt uygulamasını başlat
    app = QApplication(sys.argv)
    app.setApplicationName("Tezgah Duruş Analizi")
    
    # Pencereyi oluştur ve göster
    window = MainWindow()
    window.show()
    
    # Uygulamayı çalıştır
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()



