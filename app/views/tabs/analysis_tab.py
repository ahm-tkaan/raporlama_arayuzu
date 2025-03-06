"""
Analiz tab'ı.
"""

import os
import pandas as pd

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                           QPushButton, QLineEdit, QCheckBox, QSpinBox, QDoubleSpinBox,
                           QGroupBox, QProgressBar, QComboBox, QTextEdit, QScrollArea,
                           QSizePolicy, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QPixmap

from app.widgets.chart_widgets import PieChartWidget
import logging
logger = logging.getLogger(__name__)

class AnalysisTab(QWidget):
    """
    Analiz tab'ı sınıfı.
    """
    # Sinyaller
    analysis_started = pyqtSignal()
    
    def __init__(self, model, analysis_controller):
        """
        Tab'ı başlat.
        
        Args:
            model: Veri modeli
            analysis_controller: Analiz işlemleri kontrolcüsü
        """
        super().__init__()
        
        self.model = model
        self.analysis_controller = analysis_controller
        
        # UI oluştur
        self._create_ui()
        
        # Sinyal bağlantıları
        self._connect_signals()
        
    def _create_ui(self):
        """
        Kullanıcı arayüzünü oluştur.
        """
        # Ana layout
        main_layout = QHBoxLayout()
        
        # Sol panel - Analiz parametreleri
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Analiz seçenekleri
        options_group = QGroupBox("Analiz Seçenekleri")
        options_layout = QVBoxLayout()
        
        # Grafikleri göster
        self.show_plots_cb = QCheckBox("Grafikleri göster")
        options_layout.addWidget(self.show_plots_cb)
        
        # Grafikleri kaydet
        self.save_plots_cb = QCheckBox("Grafikleri kaydet")
        self.save_plots_cb.setChecked(True)
        options_layout.addWidget(self.save_plots_cb)
        
        # Excel'e aktar
        self.export_excel_cb = QCheckBox("Excel'e aktar")
        options_layout.addWidget(self.export_excel_cb)
        
        options_group.setLayout(options_layout)
        left_layout.addWidget(options_group)
        
        # Analiz parametreleri
        params_group = QGroupBox("Analiz Parametreleri")
        params_layout = QFormLayout()
        
        # Eşik değeri
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.1, 20.0)
        self.threshold_spin.setValue(3.0)
        self.threshold_spin.setSingleStep(0.1)
        self.threshold_spin.setSuffix("%")
        params_layout.addRow("Eşik Değeri:", self.threshold_spin)
        
        # Hedef hafta
        self.target_week_combo = QComboBox()
        self.target_week_combo.addItem("Son Hafta", -1)
        params_layout.addRow("Hedef Hafta:", self.target_week_combo)
        
        params_group.setLayout(params_layout)
        left_layout.addWidget(params_group)
        
        # Analiz başlatma
        self.analyze_button = QPushButton("Analizi Başlat")
        self.analyze_button.setFixedHeight(40)
        self.analyze_button.clicked.connect(self._start_analysis)
        left_layout.addWidget(self.analyze_button)
        
        # İptal butonu
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_analysis)
        left_layout.addWidget(self.cancel_button)
        
        # İlerleme çubuğu
        self.progress_layout = QVBoxLayout()
        
        self.progress_label = QLabel("İlerleme: ")
        self.progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_layout.addWidget(self.progress_bar)
        
        progress_frame = QFrame()
        progress_frame.setLayout(self.progress_layout)
        progress_frame.setFrameShape(QFrame.StyledPanel)
        
        left_layout.addWidget(progress_frame)
        
        # Sonuç bilgileri
        results_group = QGroupBox("Analiz Sonuçları")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        left_layout.addWidget(results_group)
        
        # Panel düzeni tamamla
        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(300)
        
        # Sağ panel - Grafikler
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        
        # İçerik widget'ı
        self.charts_widget = QWidget()
        self.charts_layout = QVBoxLayout()
        
        # Boş bir mesaj ekle
        self.empty_label = QLabel("Analiz sonuçları burada gösterilecek.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.charts_layout.addWidget(self.empty_label)
        
        # Çubuk grafiği önizleme etiketi
        self.bar_chart_label = QLabel()
        self.bar_chart_label.setVisible(False)
        self.charts_layout.addWidget(self.bar_chart_label)
        
        # Pasta grafiği önizleme widget'ı
        self.pie_chart_widget = PieChartWidget()
        self.pie_chart_widget.setVisible(False)
        self.charts_layout.addWidget(self.pie_chart_widget)
        
        self.charts_layout.addStretch()
        self.charts_widget.setLayout(self.charts_layout)
        
        right_panel.setWidget(self.charts_widget)
        
        # Ana layout'a panelleri ekle
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.setLayout(main_layout)
    
    def _connect_signals(self):
        """
        Sinyal bağlantılarını oluştur.
        """
        # Analiz kontrolcüsü sinyalleri
        self.analysis_controller.analysis_progress.connect(self._update_progress)
        self.analysis_controller.analysis_completed.connect(self._analysis_completed)
        self.analysis_controller.analysis_error.connect(self._analysis_error)
    
    @pyqtSlot()
    def _start_analysis(self):
        """
        Analiz işlemini başlat.
        """
        # Veri yükleme kontrolü
        if self.model.durus_data is None or self.model.calisma_data is None:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Uyarı", "Analiz başlatılmadan önce veri yüklenmesi gerekiyor!")
            return
        
        # Butonları güncelle
        self.analyze_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        
        # İlerleme çubuğunu sıfırla
        self.progress_bar.setValue(0)
        self.progress_label.setText("İlerleme: Başlatılıyor...")
        
        # Analiz sinyali gönder
        self.analysis_started.emit()
        
        # Analiz parametrelerini hazırla
        durus_file = self.model.durus_data.to_excel("temp_durus.xlsx", index=False)
        calisma_file = self.model.calisma_data.to_excel("temp_calisma.xlsx", index=False)
        
        arizali_file = None
        if self.model.arizali_tezgahlar:
            with open("temp_arizali.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(self.model.arizali_tezgahlar))
            arizali_file = "temp_arizali.txt"
        
        # Analizi başlat
        self.analysis_controller.start_analysis(
            durus_file="temp_durus.xlsx",
            calisma_file="temp_calisma.xlsx",
            arizali_file=arizali_file,
            show_plots=self.show_plots_cb.isChecked(),
            save_plots=self.save_plots_cb.isChecked(),
            export_excel=self.export_excel_cb.isChecked(),
            threshold=self.threshold_spin.value()
        )
    
    @pyqtSlot()
    def _cancel_analysis(self):
        """
        Analiz işlemini iptal et.
        """
        self.analysis_controller.cancel_analysis()
        
        # Butonları güncelle
        self.analyze_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        # İlerleme çubuğunu güncelle
        self.progress_label.setText("İlerleme: İptal edildi")
    
    @pyqtSlot(int, str)
    def _update_progress(self, progress, message):
        """
        İlerleme durumunu güncelle.
        
        Args:
            progress: İlerleme yüzdesi
            message: İlerleme mesajı
        """
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"İlerleme: {progress}% - {message}")
    
    @pyqtSlot(dict)
    def _analysis_completed(self, results):
        """
        Analiz tamamlandığında çağrılır.
        
        Args:
            results: Analiz sonuçları
        """
        # Butonları güncelle
        self.analyze_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        # İlerleme çubuğunu güncelle
        self.progress_bar.setValue(100)
        self.progress_label.setText("İlerleme: Tamamlandı")
        
        # Sonuçları göster
        self._show_results(results)
        
        # Geçici dosyaları temizle
        self._clean_temp_files()
    
    @pyqtSlot(str)
    def _analysis_error(self, error_message):
        """
        Analiz hatası oluştuğunda çağrılır.
        
        Args:
            error_message: Hata mesajı
        """
        # Butonları güncelle
        self.analyze_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        # Hata mesajını göster
        self.results_text.setText(f"HATA: {error_message}")
        
        # Geçici dosyaları temizle
        self._clean_temp_files()
    
    def _show_results(self, results):
        """
        Analiz sonuçlarını göster.
        
        Args:
            results: Analiz sonuçları
        """
        # Geçici etiketi gizle
        self.empty_label.setVisible(False)
        
        # Sonuç bilgilerini metin alanına yaz
        if 'latest_week_df' in results and results['latest_week_df'] is not None:
            df = results['latest_week_df']
            total_time = df['Süre (Dakika)'].sum() if 'Süre (Dakika)' in df else 0
            machine_count = len(df['İş Merkezi Kodu '].unique()) if 'İş Merkezi Kodu ' in df else 0
            week_info = f"Hafta: {results['weeks'][0]}" if 'weeks' in results and results['weeks'] else "Hafta bilgisi yok"
            
            summary_text = (
                f"Analiz Sonuçları\n"
                f"---------------\n"
                f"{week_info}\n"
                f"Toplam Tezgah Sayısı: {machine_count}\n"
                f"Toplam Duruş Süresi: {total_time} dakika\n"
            )
            
            if 'excel_file' in results:
                summary_text += f"\nExcel Dosyası: {results['excel_file']}\n"
            
            self.results_text.setText(summary_text)
        
        # Grafikleri göster
        self._display_charts()
    
    def _display_charts(self):
        """
        Oluşturulan grafikleri göster.
        """
        # Grafikleri temizle
        while self.charts_layout.count() > 3:  # İlk 3 widget'ı koru (boş etiket, bar chart, pie chart)
            item = self.charts_layout.takeAt(3)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Raporlar klasöründen grafikleri yükle
        chart_folders = [
            "Raporlar/Genel",
            "Raporlar/Kısımlar/Son Hafta",
            "Raporlar/Tezgahlar/Son Hafta"
        ]
        
        chart_count = 0
        
        for folder in chart_folders:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    if file.endswith('.png'):
                        file_path = os.path.join(folder, file)
                        
                        # Grafik grubu oluştur
                        chart_group = QGroupBox(file.replace('.png', ''))
                        chart_layout = QVBoxLayout()
                        
                        # Grafik etiketi oluştur
                        chart_label = QLabel()
                        pixmap = QPixmap(file_path)
                        chart_label.setPixmap(pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                        chart_label.setAlignment(Qt.AlignCenter)
                        chart_layout.addWidget(chart_label)
                        
                        chart_group.setLayout(chart_layout)
                        self.charts_layout.insertWidget(self.charts_layout.count() - 1, chart_group)
                        
                        chart_count += 1
                        
                        # Maksimum 5 grafik göster
                        if chart_count >= 5:
                            break
                
                # Maksimum 5 grafik göster
                if chart_count >= 5:
                    break
        
        # Eğer hiç grafik yoksa
        if chart_count == 0:
            # Boş etiketi göster
            self.empty_label.setVisible(True)
        else:
            # Boş etiketi gizle
            self.empty_label.setVisible(False)
    
    def _clean_temp_files(self):
        """
        Geçici dosyaları temizle.
        """
        temp_files = ['temp_durus.xlsx', 'temp_calisma.xlsx', 'temp_arizali.txt']
        
        for file in temp_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except Exception as e:
                    logger.warning(f"Geçici dosya silinirken hata oluştu: {str(e)}")
    
    def clear_results(self):
        """
        Sonuçları temizle.
        """
        # Sonuç metnini temizle
        self.results_text.clear()
        
        # Grafikleri temizle
        while self.charts_layout.count() > 3:  # İlk 3 widget'ı koru
            item = self.charts_layout.takeAt(3)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Boş etiketi göster
        self.empty_label.setVisible(True)
        
        # İlerleme çubuğunu sıfırla
        self.progress_bar.setValue(0)
        self.progress_label.setText("İlerleme: ")
    
    def update_target_weeks(self, weeks):
        """
        Hedef hafta combobox'ını güncelle.
        
        Args:
            weeks: Hafta numaraları listesi
        """
        self.target_week_combo.clear()
        self.target_week_combo.addItem("Son Hafta", -1)
        
        if weeks:
            for week in weeks:
                self.target_week_combo.addItem(f"Hafta {week}", week)