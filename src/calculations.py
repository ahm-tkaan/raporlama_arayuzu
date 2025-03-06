"""
Duruş verileri ve tezgah performansları için hesaplama fonksiyonları.
Bu, daha önceki calculations.py dosyasının basitleştirilmiş versiyonudur.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging

# Loglama yapılandırması
logger = logging.getLogger(__name__)

def second_to_minute(df: pd.DataFrame, second_col: str = "Süre (Saniye)", 
                   minute_col: str = "Süre (Dakika)") -> pd.DataFrame:
    """
    Saniye cinsinden verilen süreleri dakikaya çevirir.
    
    Args:
        df: İşlenecek DataFrame
        second_col: Saniye sütununun adı
        minute_col: Dakika sütununun adı
        
    Returns:
        pd.DataFrame: Dakika sütunu eklenmiş DataFrame
    """
    result_df = df.copy()
    result_df[minute_col] = (result_df[second_col] / 60).astype(int)
    return result_df

def calculate_stop_time_sum(df: pd.DataFrame) -> pd.DataFrame:
    """
    Duruş adlarına göre süreleri toplar ve benzer duruşları birleştirir.
    
    Args:
        df: İşlenecek DataFrame
        
    Returns:
        pd.DataFrame: Duruş sürelerinin toplamını içeren DataFrame
    """
    logger.info("Duruş süreleri hesaplanıyor...")
    
    # Eğer veri boşsa boş DataFrame döndür
    if df.empty:
        return pd.DataFrame(columns=['Duruş Adı', 'Süre (Saniye)', 'Süre (Dakika)'])
    
    # Örnek bir hesaplama
    toplam_sureler = df.groupby("Duruş Adı")["Süre (Saniye)"].sum().reset_index()
    toplam_sureler = toplam_sureler.sort_values(by="Süre (Saniye)", ascending=False)
    
    # Saniyeden dakikaya çevir
    toplam_sureler = second_to_minute(toplam_sureler)
    
    return toplam_sureler

def calculate_part_machine_average_time(
    df: pd.DataFrame, 
    kisim_tezgah_sayilari: Dict[str, int]
) -> pd.DataFrame:
    """
    Kısımlara göre tek tezgah başına ortalama duruş sürelerini hesaplar.
    """
    logger.info("Kısım başına ortalama duruş süreleri hesaplanıyor...")
    
    # Eğer veri boşsa boş DataFrame döndür
    if df.empty:
        return pd.DataFrame(columns=['KISIM', 'Süre (Saniye)', 'Süre (Dakika)'])
    
    # ÇALIŞMA SÜRESİ dışındaki duruşları filtreleme
    filtered_df = df[df["Duruş Adı"] != "ÇALIŞMA SÜRESİ"].copy()
    
    # Kısımlara göre toplam süreleri hesapla
    kisim_sureleri = filtered_df.groupby("KISIM")["Süre (Saniye)"].sum().reset_index()
    kisim_sureleri = kisim_sureleri.sort_values(by="KISIM", ascending=True)

    # KISIM değerlerini tezgah sayılarına bölerek güncelle
    for idx, row in kisim_sureleri.iterrows():
        if row["KISIM"] in kisim_tezgah_sayilari:
            tezgah_sayisi = kisim_tezgah_sayilari[row["KISIM"]]
            if tezgah_sayisi > 0:  # Sıfıra bölme hatasını önle
                kisim_sureleri.at[idx, "Süre (Saniye)"] = row["Süre (Saniye)"] / tezgah_sayisi

    # Saniyeden dakikaya çevir
    kisim_sureleri = second_to_minute(kisim_sureleri)
    
    return kisim_sureleri

def calculate_machine_stop_times(df: pd.DataFrame) -> pd.DataFrame:
    """
    İş merkezlerinin toplam duruş sürelerini hesaplar.
    """
    logger.info("Tezgah duruş süreleri hesaplanıyor...")
    
    # Eğer veri boşsa boş DataFrame döndür
    if df.empty:
        return pd.DataFrame(columns=['İş Merkezi Kodu ', 'Süre (Saniye)', 'Süre (Dakika)'])
    
    # ÇALIŞMA SÜRESİ dışındaki duruşları filtreleme
    filtered_df = df[df['Duruş Adı'] != 'ÇALIŞMA SÜRESİ'].copy()
    
    # İş merkezi koduna göre toplam süreleri hesapla
    tezgah_sureleri = filtered_df.groupby("İş Merkezi Kodu ")["Süre (Saniye)"].sum().reset_index()
    
    # Saniyeden dakikaya çevir
    tezgah_sureleri = second_to_minute(tezgah_sureleri)
    
    # Süreye göre sırala
    tezgah_sureleri = tezgah_sureleri.sort_values(by="Süre (Dakika)", ascending=True)
    
    return tezgah_sureleri

def calculate_machine_stop_type_times(df: pd.DataFrame) -> pd.DataFrame:
    """
    İş merkezleri için duruş tipine göre süreleri hesaplar.
    """
    logger.info("Tezgah duruş tipi süreleri hesaplanıyor...")
    
    # Eğer veri boşsa boş DataFrame döndür
    if df.empty:
        return pd.DataFrame(columns=['İş Merkezi Kodu ', 'Duruş Adı', 'Süre (Saniye)', 'Süre (Dakika)'])
    
    # Her bir "İş Merkezi Kodu" ve "Duruş Adı" için toplam süreyi hesapla
    tezgah_durus_ozet = df.groupby(["İş Merkezi Kodu ", "Duruş Adı"])["Süre (Saniye)"].sum().reset_index()
    
    # Saniyeden dakikaya çevir
    tezgah_durus_ozet = second_to_minute(tezgah_durus_ozet)
    
    return tezgah_durus_ozet

def filter_sort_top_stops(
    df: pd.DataFrame, 
    max_week: int = 1,
    gozlemlenecek: str = "KISIM"
) -> pd.DataFrame:
    """
    Her bir kısım veya tezgah için en büyük 10 duruşu filtreleyip sıralar.
    """
    logger.info(f"{gozlemlenecek} için en büyük 10 duruş hesaplanıyor...")
    
    # Eğer veri boşsa boş DataFrame döndür
    if df.empty:
        return pd.DataFrame(columns=[gozlemlenecek, 'Hafta', 'Duruş Adı', 'Süre (Saniye)', 'Süre (Dakika)'])
    
    # Gerekli sütunları kontrol et
    required_columns = [gozlemlenecek, 'Hafta', 'Duruş Adı', 'Süre (Saniye)']
    for col in required_columns:
        if col not in df.columns:
            logger.error(f"Gerekli sütun bulunamadı: {col}")
            empty_df = pd.DataFrame(columns=required_columns + ['Süre (Dakika)'])
            return empty_df
    
    # Basitleştirilmiş model: Son haftaya ait en büyük 10 duruşu hesapla
    latest_week_df = df[df['Hafta'] == max_week]
    
    if latest_week_df.empty:
        return pd.DataFrame(columns=required_columns + ['Süre (Dakika)'])
    
    result = (
        latest_week_df.groupby([gozlemlenecek, 'Duruş Adı'])['Süre (Saniye)']
        .sum()
        .reset_index()
        .sort_values('Süre (Saniye)', ascending=False)
        .groupby(gozlemlenecek)
        .head(10)
        .reset_index(drop=True)
    )
    
    # Hafta sütunu ekle
    result['Hafta'] = max_week
    
    # Saniyeden dakikaya çevir
    result = second_to_minute(result)
    
    return result

def calculate_part_average_stop_times(
    df: pd.DataFrame,
    kisim: str,
    kisim_tezgah_sayilari: Dict[str, int]
) -> pd.DataFrame:
    """
    Belirli bir kısım için tezgah başına ortalama duruş sürelerini hesaplar.
    """
    logger.info(f"{kisim} için tezgah başına ortalama duruş süreleri hesaplanıyor...")
    
    # Eğer veri boşsa boş DataFrame döndür
    if df.empty:
        return pd.DataFrame(columns=['Duruş Adı', 'Süre (Saniye)', 'Süre (Dakika)'])
    
    # Belirli kısım için veri filtrele
    kisim_for_avg = df[df["KISIM"] == kisim].copy()
    
    if kisim_for_avg.empty:
        return pd.DataFrame(columns=['Duruş Adı', 'Süre (Saniye)', 'Süre (Dakika)'])
    
    # Tezgah sayısı
    tezgah_sayisi = kisim_tezgah_sayilari.get(kisim, 1)
    
    # Süreleri tezgah sayısına böl
    kisim_for_avg['Süre (Saniye)'] = (kisim_for_avg['Süre (Saniye)'] / tezgah_sayisi).astype(int)
    
    # Duruş adlarına göre süreleri topla
    result = kisim_for_avg.groupby('Duruş Adı')['Süre (Saniye)'].sum().reset_index()
    result = result.sort_values('Süre (Saniye)', ascending=False)
    
    # Saniyeden dakikaya çevir
    result = second_to_minute(result)
    
    return result