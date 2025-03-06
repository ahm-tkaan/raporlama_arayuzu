"""
Tezgah duruş analizi veri modeli.
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import logging

# Loglama yapılandırması
logger = logging.getLogger(__name__)

class AnalysisModel:
    """
    Tezgah duruş analizi veri modeli sınıfı.
    """
    
    def __init__(self):
        """
        Veri modelini başlat.
        """
        # Ham veriler
        self.durus_data = None
        self.calisma_data = None
        self.arizali_tezgahlar = []
        
        # İşlenmiş veriler
        self.processed_data = None
        self.kisim_tezgah_sayilari = {}
        self.weeks = []
        self.latest_week_data = None
        
        # Hesaplanmış sonuçlar
        self.toplam_sureler = None
        self.tezgah_basina_kisim_sureleri = None
        self.tezgah_sureleri = None
        self.tezgah_durus_ozet = None
        self.kisim_durus_ozet = {}
        
        # Rapor yolları
        self.report_files = []
        
    def set_durus_data(self, data: pd.DataFrame) -> None:
        """
        Duruş verilerini ayarla.
        
        Args:
            data: Duruş verileri DataFrame'i
        """
        self.durus_data = data
        logger.info(f"Duruş verileri modele yüklendi. Satır sayısı: {len(data)}")
    
    def set_calisma_data(self, data: pd.DataFrame) -> None:
        """
        Çalışma süresi verilerini ayarla.
        
        Args:
            data: Çalışma süresi verileri DataFrame'i
        """
        self.calisma_data = data
        logger.info(f"Çalışma verileri modele yüklendi. Satır sayısı: {len(data)}")
    
    def set_arizali_tezgahlar(self, tezgahlar: List[str]) -> None:
        """
        Arızalı tezgah listesini ayarla.
        
        Args:
            tezgahlar: Arızalı tezgah kodları listesi
        """
        self.arizali_tezgahlar = tezgahlar
        logger.info(f"Arızalı tezgah listesi modele yüklendi. Tezgah sayısı: {len(tezgahlar)}")
    
    def set_processed_data(self, 
                          data: pd.DataFrame, 
                          kisim_tezgah_sayilari: Dict[str, int],
                          weeks: List[int]) -> None:
        """
        İşlenmiş veriyi ayarla.
        
        Args:
            data: İşlenmiş veri DataFrame'i
            kisim_tezgah_sayilari: Kısımlara göre tezgah sayıları
            weeks: Hafta numaraları listesi
        """
        self.processed_data = data
        self.kisim_tezgah_sayilari = kisim_tezgah_sayilari
        self.weeks = weeks
        logger.info(f"İşlenmiş veri modele yüklendi. Satır sayısı: {len(data)}")
    
    def set_latest_week_data(self, data: pd.DataFrame) -> None:
        """
        Son hafta verisini ayarla.
        
        Args:
            data: Son hafta verisi DataFrame'i
        """
        self.latest_week_data = data
        logger.info(f"Son hafta verisi modele yüklendi. Satır sayısı: {len(data)}")
    
    def set_calculation_results(self,
                               toplam_sureler: pd.DataFrame,
                               tezgah_basina_kisim_sureleri: pd.DataFrame,
                               tezgah_sureleri: pd.DataFrame,
                               tezgah_durus_ozet: pd.DataFrame) -> None:
        """
        Hesaplama sonuçlarını ayarla.
        
        Args:
            toplam_sureler: Toplam duruş süreleri DataFrame'i
            tezgah_basina_kisim_sureleri: Tezgah başına kısım süreleri DataFrame'i
            tezgah_sureleri: Tezgah duruş süreleri DataFrame'i
            tezgah_durus_ozet: Tezgah duruş özeti DataFrame'i
        """
        self.toplam_sureler = toplam_sureler
        self.tezgah_basina_kisim_sureleri = tezgah_basina_kisim_sureleri
        self.tezgah_sureleri = tezgah_sureleri
        self.tezgah_durus_ozet = tezgah_durus_ozet
        logger.info("Hesaplama sonuçları modele yüklendi.")
    
    def add_kisim_durus_ozet(self, kisim: str, data: pd.DataFrame) -> None:
        """
        Kısım duruş özeti ekle.
        
        Args:
            kisim: Kısım adı
            data: Kısım duruş özeti DataFrame'i
        """
        self.kisim_durus_ozet[kisim] = data
        logger.info(f"{kisim} için duruş özeti modele eklendi.")
    
    def add_report_file(self, file_path: str) -> None:
        """
        Rapor dosyası ekle.
        
        Args:
            file_path: Rapor dosyası yolu
        """
        self.report_files.append(file_path)
        logger.info(f"Rapor dosyası eklendi: {file_path}")
    
    def clear(self) -> None:
        """
        Modeli temizle.
        """
        self.__init__()
        logger.info("Model temizlendi.")