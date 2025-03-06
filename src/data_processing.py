"""
Veri yükleme, temizleme ve dönüştürme işlemleri için fonksiyonlar.

Bu, daha önceki data_processing.py dosyasının basitleştirilmiş versiyonudur.
Uygulama tamamlandığında orijinal modül içe aktarılmalıdır.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging

# Konfigürasyon dosyasını içe aktar
from config.tezgah_listesi import KISIMLAR_DICT

# Loglama yapılandırması
logger = logging.getLogger(__name__)

def assign_kisim(makina_kodu: str) -> str:
    """
    Makina koduna göre kısım atar.
    
    Args:
        makina_kodu: Makina kodu
        
    Returns:
        str: Kısım adı
    """
    for kisim, tezgahlar in KISIMLAR_DICT.items():
        if makina_kodu in tezgahlar:
            return kisim
    return "Diğer"

def prepare_data_for_analysis(
    durus_file: str,
    calisma_file: str,
    arizali_file: str = None
) -> Tuple[pd.DataFrame, Dict, List[int]]:
    """
    Analiz için veri setini hazırlar.
    
    Args:
        durus_file: Duruş verisi dosya yolu
        calisma_file: Çalışma süresi dosya yolu
        arizali_file: Arızalı tezgah listesi dosya yolu
        
    Returns:
        Tuple[pd.DataFrame, Dict, List[int]]: İşlenmiş veri, kısım-tezgah sayıları ve hafta listesi
    """
    logger.info("Veri hazırlama işlemi başlıyor...")
    
    try:
        # Örnek veri ve parametreler oluştur
        df = pd.DataFrame({
            'İş Merkezi Kodu ': ['CT.D01', 'CT.D02', 'İM.K01', 'İM.MV1'],
            'Duruş Adı': ['YEMEK MOLASI', 'ARIZA', 'TASARIM', 'ÇALIŞMA SÜRESİ'],
            'Duruş Başlangıç Tarih': pd.date_range(start='2023-01-01', periods=4),
            'Duruş Bitiş Tarih': pd.date_range(start='2023-01-01 01:00:00', periods=4),
            'Süre (Saniye)': [3600, 7200, 1800, 28800],
            'Süre (Dakika)': [60, 120, 30, 480],
            'Hafta': [1, 1, 2, 2],
            'Oee': [0.85, 0.78, 0.92, 0.88],
            'Performans': [0.90, 0.82, 0.95, 0.87],
            'Kullanılabilirlik': [0.92, 0.85, 0.96, 0.90],
            'Kalite': [0.97, 0.88, 0.98, 0.95]
        })
        
        # Kısım bilgisini ekle
        df['KISIM'] = df['İş Merkezi Kodu '].apply(assign_kisim)
        
        # Örnek kısım-tezgah sayıları
        kisim_tezgah_sayilari = {
            'KISIM 2.1': len(KISIM_2_1),
            'KISIM 2.2': len(KISIM_2_2),
            'KISIM 3.1': len(KISIM_3_1),
            'KISIM 3.2': len(KISIM_3_2),
            'KISIM 4.1': len(KISIM_4_1),
            'KISIM 4.2': len(KISIM_4_2),
            'KISIM 5.1': len(KISIM_5_1)
        }
        
        # Örnek hafta listesi
        weeks = [1, 2]
        
        logger.info("Veri hazırlama işlemi tamamlandı (örnek veri oluşturuldu).")
        return df, kisim_tezgah_sayilari, weeks
        
    except Exception as e:
        logger.error(f"Veri hazırlama hatası: {str(e)}", exc_info=True)
        # Hata durumunda temel örnek bir veri oluştur
        df = pd.DataFrame(columns=['İş Merkezi Kodu ', 'Duruş Adı', 'Süre (Dakika)', 'KISIM', 'Hafta'])
        return df, {}, [1]

def get_latest_week_data(df: pd.DataFrame, weeks: List[int]) -> pd.DataFrame:
    """
    En son haftaya ait veriyi filtreler.
    
    Args:
        df: Tüm veri seti
        weeks: Sıralanmış hafta numaraları listesi
        
    Returns:
        pd.DataFrame: Son haftaya ait filtrelenmiş veri
    """
    if not weeks:
        logger.warning("Hafta bilgisi bulunamadı!")
        return pd.DataFrame()
        
    latest_week = weeks[-1]  # Son hafta
    logger.info(f"Son hafta verisi filtreleniyor: Hafta {latest_week}")
    
    latest_week_df = df[df['Hafta'] == latest_week]
    logger.info(f"Son hafta satır sayısı: {len(latest_week_df)}")
    
    return latest_week_df