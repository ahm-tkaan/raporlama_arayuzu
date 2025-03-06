"""
Analiz işlemleri kontrolcüsü.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

# Mevcut analiz fonksiyonlarını içe aktar
from src.data_processing import (
    prepare_data_for_analysis, 
    get_latest_week_data,
    assign_kisim
)
from src.calculations import (
    calculate_stop_time_sum,
    calculate_part_machine_average_time,
    calculate_machine_stop_times,
    calculate_machine_stop_type_times,
    filter_sort_top_stops,
    calculate_part_average_stop_times
)
from src.visualization import (
    visualize_pie,
    visualize_weekly_comparison,
    visualize_bar,
    plot_bar,
    visualize_top_bottom_machines,
    generate_oee_visuals
)

# Tezgah listesi konfigürasyonunu içe aktar
from config.tezgah_listesi import KISIMLAR_DICT

# Loglama yapılandırması
logger = logging.getLogger(__name__)

class AnalysisWorker(QThread):
    """
    Analiz işlemlerini arka planda çalıştıran iş parçacığı sınıfı.
    """
    # Sinyaller
    progress_updated = pyqtSignal(int, str)
    analysis_completed = pyqtSignal(dict)
    analysis_error = pyqtSignal(str)
    
    def __init__(self, 
                durus_file: str, 
                calisma_file: str, 
                arizali_file: str,
                show_plots: bool,
                save_plots: bool,
                export_excel: bool,
                threshold: float):
        """
        Worker'ı başlat.
        
        Args:
            durus_file: Duruş verisi dosya yolu
            calisma_file: Çalışma süresi dosya yolu
            arizali_file: Arızalı tezgah listesi dosya yolu
            show_plots: Grafikleri gösterme bayrağı
            save_plots: Grafikleri kaydetme bayrağı
            export_excel: Excel'e aktarma bayrağı
            threshold: Pasta grafik eşik değeri
        """
        super().__init__()
        self.durus_file = durus_file
        self.calisma_file = calisma_file
        self.arizali_file = arizali_file
        self.show_plots = show_plots
        self.save_plots = save_plots
        self.export_excel = export_excel
        self.threshold = threshold
        
    def run(self):
        """
        Analiz işlemlerini çalıştır.
        """
        try:
            logger.info("Analiz işlemi başlıyor...")
            results = {}
            
            # İlerleme: Veri yükleme
            self.progress_updated.emit(10, "Veriler yükleniyor...")
            
            # Veriyi hazırla
            df, kisim_tezgah_sayilari, weeks = prepare_data_for_analysis(
                self.durus_file,
                self.calisma_file,
                self.arizali_file
            )
            
            # Son hafta verisini al
            latest_week_df = get_latest_week_data(df, weeks)
            
            # Excel'e dışa aktarma
            if self.export_excel:
                output_file = 'Son Hafta için Analiz Edilen Veriler.xlsx'
                latest_week_df.to_excel(output_file, index=False)
                logger.info(f"Son hafta verileri dışa aktarıldı: {output_file}")
                results['excel_file'] = output_file
            
            # İlerleme: Hesaplamalar
            self.progress_updated.emit(30, "Hesaplamalar yapılıyor...")
            
            # Duruş sürelerini hesapla
            toplam_sureler = calculate_stop_time_sum(latest_week_df)
            
            # Kısımlara göre tek tezgah için ortalama süreleri hesapla
            tezgah_basina_kisim_sureleri = calculate_part_machine_average_time(
                latest_week_df, 
                kisim_tezgah_sayilari
            )
            
            # İş merkezlerinin toplam duruş sürelerini hesapla
            tezgah_sureleri = calculate_machine_stop_times(latest_week_df)
            
            # İş merkezleri için duruş tipine göre süreleri hesapla
            tezgah_durus_ozet = calculate_machine_stop_type_times(latest_week_df)
            
            # Haftalar boyunca en büyük 10 duruşu hesapla (kısımlara göre)
            filtered_kisimlar = filter_sort_top_stops(df, weeks[0])
            
            # Haftalar boyunca en büyük 10 duruşu hesapla (tezgahlara göre)
            filtered_machine = filter_sort_top_stops(
                df, 
                weeks[0], 
                gozlemlenecek='İş Merkezi Kodu '
            )
            
            # Her kısım için tezgah başına ortalama duruş sürelerini hesapla
            kisim_avg_sureler = {}
            for kisim in kisim_tezgah_sayilari.keys():
                kisim_avg_sureler[kisim] = calculate_part_average_stop_times(
                    latest_week_df,
                    kisim,
                    kisim_tezgah_sayilari
                )
            
            # İlerleme: Görselleştirmeler
            self.progress_updated.emit(50, "Grafikler oluşturuluyor...")
            
            # Tüm tezgahlar için toplam duruş süreleri - pasta grafik
            visualize_pie(
                toplam_sureler, 
                threshold=self.threshold, 
                baslik="Tüm Tezgahlar Toplam",
                save=self.save_plots, 
                show=self.show_plots,
                category_column="Duruş Adı"
            )
            
            # Tezgah başına ortalama duruş süreleri - pasta grafik
            visualize_pie(
                tezgah_basina_kisim_sureleri, 
                baslik="Tüm Bölümler (Tezgah Başına)",
                save=self.save_plots, 
                show=self.show_plots,
                category_column="KISIM"
            )
            
            # Her kısım için tezgah başına ortalama duruş süreleri - pasta grafik
            for kisim, data in kisim_avg_sureler.items():
                visualize_pie(
                    data, 
                    baslik=f"{kisim} (Tezgah Başına)", 
                    threshold=self.threshold,
                    save=self.save_plots, 
                    show=self.show_plots,
                    category_column="Duruş Adı"
                )
            
            # İlerleme güncelle
            self.progress_updated.emit(70, "Tezgah grafikleri oluşturuluyor...")
            
            # En fazla duruş yapan tezgahlar - çubuk grafik
            visualize_bar(
                tezgah_sureleri, 
                colors="Reds", 
                bundan=-10, 
                baslik="En Fazla Duruş Yapan 10 Tezgah",
                save=self.save_plots, 
                show=self.show_plots
            )
            
            # En az duruş yapan tezgahlar - çubuk grafik
            visualize_bar(
                tezgah_sureleri, 
                colors="Greens", 
                bundan=0, 
                buna=10, 
                baslik="En Az Duruş Yapan 10 Tezgah",
                save=self.save_plots, 
                show=self.show_plots
            )
            
            # En az ve en çok duruş yapan tezgahlar karşılaştırması - çubuk grafik
            visualize_top_bottom_machines(
                tezgah_sureleri,
                save=self.save_plots, 
                show=self.show_plots
            )
            
            # Her tezgah için duruş nedenleri pasta grafikleri
            logger.info("Her tezgah için duruş nedenleri pasta grafikleri oluşturuluyor...")
            unique_machines = latest_week_df["İş Merkezi Kodu "].unique()
            
            # Her tezgah için duruş nedenleri - çubuk grafik
            plot_bar(
                tezgah_durus_ozet,
                save=self.save_plots, 
                show=self.show_plots
            )
            
            # 4 haftalık karşılaştırmalar
            self.progress_updated.emit(85, "Haftalık karşılaştırma grafikleri oluşturuluyor...")
            
            # 4 haftalık kısımlara göre duruş karşılaştırması - çubuk grafik
            visualize_weekly_comparison(
                filtered_kisimlar,
                egiklik=75,
                sort_by_last_week=True,
                target_week=weeks[0],
                save=self.save_plots, 
                show=self.show_plots
            )

            # 4 haftalık tezgahlara göre duruş karşılaştırması - çubuk grafik
            visualize_weekly_comparison(
                filtered_machine, 
                gozlem="İş Merkezi Kodu ", 
                egiklik=75,
                palet="Accent",
                sort_by_last_week=True,
                target_week=weeks[0],
                save=self.save_plots, 
                show=self.show_plots
            )
            
            # OEE ve diğer metrik görselleri
            generate_oee_visuals(df, weeks)
            
            # Sonuçları hazırla
            results.update({
                'df': df,
                'kisim_tezgah_sayilari': kisim_tezgah_sayilari,
                'weeks': weeks,
                'latest_week_df': latest_week_df,
                'toplam_sureler': toplam_sureler,
                'tezgah_basina_kisim_sureleri': tezgah_basina_kisim_sureleri,
                'tezgah_sureleri': tezgah_sureleri,
                'tezgah_durus_ozet': tezgah_durus_ozet,
                'kisim_avg_sureler': kisim_avg_sureler,
                'filtered_kisimlar': filtered_kisimlar,
                'filtered_machine': filtered_machine
            })
            
            # İlerleme: Tamamlandı
            self.progress_updated.emit(100, "Analiz tamamlandı!")
            
            # Analiz tamamlandı sinyali
            self.analysis_completed.emit(results)
            
            logger.info("Analiz işlemi tamamlandı.")
            
        except Exception as e:
            logger.error(f"Analiz hatası: {str(e)}", exc_info=True)
            self.analysis_error.emit(f"Analiz işlemi sırasında bir hata oluştu: {str(e)}")


class AnalysisController(QObject):
    """
    Analiz işlemleri kontrolcüsü sınıfı.
    """
    # Sinyaller
    analysis_progress = pyqtSignal(int, str)
    analysis_completed = pyqtSignal(dict)
    analysis_error = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
        Kontrolcüyü başlat.
        """
        super().__init__(parent)
        self.worker = None
    
    def start_analysis(self, 
                      durus_file: str, 
                      calisma_file: str, 
                      arizali_file: str,
                      show_plots: bool,
                      save_plots: bool,
                      export_excel: bool,
                      threshold: float):
        """
        Analiz işlemini başlat.
        
        Args:
            durus_file: Duruş verisi dosya yolu
            calisma_file: Çalışma süresi dosya yolu
            arizali_file: Arızalı tezgah listesi dosya yolu
            show_plots: Grafikleri gösterme bayrağı
            save_plots: Grafikleri kaydetme bayrağı
            export_excel: Excel'e aktarma bayrağı
            threshold: Pasta grafik eşik değeri
        """
        # Eğer zaten çalışan bir worker varsa durdur
        if self.worker is not None and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        # Yeni worker oluştur
        self.worker = AnalysisWorker(
            durus_file,
            calisma_file,
            arizali_file,
            show_plots,
            save_plots,
            export_excel,
            threshold
        )
        
        # Sinyalleri bağla
        self.worker.progress_updated.connect(self.analysis_progress.emit)
        self.worker.analysis_completed.connect(self.analysis_completed.emit)
        self.worker.analysis_error.connect(self.analysis_error.emit)
        
        # Worker'ı başlat
        self.worker.start()
        
        logger.info("Analiz işlemi başlatıldı.")
    
    def cancel_analysis(self):
        """
        Analiz işlemini iptal et.
        """
        if self.worker is not None and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            logger.info("Analiz işlemi iptal edildi.")