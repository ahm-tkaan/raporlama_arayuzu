"""
Veri yükleme tab'ı.
"""

import os
import pandas as pd
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                           QPushButton, QLineEdit, QFileDialog, QTableView, QMessageBox, 
                           QGroupBox, QSplitter, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QStandardItemModel, QStandardItem

import logging
logger = logging.getLogger(__name__)

class DataTab(QWidget):
    """
    Veri yükleme tab'ı sınıfı.
    """
    # Sinyaller
    data_loaded = pyqtSignal(object)
    
    def __init__(self, model, file_controller):
        """
        Tab'ı başlat.
        
        Args:
            model: Veri modeli
            file_controller: Dosya işlemleri kontrolcüsü
        """
        super().__init__()
        
        self.model = model
        self.file_controller = file_controller
        
        # Dosya yolları
        self.durus_file = ""
        self.calisma_file = ""
        self.arizali_file = ""
        
        # Önizleme verileri
        self.durus_preview = None
        self.calisma_preview = None
        
        # UI oluştur
        self._create_ui()
        
    def _create_ui(self):
        """
        Kullanıcı arayüzünü oluştur.
        """
        # Ana layout
        main_layout = QVBoxLayout()
        
        # Dosya seçim alanı
        file_group = QGroupBox("Veri Dosyaları")
        file_layout = QFormLayout()
        
        # Duruş verisi dosya seçimi
        durus_layout = QHBoxLayout()
        self.durus_line_edit = QLineEdit()
        self.durus_line_edit.setReadOnly(True)
        self.durus_line_edit.setPlaceholderText("Duruş verisi Excel dosyası seçin")
        self.durus_browse_button = QPushButton("Gözat")
        self.durus_browse_button.clicked.connect(self._browse_durus_file)
        durus_layout.addWidget(self.durus_line_edit)
        durus_layout.addWidget(self.durus_browse_button)
        file_layout.addRow("Duruş Verisi:", durus_layout)
        
        # Çalışma süresi dosya seçimi
        calisma_layout = QHBoxLayout()
        self.calisma_line_edit = QLineEdit()
        self.calisma_line_edit.setReadOnly(True)
        self.calisma_line_edit.setPlaceholderText("Çalışma süresi Excel dosyası seçin")
        self.calisma_browse_button = QPushButton("Gözat")
        self.calisma_browse_button.clicked.connect(self._browse_calisma_file)
        calisma_layout.addWidget(self.calisma_line_edit)
        calisma_layout.addWidget(self.calisma_browse_button)
        file_layout.addRow("Çalışma Süresi:", calisma_layout)
        
        # Arızalı tezgah listesi dosya seçimi
        arizali_layout = QHBoxLayout()
        self.arizali_line_edit = QLineEdit()
        self.arizali_line_edit.setReadOnly(True)
        self.arizali_line_edit.setPlaceholderText("Arızalı tezgah listesi metin dosyası seçin (opsiyonel)")
        self.arizali_browse_button = QPushButton("Gözat")
        self.arizali_browse_button.clicked.connect(self._browse_arizali_file)
        arizali_layout.addWidget(self.arizali_line_edit)
        arizali_layout.addWidget(self.arizali_browse_button)
        file_layout.addRow("Arızalı Tezgahlar:", arizali_layout)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # Veri yükleme butonu
        self.load_button = QPushButton("Verileri Yükle")
        self.load_button.setFixedHeight(40)
        self.load_button.clicked.connect(self._load_data)
        main_layout.addWidget(self.load_button)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Veri önizleme alanı
        preview_group = QGroupBox("Veri Önizlemesi")
        preview_layout = QVBoxLayout()
        
        # Splitter ile iki önizleme tablosunu ayır
        splitter = QSplitter(Qt.Vertical)
        
        # Duruş verisi önizleme
        durus_preview_group = QGroupBox("Duruş Verisi Önizlemesi")
        durus_preview_layout = QVBoxLayout()
        self.durus_table = QTableView()
        durus_preview_layout.addWidget(self.durus_table)
        durus_preview_group.setLayout(durus_preview_layout)
        
        # Çalışma süresi önizleme
        calisma_preview_group = QGroupBox("Çalışma Süresi Önizlemesi")
        calisma_preview_layout = QVBoxLayout()
        self.calisma_table = QTableView()
        calisma_preview_layout.addWidget(self.calisma_table)
        calisma_preview_group.setLayout(calisma_preview_layout)
        
        # Önizleme gruplarını splitter'a ekle
        splitter.addWidget(durus_preview_group)
        splitter.addWidget(calisma_preview_group)
        
        preview_layout.addWidget(splitter)
        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group, 1)
        
        self.setLayout(main_layout)
        
    @pyqtSlot()
    def _browse_durus_file(self):
        """
        Duruş verisi dosyasını seç.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Duruş Verisi Aç", "", "Excel Dosyaları (*.xlsx *.xls);;Tüm Dosyalar (*)"
        )
        
        if file_path:
            self.set_durus_file(file_path)
    
    @pyqtSlot()
    def _browse_calisma_file(self):
        """
        Çalışma süresi dosyasını seç.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Çalışma Süresi Aç", "", "Excel Dosyaları (*.xlsx *.xls);;Tüm Dosyalar (*)"
        )
        
        if file_path:
            self.set_calisma_file(file_path)
    
    @pyqtSlot()
    def _browse_arizali_file(self):
        """
        Arızalı tezgah listesi dosyasını seç.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Arızalı Tezgah Listesi Aç", "", "Metin Dosyaları (*.txt);;Tüm Dosyalar (*)"
        )
        
        if file_path:
            self.set_arizali_file(file_path)
    
    def set_durus_file(self, file_path):
        """
        Duruş verisi dosya yolunu ayarla ve önizleme oluştur.
        
        Args:
            file_path: Dosya yolu
        """
        self.durus_file = file_path
        self.durus_line_edit.setText(file_path)
        
        # Önizleme yükle
        success, df, message = self.file_controller.load_durus_data(file_path)
        
        if success:
            self.durus_preview = df
            self._update_durus_preview()
        else:
            QMessageBox.warning(self, "Uyarı", message)
    
    def set_calisma_file(self, file_path):
        """
        Çalışma süresi dosya yolunu ayarla ve önizleme oluştur.
        
        Args:
            file_path: Dosya yolu
        """
        self.calisma_file = file_path
        self.calisma_line_edit.setText(file_path)
        
        # Önizleme yükle
        success, df, message = self.file_controller.load_calisma_data(file_path)
        
        if success:
            self.calisma_preview = df
            self._update_calisma_preview()
        else:
            QMessageBox.warning(self, "Uyarı", message)
    
    def set_arizali_file(self, file_path):
        """
        Arızalı tezgah listesi dosya yolunu ayarla.
        
        Args:
            file_path: Dosya yolu
        """
        self.arizali_file = file_path
        self.arizali_line_edit.setText(file_path)
    
    def _update_durus_preview(self):
        """
        Duruş verisi önizleme tablosunu güncelle.
        """
        if self.durus_preview is not None:
            # Model oluştur
            model = QStandardItemModel()
            
            # Başlıkları ayarla
            model.setHorizontalHeaderLabels(self.durus_preview.columns)
            
            # Verileri ekle
            preview_data = self.durus_preview.head(10)
            for i, row in enumerate(preview_data.values):
                items = [QStandardItem(str(cell)) for cell in row]
                model.appendRow(items)
            
            # Tabloyu güncelle
            self.durus_table.setModel(model)
            self.durus_table.resizeColumnsToContents()
    
    def _update_calisma_preview(self):
        """
        Çalışma süresi önizleme tablosunu güncelle.
        """
        if self.calisma_preview is not None:
            # Model oluştur
            model = QStandardItemModel()
            
            # Başlıkları ayarla
            model.setHorizontalHeaderLabels(self.calisma_preview.columns)
            
            # Verileri ekle
            preview_data = self.calisma_preview.head(10)
            for i, row in enumerate(preview_data.values):
                items = [QStandardItem(str(cell)) for cell in row]
                model.appendRow(items)
            
            # Tabloyu güncelle
            self.calisma_table.setModel(model)
            self.calisma_table.resizeColumnsToContents()
    
    @pyqtSlot()
    def _load_data(self):
        """
        Veri dosyalarını yükle.
        """
        # Dosya yollarını kontrol et
        if not self.durus_file or not os.path.exists(self.durus_file):
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir duruş verisi dosyası seçin!")
            return
        
        if not self.calisma_file or not os.path.exists(self.calisma_file):
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir çalışma süresi dosyası seçin!")
            return
        
        # İlerleme çubuğunu göster
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        
        # Verileri yükle
        durus_success, durus_df, durus_message = self.file_controller.load_durus_data(self.durus_file)
        if not durus_success:
            QMessageBox.critical(self, "Hata", durus_message)
            self.progress_bar.setVisible(False)
            return
        
        self.progress_bar.setValue(30)
        
        calisma_success, calisma_df, calisma_message = self.file_controller.load_calisma_data(self.calisma_file)
        if not calisma_success:
            QMessageBox.critical(self, "Hata", calisma_message)
            self.progress_bar.setVisible(False)
            return
        
        self.progress_bar.setValue(50)
        
        # Arızalı tezgah dosyasını yükle (varsa)
        arizali_tezgahlar = []
        if self.arizali_file and os.path.exists(self.arizali_file):
            arizali_success, arizali_tezgahlar, arizali_message = self.file_controller.load_arizali_tezgahlar(self.arizali_file)
            if not arizali_success:
                QMessageBox.warning(self, "Uyarı", arizali_message)
        
        self.progress_bar.setValue(70)
        
        # Verileri doğrula
        is_valid, validation_message = self.file_controller.validate_data(durus_df, calisma_df)
        if not is_valid:
            QMessageBox.critical(self, "Doğrulama Hatası", validation_message)
            self.progress_bar.setVisible(False)
            return
        
        self.progress_bar.setValue(90)
        
        # Verileri modele kaydet
        self.model.set_durus_data(durus_df)
        self.model.set_calisma_data(calisma_df)
        self.model.set_arizali_tezgahlar(arizali_tezgahlar)
        
        self.progress_bar.setValue(100)
        
        # Veri yükleme sinyali gönder
        self.data_loaded.emit({
            'durus_file': self.durus_file,
            'calisma_file': self.calisma_file,
            'arizali_file': self.arizali_file
        })
        
        # İlerleme çubuğunu gizle
        self.progress_bar.setVisible(False)
        
        # Bilgi mesajı göster
        QMessageBox.information(self, "Veri Yükleme", "Veriler başarıyla yüklendi! Analiz tabına geçebilirsiniz.")
    
    def clear_fields(self):
        """
        Tüm alanları temizle.
        """
        self.durus_file = ""
        self.calisma_file = ""
        self.arizali_file = ""
        
        self.durus_line_edit.clear()
        self.calisma_line_edit.clear()
        self.arizali_line_edit.clear()
        
        self.durus_preview = None
        self.calisma_preview = None
        
        # Tabloları temizle
        self.durus_table.setModel(None)
        self.calisma_table.setModel(None)