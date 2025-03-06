"""
Özel widget'lar.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QFrame, QProgressBar, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QPixmap, QIcon

import logging
logger = logging.getLogger(__name__)

class ClickableLabel(QLabel):
    """
    Tıklanabilir etiket widget'ı.
    """
    # Sinyaller
    clicked = pyqtSignal()
    
    def __init__(self, text="", parent=None):
        """
        Widget'ı başlat.
        
        Args:
            text: Etiket metni
            parent: Üst widget
        """
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        """
        Fare tıklama olayı.
        
        Args:
            event: Olay nesnesi
        """
        self.clicked.emit()
        super().mousePressEvent(event)


class ImageButton(QPushButton):
    """
    Resimli buton widget'ı.
    """
    
    def __init__(self, image_path="", tooltip="", parent=None):
        """
        Widget'ı başlat.
        
        Args:
            image_path: Resim dosyası yolu
            tooltip: İpucu metni
            parent: Üst widget
        """
        super().__init__(parent)
        
        # Resim ayarla
        if image_path:
            icon = QIcon(image_path)
            self.setIcon(icon)
        
        # İpucu metni ayarla
        if tooltip:
            self.setToolTip(tooltip)
        
        # Stil ayarları
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)


class StatusWidget(QFrame):
    """
    Durum gösterge widget'ı.
    """
    
    def __init__(self, title="", parent=None):
        """
        Widget'ı başlat.
        
        Args:
            title: Başlık
            parent: Üst widget
        """
        super().__init__(parent)
        
        # Layout oluştur
        layout = QVBoxLayout()
        
        # Başlık
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Durum metni
        self.status_label = QLabel("Hazır")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Çerçeve ayarları
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        self.setLayout(layout)
    
    def set_status(self, status_text, progress=None):
        """
        Durum bilgisini ayarla.
        
        Args:
            status_text: Durum metni
            progress: İlerleme değeri (None ise ilerleme çubuğu gizlenir)
        """
        self.status_label.setText(status_text)
        
        if progress is not None:
            self.progress_bar.setValue(progress)
            self.progress_bar.setVisible(True)
        else:
            self.progress_bar.setVisible(False)


class InfoPanel(QWidget):
    """
    Bilgi paneli widget'ı.
    """
    
    def __init__(self, title="", parent=None):
        """
        Widget'ı başlat.
        
        Args:
            title: Başlık
            parent: Üst widget
        """
        super().__init__(parent)
        
        # Layout oluştur
        layout = QVBoxLayout()
        
        # Başlık
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Ayırıcı çizgi
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # İçerik widget'ı
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_widget.setLayout(self.content_layout)
        layout.addWidget(self.content_widget)
        
        # Stil ayarları
        self.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        
        self.setLayout(layout)
    
    def add_info_row(self, label_text, value_text):
        """
        Bilgi satırı ekle.
        
        Args:
            label_text: Etiket metni
            value_text: Değer metni
        """
        row_layout = QHBoxLayout()
        
        label = QLabel(f"{label_text}:")
        label.setStyleSheet("font-weight: bold;")
        
        value = QLabel(value_text)
        
        row_layout.addWidget(label)
        row_layout.addWidget(value, 1)
        
        self.content_layout.addLayout(row_layout)
    
    def clear_info(self):
        """
        Tüm bilgi satırlarını temizle.
        """
        # İçerik layout'ındaki tüm widget'ları temizle
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            
            if widget:
                widget.deleteLater()
            else:
                # Eğer layout ise temizle
                while item.count():
                    sub_item = item.takeAt(0)
                    sub_widget = sub_item.widget()
                    if sub_widget:
                        sub_widget.deleteLater()


class HeaderWidget(QWidget):
    """
    Başlık widget'ı.
    """
    
    def __init__(self, title="", description="", icon_path=None, parent=None):
        """
        Widget'ı başlat.
        
        Args:
            title: Başlık
            description: Açıklama
            icon_path: İkon dosya yolu
            parent: Üst widget
        """
        super().__init__(parent)
        
        # Layout oluştur
        layout = QHBoxLayout()
        
        # İkon (varsa)
        if icon_path:
            icon_label = QLabel()
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            layout.addWidget(icon_label)
        
        # Metin alanı
        text_layout = QVBoxLayout()
        
        # Başlık
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        text_layout.addWidget(title_label)
        
        # Açıklama
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet("font-size: 10pt;")
            text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout)
        
        # Sağa boşluk ekle
        layout.addStretch()
        
        # Stil ayarları
        self.setStyleSheet("background-color: #e0e0e0; border-radius: 5px;")
        
        self.setLayout(layout)
        
        # Minimum yükseklik
        self.setMinimumHeight(60)