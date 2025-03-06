"""
Raporlar tab'ı.
"""

import os
import pandas as pd
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                           QPushButton, QTableView, QHeaderView, QFileDialog, QMessageBox,
                           QGroupBox, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap

import logging
logger = logging.getLogger(__name__)

class ReportsTab(QWidget):
    """
    Raporlar tab'ı sınıfı.
    """
    
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
        
        # Rapor listesi
        self.report_files = []
        
        # UI oluştur
        self._create_ui()
        
        # Rapor listesini yükle
        self.refresh_report_list()
        
    def _create_ui(self):
        """
        Kullanıcı arayüzünü oluştur.
        """
        # Ana layout
        main_layout = QHBoxLayout()
        
        # Sol panel - Rapor listesi
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Rapor listesi
        reports_group = QGroupBox("Raporlar")
        reports_layout = QVBoxLayout()
        
        self.report_table = QTableView()
        self.report_table.setSelectionBehavior(QTableView.SelectRows)
        self.report_table.setSelectionMode(QTableView.SingleSelection)
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.report_table.clicked.connect(self._report_selected)
        
        reports_layout.addWidget(self.report_table)
        
        # Aksiyon butonları
        buttons_layout = QHBoxLayout()
        
        self.view_button = QPushButton("Görüntüle")
        self.view_button.clicked.connect(self._view_selected_report)
        buttons_layout.addWidget(self.view_button)
        
        self.copy_button = QPushButton("Kopyala")
        self.copy_button.clicked.connect(self._copy_selected_report)
        buttons_layout.addWidget(self.copy_button)
        
        self.delete_button = QPushButton("Sil")
        self.delete_button.clicked.connect(self._delete_selected_report)
        buttons_layout.addWidget(self.delete_button)
        
        reports_layout.addLayout(buttons_layout)
        
        reports_group.setLayout(reports_layout)
        left_layout.addWidget(reports_group)
        
        # Yenile butonu
        self.refresh_button = QPushButton("Rapor Listesini Yenile")
        self.refresh_button.clicked.connect(self.refresh_report_list)
        left_layout.addWidget(self.refresh_button)
        
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(400)
        
        # Sağ panel - Önizleme
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        preview_group = QGroupBox("Önizleme")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("Önizleme için bir rapor seçin")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)
        
        right_panel.setLayout(right_layout)
        
        # Ana layout'a panelleri ekle
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
        
    def refresh_report_list(self):
        """
        Rapor listesini yenile.
        """
        # Rapor dosyalarını al
        self.report_files = self.file_controller.get_report_files()
        
        # Model oluştur
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Rapor Adı", "Kategori", "Tür", "Tarih"])
        
        # Rapor verilerini ekle
        for report in self.report_files:
            name_item = QStandardItem(report["name"])
            category_item = QStandardItem(report["category"])
            type_item = QStandardItem(report["type"])
            
            # Tarih formatla
            date_str = datetime.datetime.fromtimestamp(report["date"]).strftime("%d.%m.%Y %H:%M")
            date_item = QStandardItem(date_str)
            
            model.appendRow([name_item, category_item, type_item, date_item])
        
        # Proxy model ile sıralama
        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        
        # Tablo modeli olarak ayarla
        self.report_table.setModel(proxy_model)
        
        # Tarihe göre sırala (yeniden eskiye)
        self.report_table.sortByColumn(3, Qt.DescendingOrder)
        
        # Butonları devre dışı bırak
        self.view_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
        # Önizlemeyi temizle
        self.preview_label.setText("Önizleme için bir rapor seçin")
        self.preview_label.setPixmap(QPixmap())
    
    @pyqtSlot()
    def _report_selected(self):
        """
        Bir rapor seçildiğinde çağrılır.
        """
        # Butonları etkinleştir
        self.view_button.setEnabled(True)
        self.copy_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        
        # Seçilen raporu al
        selected_row = self.report_table.selectionModel().selectedRows()[0].row()
        proxy_model = self.report_table.model()
        source_row = proxy_model.mapToSource(proxy_model.index(selected_row, 0)).row()
        
        # Seçilen raporun verilerini al
        selected_report = self.report_files[source_row]
        
        # Önizleme göster
        if selected_report["type"] == "Grafik" and os.path.exists(selected_report["path"]):
            pixmap = QPixmap(selected_report["path"])
            self.preview_label.setPixmap(pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.preview_label.setText(f"Seçilen rapor: {selected_report['name']}\nTür: {selected_report['type']}")
            self.preview_label.setPixmap(QPixmap())
    
    @pyqtSlot()
    def _view_selected_report(self):
        """
        Seçilen raporu görüntüle.
        """
        if not self.report_table.selectionModel().hasSelection():
            return
        
        # Seçilen raporu al
        selected_row = self.report_table.selectionModel().selectedRows()[0].row()
        proxy_model = self.report_table.model()
        source_row = proxy_model.mapToSource(proxy_model.index(selected_row, 0)).row()
        
        # Seçilen raporun verilerini al
        selected_report = self.report_files[source_row]
        
        # Raporu aç
        if os.path.exists(selected_report["path"]):
            from PyQt5.QtGui import QDesktopServices
            from PyQt5.QtCore import QUrl
            QDesktopServices.openUrl(QUrl.fromLocalFile(selected_report["path"]))
        else:
            QMessageBox.warning(self, "Uyarı", f"Rapor dosyası bulunamadı: {selected_report['path']}")
    
    @pyqtSlot()
    def _copy_selected_report(self):
        """
        Seçilen raporu kopyala.
        """
        if not self.report_table.selectionModel().hasSelection():
            return
        
        # Seçilen raporu al
        selected_row = self.report_table.selectionModel().selectedRows()[0].row()
        proxy_model = self.report_table.model()
        source_row = proxy_model.mapToSource(proxy_model.index(selected_row, 0)).row()
        
        # Seçilen raporun verilerini al
        selected_report = self.report_files[source_row]
        
        # Hedef dosya adını al
        file_name = os.path.basename(selected_report["path"])
        file_ext = os.path.splitext(file_name)[1]
        
        file_filter = "Grafik Dosyaları (*.png)" if file_ext == ".png" else "Excel Dosyaları (*.xlsx)"
        
        target_path, _ = QFileDialog.getSaveFileName(
            self, "Raporu Farklı Kaydet", file_name, file_filter
        )
        
        if target_path:
            try:
                import shutil
                shutil.copy2(selected_report["path"], target_path)
                QMessageBox.information(self, "Bilgi", f"Rapor başarıyla kopyalandı: {target_path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Rapor kopyalanırken bir hata oluştu: {str(e)}")
    
    @pyqtSlot()
    def _delete_selected_report(self):
        """
        Seçilen raporu sil.
        """
        if not self.report_table.selectionModel().hasSelection():
            return
        
        # Seçilen raporu al
        selected_row = self.report_table.selectionModel().selectedRows()[0].row()
        proxy_model = self.report_table.model()
        source_row = proxy_model.mapToSource(proxy_model.index(selected_row, 0)).row()
        
        # Seçilen raporun verilerini al
        selected_report = self.report_files[source_row]
        
        # Onay kutusu göster
        reply = QMessageBox.question(
            self, 
            "Raporu Sil", 
            f"{selected_report['name']} raporunu silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists(selected_report["path"]):
                    os.remove(selected_report["path"])
                    QMessageBox.information(self, "Bilgi", f"Rapor başarıyla silindi: {selected_report['name']}")
                    
                    # Rapor listesini yenile
                    self.refresh_report_list()
                else:
                    QMessageBox.warning(self, "Uyarı", f"Rapor dosyası bulunamadı: {selected_report['path']}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Rapor silinirken bir hata oluştu: {str(e)}")
    
    def save_selected_report(self):
        """
        Seçilen raporu kaydet.
        """
        if not self.report_table.selectionModel().hasSelection():
            QMessageBox.information(self, "Bilgi", "Lütfen önce bir rapor seçin.")
            return
        
        self._copy_selected_report()