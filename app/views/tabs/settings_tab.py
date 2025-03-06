"""
Ayarlar tab'ı.
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                           QPushButton, QLineEdit, QCheckBox, QSpinBox, QDoubleSpinBox,
                           QGroupBox, QComboBox, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

from config.settings import VISUALIZATION_SETTINGS

import logging
logger = logging.getLogger(__name__)

class SettingsTab(QWidget):
    """
    Ayarlar tab'ı sınıfı.
    """
    # Sinyaller
    settings_changed = pyqtSignal()
    
    def __init__(self, model):
        """
        Tab'ı başlat.
        
        Args:
            model: Veri modeli
        """
        super().__init__()
        
        self.model = model
        
        # UI oluştur
        self._create_ui()
        
        # Varsayılan ayarları yükle
        self._load_default_settings()
        
    def _create_ui(self):
        """
        Kullanıcı arayüzünü oluştur.
        """
        # Ana layout
        main_layout = QVBoxLayout()
        
        # Genel ayarlar
        general_group = QGroupBox("Genel Ayarlar")
        general_layout = QFormLayout()
        
        # Çıktı dizini
        output_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setReadOnly(True)
        self.output_browse_button = QPushButton("Gözat")
        self.output_browse_button.clicked.connect(self._browse_output_dir)
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(self.output_browse_button)
        general_layout.addRow("Çıktı Dizini:", output_layout)
        
        # Eşik değeri
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.1, 20.0)
        self.threshold_spin.setValue(3.0)
        self.threshold_spin.setSingleStep(0.1)
        self.threshold_spin.setSuffix("%")
        general_layout.addRow("Pasta Grafik Eşik Değeri:", self.threshold_spin)
        
        general_group.setLayout(general_layout)
        main_layout.addWidget(general_group)
        
        # Görselleştirme ayarları
        visual_group = QGroupBox("Görselleştirme Ayarları")
        visual_layout = QFormLayout()
        
        # DPI
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 600)
        self.dpi_spin.setValue(300)
        visual_layout.addRow("DPI:", self.dpi_spin)
        
        # Grafik boyutu
        figsize_layout = QHBoxLayout()
        self.figsize_width_spin = QSpinBox()
        self.figsize_width_spin.setRange(6, 24)
        self.figsize_width_spin.setValue(12)
        
        self.figsize_height_spin = QSpinBox()
        self.figsize_height_spin.setRange(4, 18)
        self.figsize_height_spin.setValue(8)
        
        figsize_layout.addWidget(self.figsize_width_spin)
        figsize_layout.addWidget(QLabel("x"))
        figsize_layout.addWidget(self.figsize_height_spin)
        
        visual_layout.addRow("Grafik Boyutu (inç):", figsize_layout)
        
        # Renk paleti
        self.color_palette_combo = QComboBox()
        self.color_palette_combo.addItems([
            "Pastel2", "tab20", "Accent", "Set1", "Set2", "Set3", "tab10", "Paired"
        ])
        visual_layout.addRow("Renk Paleti:", self.color_palette_combo)
        
        visual_group.setLayout(visual_layout)
        main_layout.addWidget(visual_group)
        
        # Butonlar
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Ayarları Kaydet")
        self.save_button.clicked.connect(self._save_settings)
        buttons_layout.addWidget(self.save_button)
        
        self.reset_button = QPushButton("Varsayılana Sıfırla")
        self.reset_button.clicked.connect(self._load_default_settings)
        buttons_layout.addWidget(self.reset_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Boşluk ekle
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
    def _browse_output_dir(self):
        """
        Çıktı dizinini seç.
        """
        dir_path = QFileDialog.getExistingDirectory(
            self, "Çıktı Dizini Seç", self.output_dir_edit.text()
        )
        
        if dir_path:
            self.output_dir_edit.setText(dir_path)
    
    def _load_default_settings(self):
        """
        Varsayılan ayarları yükle.
        """
        # Çıktı dizini
        self.output_dir_edit.setText("Raporlar")
        
        # Eşik değeri
        self.threshold_spin.setValue(VISUALIZATION_SETTINGS["default_threshold"])
        
        # DPI
        self.dpi_spin.setValue(VISUALIZATION_SETTINGS["dpi"])
        
        # Grafik boyutu
        figsize = VISUALIZATION_SETTINGS["default_figsize"]
        self.figsize_width_spin.setValue(figsize[0])
        self.figsize_height_spin.setValue(figsize[1])
        
        # Renk paleti
        self.color_palette_combo.setCurrentText("Pastel2")
    
    def _save_settings(self):
        """
        Ayarları kaydet.
        """
        try:
            # Çıktı dizini oluştur
            output_dir = self.output_dir_edit.text()
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Ayarları güncelle
            VISUALIZATION_SETTINGS["default_threshold"] = self.threshold_spin.value()
            VISUALIZATION_SETTINGS["dpi"] = self.dpi_spin.value()
            VISUALIZATION_SETTINGS["default_figsize"] = (
                self.figsize_width_spin.value(),
                self.figsize_height_spin.value()
            )
            
            # Değişiklik sinyali gönder
            self.settings_changed.emit()
            
            QMessageBox.information(self, "Bilgi", "Ayarlar başarıyla kaydedildi.")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ayarlar kaydedilirken bir hata oluştu: {str(e)}")