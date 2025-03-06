"""
Ana pencere bileşeni.
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QStatusBar, QAction, 
                           QMenuBar, QToolBar, QMessageBox, QFileDialog)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, pyqtSlot

from app.models.analysis_model import AnalysisModel
from app.controllers.file_controller import FileController
from app.controllers.analysis_controller import AnalysisController
from app.views.tabs.data_tab import DataTab
from app.views.tabs.analysis_tab import AnalysisTab
from app.views.tabs.reports_tab import ReportsTab
from app.views.tabs.settings_tab import SettingsTab

import logging
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    Ana pencere sınıfı.
    """
    
    def __init__(self):
        """
        Ana pencereyi başlat.
        """
        super().__init__()
        
        # Model ve kontrolcüleri oluştur
        self.model = AnalysisModel()
        self.file_controller = FileController()
        self.analysis_controller = AnalysisController()
        
        # Pencere özelliklerini ayarla
        self.setWindowTitle("Tezgah Duruş Analizi")
        self.setMinimumSize(1024, 768)
        
        # Menü ve araç çubuklarını oluştur
        self._create_menu_bar()
        self._create_tool_bar()
        
        # Tab widget'ı oluştur
        self.tab_widget = QTabWidget()
        
        # Tabları oluştur
        self.data_tab = DataTab(self.model, self.file_controller)
        self.analysis_tab = AnalysisTab(self.model, self.analysis_controller)
        self.reports_tab = ReportsTab(self.model, self.file_controller)
        self.settings_tab = SettingsTab(self.model)
        
        # Tabları ekle
        self.tab_widget.addTab(self.data_tab, "Veri Yükleme")
        self.tab_widget.addTab(self.analysis_tab, "Analiz")
        self.tab_widget.addTab(self.reports_tab, "Raporlar")
        self.tab_widget.addTab(self.settings_tab, "Ayarlar")
        
        # Merkez widget olarak ayarla
        self.setCentralWidget(self.tab_widget)
        
        # Durum çubuğunu oluştur
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Programa hoş geldiniz!")
        
        # Sinyal bağlantıları
        self._connect_signals()
        
        logger.info("Ana pencere oluşturuldu.")
    
    def _create_menu_bar(self):
        """
        Menü çubuğunu oluştur.
        """
        menu_bar = self.menuBar()
        
        # Dosya menüsü
        file_menu = menu_bar.addMenu("Dosya")
        
        # Dosya - Aç
        open_durus_action = QAction("Duruş Verisi Aç", self)
        open_durus_action.setShortcut(QKeySequence.Open)
        open_durus_action.triggered.connect(self._open_durus_file)
        file_menu.addAction(open_durus_action)
        
        open_calisma_action = QAction("Çalışma Süresi Aç", self)
        open_calisma_action.triggered.connect(self._open_calisma_file)
        file_menu.addAction(open_calisma_action)
        
        open_arizali_action = QAction("Arızalı Tezgah Listesi Aç", self)
        open_arizali_action.triggered.connect(self._open_arizali_file)
        file_menu.addAction(open_arizali_action)
        
        file_menu.addSeparator()
        
        # Dosya - Kaydet
        save_action = QAction("Rapor Kaydet", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save_report)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Dosya - Çıkış
        exit_action = QAction("Çıkış", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Düzenle menüsü
        edit_menu = menu_bar.addMenu("Düzenle")
        
        # Düzenle - Temizle
        clear_action = QAction("Verileri Temizle", self)
        clear_action.triggered.connect(self._clear_data)
        edit_menu.addAction(clear_action)
        
        # Görünüm menüsü
        view_menu = menu_bar.addMenu("Görünüm")
        
        # Görünüm - Yenile
        refresh_action = QAction("Raporları Yenile", self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self._refresh_reports)
        view_menu.addAction(refresh_action)
        
        # Yardım menüsü
        help_menu = menu_bar.addMenu("Yardım")
        
        # Yardım - Hakkında
        about_action = QAction("Hakkında", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_tool_bar(self):
        """
        Araç çubuğunu oluştur.
        """
        tool_bar = QToolBar("Ana Araç Çubuğu")
        tool_bar.setMovable(False)
        self.addToolBar(tool_bar)
        
        # Dosya Aç
        open_action = QAction("Duruş Verisi Aç", self)
        open_action.triggered.connect(self._open_durus_file)
        tool_bar.addAction(open_action)
        
        # Analiz Başlat
        analyze_action = QAction("Analiz Başlat", self)
        analyze_action.triggered.connect(self._start_analysis)
        tool_bar.addAction(analyze_action)
        
        # Rapor Görüntüle
        view_report_action = QAction("Raporları Görüntüle", self)
        view_report_action.triggered.connect(self._view_reports)
        tool_bar.addAction(view_report_action)
    
    def _connect_signals(self):
        """
        Sinyal bağlantılarını oluştur.
        """
        # Analiz kontrolcüsü sinyalleri
        self.analysis_controller.analysis_progress.connect(self._update_analysis_progress)
        self.analysis_controller.analysis_completed.connect(self._analysis_completed)
        self.analysis_controller.analysis_error.connect(self._show_error)
        
        # Tab sinyalleri
        self.data_tab.data_loaded.connect(self._data_loaded)
        self.analysis_tab.analysis_started.connect(self._analysis_started)
        
    @pyqtSlot()
    def _open_durus_file(self):
        """
        Duruş verisi dosyasını aç.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Duruş Verisi Aç", "", "Excel Dosyaları (*.xlsx *.xls);;Tüm Dosyalar (*)"
        )
        
        if file_path:
            self.data_tab.set_durus_file(file_path)
            self.status_bar.showMessage(f"Duruş verisi dosyası seçildi: {file_path}")
    
    @pyqtSlot()
    def _open_calisma_file(self):
        """
        Çalışma süresi dosyasını aç.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Çalışma Süresi Aç", "", "Excel Dosyaları (*.xlsx *.xls);;Tüm Dosyalar (*)"
        )
        
        if file_path:
            self.data_tab.set_calisma_file(file_path)
            self.status_bar.showMessage(f"Çalışma süresi dosyası seçildi: {file_path}")
    
    @pyqtSlot()
    def _open_arizali_file(self):
        """
        Arızalı tezgah listesi dosyasını aç.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Arızalı Tezgah Listesi Aç", "", "Metin Dosyaları (*.txt);;Tüm Dosyalar (*)"
        )
        
        if file_path:
            self.data_tab.set_arizali_file(file_path)
            self.status_bar.showMessage(f"Arızalı tezgah listesi dosyası seçildi: {file_path}")
    
    @pyqtSlot()
    def _save_report(self):
        """
        Rapor kaydet.
        """
        self.tab_widget.setCurrentIndex(2)  # Raporlar tabına geç
        self.reports_tab.save_selected_report()
    
    @pyqtSlot()
    def _clear_data(self):
        """
        Verileri temizle.
        """
        reply = QMessageBox.question(
            self, 
            "Verileri Temizle", 
            "Tüm yüklenen veriler ve sonuçlar temizlenecek. Emin misiniz?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.model.clear()
            self.data_tab.clear_fields()
            self.analysis_tab.clear_results()
            self.reports_tab.refresh_report_list()
            self.status_bar.showMessage("Tüm veriler ve sonuçlar temizlendi.")
    
    @pyqtSlot()
    def _refresh_reports(self):
        """
        Raporları yenile.
        """
        self.reports_tab.refresh_report_list()
        self.status_bar.showMessage("Rapor listesi yenilendi.")
    
    @pyqtSlot()
    def _show_about(self):
        """
        Hakkında mesajını göster.
        """
        QMessageBox.about(
            self, 
            "Tezgah Duruş Analizi Hakkında", 
            "Tezgah Duruş Analizi v1.0.0\n\n"
            "Tezgah duruş verilerinin analizi ve görselleştirilmesi için geliştirilmiş bir uygulamadır."
        )
    
    @pyqtSlot()
    def _start_analysis(self):
        """
        Analiz işlemini başlat.
        """
        self.tab_widget.setCurrentIndex(1)  # Analiz tabına geç
        self.analysis_tab.start_analysis()
    
    @pyqtSlot()
    def _view_reports(self):
        """
        Raporları görüntüle.
        """
        self.tab_widget.setCurrentIndex(2)  # Raporlar tabına geç
        self.reports_tab.refresh_report_list()
    
    @pyqtSlot(object)
    def _data_loaded(self, data_info):
        """
        Veri yükleme tamamlandığında çağrılır.
        
        Args:
            data_info: Yüklenen veri bilgileri
        """
        self.status_bar.showMessage("Veriler başarıyla yüklendi!")
        # Analiz tabına geç
        self.tab_widget.setCurrentIndex(1)
    
    @pyqtSlot()
    def _analysis_started(self):
        """
        Analiz başladığında çağrılır.
        """
        self.status_bar.showMessage("Analiz işlemi başlatıldı...")
    
    @pyqtSlot(int, str)
    def _update_analysis_progress(self, progress, message):
        """
        Analiz ilerleme durumunu güncelle.
        
        Args:
            progress: İlerleme yüzdesi
            message: İlerleme mesajı
        """
        self.status_bar.showMessage(f"Analiz: {progress}% - {message}")
    
    @pyqtSlot(dict)
    def _analysis_completed(self, results):
        """
        Analiz tamamlandığında çağrılır.
        
        Args:
            results: Analiz sonuçları
        """
        self.status_bar.showMessage("Analiz başarıyla tamamlandı!")
        # Raporlar tabına geç
        self.tab_widget.setCurrentIndex(2)
        self.reports_tab.refresh_report_list()
    
    @pyqtSlot(str)
    def _show_error(self, error_message):
        """
        Hata mesajı göster.
        
        Args:
            error_message: Hata mesajı
        """
        QMessageBox.critical(self, "Hata", error_message)
        self.status_bar.showMessage(f"Hata: {error_message}")
    
    def closeEvent(self, event):
        """
        Pencere kapatma olayı.
        
        Args:
            event: Kapatma olayı
        """
        reply = QMessageBox.question(
            self, 
            "Çıkış", 
            "Programdan çıkmak istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()