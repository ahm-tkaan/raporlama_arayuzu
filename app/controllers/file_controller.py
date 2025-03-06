"""
Dosya işlemleri kontrolcüsü.
"""

import os
import pandas as pd
from typing import List, Tuple, Optional, Dict
import logging

# Tezgah listesi konfigürasyonunu içe aktar
from config.tezgah_listesi import KISIMLAR_DICT

# Loglama yapılandırması
logger = logging.getLogger(__name__)

class FileController:
    """
    Dosya işlemleri kontrolcüsü sınıfı.
    """
    
    @staticmethod
    def load_durus_data(file_path: str) -> Tuple[bool, Optional[pd.DataFrame], str]:
        """
        Duruş verilerini yükler.
        
        Args:
            file_path: Excel dosyasının yolu
            
        Returns:
            Tuple[bool, Optional[pd.DataFrame], str]: Başarı durumu, yüklenmiş veri ve mesaj
        """
        try:
            logger.info(f"Duruş verisi yükleniyor: {file_path}")
            df = pd.read_excel(
                file_path, 
                usecols=["İş Merkezi Kodu ", "Duruş Adı", "Duruş Başlangıç Tarih", "Duruş Bitiş Tarih"]
            )
            logger.info(f"Duruş verisi yüklendi. Satır sayısı: {len(df)}")
            return True, df, f"Duruş verisi başarıyla yüklendi. {len(df)} satır okundu."
        except Exception as e:
            error_msg = f"Duruş verisi yükleme hatası: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    @staticmethod
    def load_calisma_data(file_path: str) -> Tuple[bool, Optional[pd.DataFrame], str]:
        """
        Çalışma süresi verilerini yükler.
        
        Args:
            file_path: Excel dosyasının yolu
            
        Returns:
            Tuple[bool, Optional[pd.DataFrame], str]: Başarı durumu, yüklenmiş veri ve mesaj
        """
        try:
            logger.info(f"Çalışma süresi verisi yükleniyor: {file_path}")
            df = pd.read_excel(
                file_path, 
                usecols=["Makina Kodu", "Tarih", "Çalışma Zamanı", "Planlı Duruş",
                        "Plansız Duruş", "Oee", "Performans", "Kullanılabilirlik", "Kalite"]
            )
            logger.info(f"Çalışma süresi verisi yüklendi. Satır sayısı: {len(df)}")
            return True, df, f"Çalışma süresi verisi başarıyla yüklendi. {len(df)} satır okundu."
        except Exception as e:
            error_msg = f"Çalışma süresi verisi yükleme hatası: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    @staticmethod
    def load_arizali_tezgahlar(file_path: str) -> Tuple[bool, List[str], str]:
        """
        Arızalı tezgah listesini dosyadan yükler.
        
        Args:
            file_path: Arızalı tezgahların bulunduğu dosya yolu
            
        Returns:
            Tuple[bool, List[str], str]: Başarı durumu, arızalı tezgah kodları listesi ve mesaj
        """
        try:
            logger.info(f"Arızalı tezgah listesi yükleniyor: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                arizali_tezgahlar = f.read().strip().split("\n")
            logger.info(f"Arızalı tezgah listesi yüklendi. Tezgah sayısı: {len(arizali_tezgahlar)}")
            return True, arizali_tezgahlar, f"Arızalı tezgah listesi başarıyla yüklendi. {len(arizali_tezgahlar)} tezgah okundu."
        except Exception as e:
            error_msg = f"Arızalı tezgah listesi yükleme hatası: {str(e)}"
            logger.error(error_msg)
            return False, [], error_msg
    
    @staticmethod
    def validate_data(durus_df: pd.DataFrame, calisma_df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Yüklenen verilerin doğruluğunu kontrol eder.
        
        Args:
            durus_df: Duruş verileri DataFrame'i
            calisma_df: Çalışma süresi verileri DataFrame'i
            
        Returns:
            Tuple[bool, str]: Doğruluk durumu ve mesaj
        """
        messages = []
        is_valid = True
        
        # Duruş verilerini kontrol et
        if durus_df is None or durus_df.empty:
            is_valid = False
            messages.append("Duruş verileri boş veya hatalı.")
        else:
            # Gerekli sütunları kontrol et
            required_columns = ["İş Merkezi Kodu ", "Duruş Adı", "Duruş Başlangıç Tarih", "Duruş Bitiş Tarih"]
            missing_columns = [col for col in required_columns if col not in durus_df.columns]
            
            if missing_columns:
                is_valid = False
                messages.append(f"Duruş verileri eksik sütunlar içeriyor: {', '.join(missing_columns)}")
        
        # Çalışma süresi verilerini kontrol et
        if calisma_df is None or calisma_df.empty:
            is_valid = False
            messages.append("Çalışma süresi verileri boş veya hatalı.")
        else:
            # Gerekli sütunları kontrol et
            required_columns = ["Makina Kodu", "Tarih", "Çalışma Zamanı", "Planlı Duruş",
                              "Plansız Duruş", "Oee", "Performans", "Kullanılabilirlik", "Kalite"]
            missing_columns = [col for col in required_columns if col not in calisma_df.columns]
            
            if missing_columns:
                is_valid = False
                messages.append(f"Çalışma süresi verileri eksik sütunlar içeriyor: {', '.join(missing_columns)}")
        
        # İlişkisel bütünlüğü kontrol et
        if is_valid:
            durus_machines = set(durus_df["İş Merkezi Kodu "].unique())
            calisma_machines = set(calisma_df["Makina Kodu"].unique())
            
            # En az bir makine kodunun her iki veri setinde de bulunması gerekir
            common_machines = durus_machines.intersection(calisma_machines)
            if not common_machines:
                is_valid = False
                messages.append("Duruş verileri ve çalışma süresi verileri arasında ortak makine kodu bulunamadı.")
            else:
                messages.append(f"{len(common_machines)} ortak makine kodu bulundu.")
        
        return is_valid, "\n".join(messages)
    
    @staticmethod
    def preview_data(df: pd.DataFrame, max_rows: int = 10) -> pd.DataFrame:
        """
        Verinin önizlemesini oluşturur.
        
        Args:
            df: Önizlemesi oluşturulacak DataFrame
            max_rows: Maksimum satır sayısı
            
        Returns:
            pd.DataFrame: Önizleme DataFrame'i
        """
        return df.head(max_rows)
    
    @staticmethod
    def export_to_excel(df: pd.DataFrame, file_path: str) -> Tuple[bool, str]:
        """
        Veriyi Excel dosyasına aktarır.
        
        Args:
            df: Dışa aktarılacak DataFrame
            file_path: Çıktı dosyası yolu
            
        Returns:
            Tuple[bool, str]: Başarı durumu ve mesaj
        """
        try:
            logger.info(f"Veri Excel'e aktarılıyor: {file_path}")
            df.to_excel(file_path, index=False)
            logger.info(f"Veri başarıyla Excel'e aktarıldı: {file_path}")
            return True, f"Veri başarıyla Excel'e aktarıldı: {file_path}"
        except Exception as e:
            error_msg = f"Excel'e aktarma hatası: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def get_report_files() -> List[Dict[str, str]]:
        """
        Mevcut rapor dosyalarını listeler.
        
        Returns:
            List[Dict[str, str]]: Rapor dosyaları listesi. Her öğe dosya adı, yolu ve türünü içerir.
        """
        report_files = []
        
        # Rapor dizinlerini tanımla
        report_dirs = {
            "Genel": "Raporlar/Genel",
            "Kısımlar": "Raporlar/Kısımlar",
            "Tezgahlar": "Raporlar/Tezgahlar",
            "Tee": "Raporlar/Tee"
        }
        
        for category, directory in report_dirs.items():
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.png') or file.endswith('.xlsx'):
                            file_path = os.path.join(root, file)
                            report_files.append({
                                "name": file,
                                "path": file_path,
                                "category": category,
                                "type": "Grafik" if file.endswith('.png') else "Veri",
                                "date": os.path.getmtime(file_path)
                            })
        
        # Tarihe göre sırala (en yeni en üstte)
        report_files.sort(key=lambda x: x["date"], reverse=True)
        
        return report_files