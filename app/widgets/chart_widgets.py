"""
Grafik widget'ları.
"""

import os
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QComboBox, QGroupBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

import logging
logger = logging.getLogger(__name__)

class MatplotlibCanvas(FigureCanvas):
    """
    Matplotlib figürü için canvas sınıfı.
    """
    
    def __init__(self, width=8, height=6, dpi=100):
        """
        Canvas'ı başlat.
        
        Args:
            width: Genişlik (inç)
            height: Yükseklik (inç)
            dpi: DPI değeri
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        
        # Figür için ayarlar
        self.fig.tight_layout()
        
    def clear(self):
        """
        Figürü temizle.
        """
        self.axes.clear()
        self.fig.canvas.draw()


class PieChartWidget(QWidget):
    """
    Pasta grafik widget'ı.
    """
    
    def __init__(self, parent=None):
        """
        Widget'ı başlat.
        
        Args:
            parent: Üst widget
        """
        super().__init__(parent)
        
        # Layout
        layout = QVBoxLayout()
        
        # Canvas
        self.canvas = MatplotlibCanvas(width=8, height=6, dpi=100)
        layout.addWidget(self.canvas)
        
        # Toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        
        self.setLayout(layout)
    
    def plot_pie_chart(self, data, column, title="", threshold=3.0):
        """
        Pasta grafik çiz.
        
        Args:
            data: Veri DataFrame'i
            column: Kategori sütunu
            title: Başlık
            threshold: Eşik değeri
        """
        try:
            # Canvas'ı temizle
            self.canvas.clear()
            
            # Toplam değer
            if 'Süre (Dakika)' in data.columns:
                total = data['Süre (Dakika)'].sum()
                
                # Yüzdeleri hesapla
                data = data.copy()
                data['Yüzde'] = data['Süre (Dakika)'] / total * 100
                
                # Eşik değerinin altındakileri "Diğer" olarak grupla
                other_value = data[data['Yüzde'] < threshold]['Süre (Dakika)'].sum()
                filtered_data = data[data['Yüzde'] >= threshold].copy()
                
                if other_value > 0:
                    other_df = pd.DataFrame({
                        column: ['Diğer'],
                        'Süre (Dakika)': [other_value],
                        'Yüzde': [other_value / total * 100]
                    })
                    filtered_data = pd.concat([filtered_data, other_df])
                
                # Pasta grafik çiz
                patches, texts, autotexts = self.canvas.axes.pie(
                    filtered_data['Süre (Dakika)'],
                    labels=filtered_data[column],
                    autopct='%1.1f%%',
                    startangle=90,
                    shadow=True
                )
                
                # Başlık
                self.canvas.axes.set_title(title)
                
                # Eşit açı
                self.canvas.axes.axis('equal')
                
                # Canvas'ı güncelle
                self.canvas.fig.canvas.draw()
            else:
                logger.error("Veri 'Süre (Dakika)' sütununu içermiyor!")
        except Exception as e:
            logger.error(f"Pasta grafik çizilirken hata oluştu: {str(e)}")


class BarChartWidget(QWidget):
    """
    Çubuk grafik widget'ı.
    """
    
    def __init__(self, parent=None):
        """
        Widget'ı başlat.
        
        Args:
            parent: Üst widget
        """
        super().__init__(parent)
        
        # Layout
        layout = QVBoxLayout()
        
        # Canvas
        self.canvas = MatplotlibCanvas(width=10, height=6, dpi=100)
        layout.addWidget(self.canvas)
        
        # Toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        
        self.setLayout(layout)
    
    def plot_bar_chart(self, data, x_column, y_column, title="", color=None):
        """
        Çubuk grafik çiz.
        
        Args:
            data: Veri DataFrame'i
            x_column: X ekseni sütunu
            y_column: Y ekseni sütunu
            title: Başlık
            color: Renk
        """
        try:
            # Canvas'ı temizle
            self.canvas.clear()
            
            # Çubuk grafik çiz
            bars = self.canvas.axes.bar(
                data[x_column],
                data[y_column],
                color=color
            )
            
            # X ekseni etiketleri döndür
            self.canvas.axes.set_xticklabels(data[x_column], rotation=45, ha='right')
            
            # Başlık ve eksen etiketleri
            self.canvas.axes.set_title(title)
            self.canvas.axes.set_xlabel(x_column)
            self.canvas.axes.set_ylabel(y_column)
            
            # Değerleri çubukların üzerine ekle
            for bar in bars:
                height = bar.get_height()
                self.canvas.axes.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    f'{height:.1f}',
                    ha='center',
                    va='bottom'
                )
            
            # Canvas'ı güncelle
            self.canvas.fig.tight_layout()
            self.canvas.fig.canvas.draw()
        except Exception as e:
            logger.error(f"Çubuk grafik çizilirken hata oluştu: {str(e)}")


class LineChartWidget(QWidget):
    """
    Çizgi grafik widget'ı.
    """
    
    def __init__(self, parent=None):
        """
        Widget'ı başlat.
        
        Args:
            parent: Üst widget
        """
        super().__init__(parent)
        
        # Layout
        layout = QVBoxLayout()
        
        # Canvas
        self.canvas = MatplotlibCanvas(width=10, height=6, dpi=100)
        layout.addWidget(self.canvas)
        
        # Toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        
        self.setLayout(layout)
    
    def plot_line_chart(self, data, x_column, y_columns, title="", colors=None):
        """
        Çizgi grafik çiz.
        
        Args:
            data: Veri DataFrame'i
            x_column: X ekseni sütunu
            y_columns: Y ekseni sütunları listesi
            title: Başlık
            colors: Renkler listesi
        """
        try:
            # Canvas'ı temizle
            self.canvas.clear()
            
            # Renk ayarla
            if colors is None:
                colors = [f'C{i}' for i in range(len(y_columns))]
            
            # Her seri için çizgi çiz
            for i, y_column in enumerate(y_columns):
                self.canvas.axes.plot(
                    data[x_column],
                    data[y_column],
                    marker='o',
                    color=colors[i],
                    label=y_column
                )
            
            # Başlık ve eksen etiketleri
            self.canvas.axes.set_title(title)
            self.canvas.axes.set_xlabel(x_column)
            self.canvas.axes.set_ylabel('Değer')
            
            # Izgara
            self.canvas.axes.grid(True, linestyle='--', alpha=0.7)
            
            # Gösterge
            self.canvas.axes.legend()
            
            # Canvas'ı güncelle
            self.canvas.fig.tight_layout()
            self.canvas.fig.canvas.draw()
        except Exception as e:
            logger.error(f"Çizgi grafik çizilirken hata oluştu: {str(e)}")


class CustomWidgetsDemo(QWidget):
    """
    Özel widget'lar için demo sınıfı.
    """
    
    def __init__(self, parent=None):
        """
        Widget'ı başlat.
        
        Args:
            parent: Üst widget
        """
        super().__init__(parent)
        
        # Layout
        layout = QVBoxLayout()
        
        # Pasta grafik
        pie_group = QGroupBox("Pasta Grafik")
        pie_layout = QVBoxLayout()
        self.pie_chart = PieChartWidget()
        pie_layout.addWidget(self.pie_chart)
        pie_group.setLayout(pie_layout)
        layout.addWidget(pie_group)
        
        # Çubuk grafik
        bar_group = QGroupBox("Çubuk Grafik")
        bar_layout = QVBoxLayout()
        self.bar_chart = BarChartWidget()
        bar_layout.addWidget(self.bar_chart)
        bar_group.setLayout(bar_layout)
        layout.addWidget(bar_group)
        
        # Çizgi grafik
        line_group = QGroupBox("Çizgi Grafik")
        line_layout = QVBoxLayout()
        self.line_chart = LineChartWidget()
        line_layout.addWidget(self.line_chart)
        line_group.setLayout(line_layout)
        layout.addWidget(line_group)
        
        self.setLayout(layout)
        
        # Demo verileri göster
        self._show_demo_data()
    
    def _show_demo_data(self):
        """
        Demo verileri göster.
        """
        # Pasta grafik için demo veri
        pie_data = pd.DataFrame({
            'Kategori': ['A', 'B', 'C', 'D', 'E'],
            'Süre (Dakika)': [30, 25, 15, 10, 5]
        })
        self.pie_chart.plot_pie_chart(pie_data, 'Kategori', 'Demo Pasta Grafik', threshold=5)
        
        # Çubuk grafik için demo veri
        bar_data = pd.DataFrame({
            'Tezgah': ['T1', 'T2', 'T3', 'T4', 'T5'],
            'Süre': [120, 90, 150, 80, 110]
        })
        self.bar_chart.plot_bar_chart(bar_data, 'Tezgah', 'Süre', 'Demo Çubuk Grafik')
        
        # Çizgi grafik için demo veri
        x = np.linspace(0, 10, 20)
        line_data = pd.DataFrame({
            'X': x,
            'Seri 1': np.sin(x),
            'Seri 2': np.cos(x),
            'Seri 3': np.sin(x) + np.cos(x)
        })
        self.line_chart.plot_line_chart(
            line_data, 'X', ['Seri 1', 'Seri 2', 'Seri 3'], 'Demo Çizgi Grafik'
        )