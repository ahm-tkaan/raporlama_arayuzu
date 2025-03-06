"""
Yardımcı fonksiyonlar.
"""

import os
import sys
import time
import datetime
import logging
from typing import Dict, List, Tuple, Optional, Union

logger = logging.getLogger(__name__)

def ensure_dir(directory: str) -> bool:
    """
    Belirtilen dizinin var olduğundan emin olur, yoksa oluşturur.
    
    Args:
        directory: Oluşturulacak dizin yolu
        
    Returns:
        bool: Başarı durumu
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Dizin oluşturuldu: {directory}")
        return True
    except Exception as e:
        logger.error(f"Dizin oluşturma hatası: {str(e)}")
        return False

def format_time(seconds: float) -> str:
    """
    Saniye cinsinden zamanı biçimlendirir.
    
    Args:
        seconds: Saniye cinsinden zaman
        
    Returns:
        str: Biçimlendirilmiş zaman
    """
    if seconds < 60:
        return f"{seconds:.2f} saniye"
    elif seconds < 3600:
        minutes = seconds // 60
        remain_seconds = seconds % 60
        return f"{int(minutes)} dakika {int(remain_seconds)} saniye"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)} saat {int(minutes)} dakika"

def sanitize_filename(filename: str) -> str:
    """
    Dosya adını geçersiz karakterlerden arındırır.
    
    Args:
        filename: Dosya adı
        
    Returns:
        str: Geçerli dosya adı
    """
    # Yasaklı karakterler
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    
    # Karakterleri değiştir
    result = filename
    for char in invalid_chars:
        result = result.replace(char, '_')
    
    return result

def bytes_to_human_readable(size_bytes: int) -> str:
    """
    Byte cinsinden boyutu insan okunabilir formata dönüştürür.
    
    Args:
        size_bytes: Byte cinsinden boyut
        
    Returns:
        str: İnsan okunabilir boyut
    """
    if size_bytes == 0:
        return "0 B"
    
    # Birimler
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    
    # Birim indeksi
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {units[i]}"

def date_to_week_number(date: datetime.date) -> int:
    """
    Tarihten hafta numarasını döndürür.
    
    Args:
        date: Tarih
        
    Returns:
        int: Hafta numarası
    """
    return date.isocalendar()[1]

def get_file_stats(file_path: str) -> Dict:
    """
    Dosya istatistiklerini döndürür.
    
    Args:
        file_path: Dosya yolu
        
    Returns:
        Dict: Dosya istatikleri
    """
    stats = {}
    
    try:
        if os.path.exists(file_path):
            file_stat = os.stat(file_path)
            
            stats['size'] = bytes_to_human_readable(file_stat.st_size)
            stats['created'] = datetime.datetime.fromtimestamp(file_stat.st_ctime).strftime('%d.%m.%Y %H:%M:%S')
            stats['modified'] = datetime.datetime.fromtimestamp(file_stat.st_mtime).strftime('%d.%m.%Y %H:%M:%S')
            stats['extension'] = os.path.splitext(file_path)[1]
            
            return stats
        else:
            return {'error': 'Dosya bulunamadı'}
    except Exception as e:
        logger.error(f"Dosya istatistikleri alınırken hata oluştu: {str(e)}")
        return {'error': str(e)}

def get_application_path() -> str:
    """
    Uygulama dizinini döndürür.
    
    Returns:
        str: Uygulama dizini
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # Normal Python
        return os.path.dirname(os.path.abspath(__file__))