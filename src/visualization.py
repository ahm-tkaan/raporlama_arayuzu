"""
Tezgah duruş analizleri için görselleştirme fonksiyonları.
Bu, daha önceki visualization.py dosyasının basitleştirilmiş versiyonudur.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Union
import logging

# Loglama yapılandırması
logger = logging.getLogger(__name__)

def ensure_dir(directory: str) -> None:
    """
    Belirtilen dizinin var olduğundan emin olur, yoksa oluşturur.
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Dizin oluşturuldu: {directory}")

def visualize_pie(
    data: pd.DataFrame, 
    threshold: float = 3.0,
    baslik: str = "Pasta Grafik",
    save: bool = True, 
    show: bool = True,
    category_column: str = None,
    custom_folder: str = None
) -> None:
    """
    Duruş sürelerini pasta grafik olarak görselleştirir.
    """
    logger.info(f"Pasta grafik oluşturuluyor: {baslik}")
    
    # Veri çerçevesini kopyalama
    data = data.copy()
    
    # Klasör yolunu belirleme
    if custom_folder is not None:
        folder_path = custom_folder
    elif "KISIM" in baslik:
        folder_path = 'Raporlar/Kısımlar/Son Hafta'
    else:
        folder_path = 'Raporlar/Genel'
    
    # Klasör oluşturma
    ensure_dir(folder_path)
    
    # Kategori sütunu belirleme
    if category_column is None:
        if 'Duruş Adı' in data.columns:
            category_column = 'Duruş Adı'
        elif 'KISIM' in data.columns:
            category_column = 'KISIM'
        elif 'İş Merkezi Kodu ' in data.columns:
            category_column = 'İş Merkezi Kodu '
        else:
            # Eğer uygun sütun bulunamazsa, indeksi kullan
            data = data.reset_index()
            if 'index' in data.columns:
                category_column = 'index'
            else:
                logger.error("Veri çerçevesinde kategori sütunu bulunamadı!")
                return
    
    # Kategori sütunu kontrolü
    if category_column not in data.columns:
        logger.error(f"Kategori sütunu '{category_column}' veri çerçevesinde bulunamadı!")
        return
    
    # Eğer veri yoksa işlem yapma
    if len(data) == 0 or 'Süre (Dakika)' not in data.columns:
        logger.warning(f"Pasta grafik için geçerli veri bulunamadı: {baslik}")
        return
    
    try:
        # Toplam süre hesaplama
        total_time = data["Süre (Dakika)"].sum()
        
        # Yüzde hesaplama
        data["Yüzde"] = (data["Süre (Dakika)"] / total_time * 100)
        
        # Eşik değerinden küçük olanları "Diğer" olarak gruplama
        diger_sure = data[data["Yüzde"] < threshold]["Süre (Dakika)"].sum()
        diger_df = data[data["Yüzde"] >= threshold].copy()
        
        # "Diğer" satırını ekleme
        if diger_sure > 0:
            diger_row = pd.DataFrame({
                category_column: ["Diğer"],
                "Süre (Dakika)": [diger_sure],
                "Yüzde": [(diger_sure / total_time * 100)]
            })
            diger_df = pd.concat([diger_df, diger_row])
        
        # Yüzdeye göre sıralama
        diger_df = diger_df.sort_values("Yüzde", ascending=False)
        
        # Pasta grafik oluşturma
        plt.figure(figsize=(10, 8))
        
        # Pasta grafiği
        plt.pie(
            diger_df["Süre (Dakika)"],
            labels=diger_df[category_column],
            autopct='%1.1f%%',
            startangle=90,
            shadow=True
        )
        
        # Başlık ve eksen ayarları
        plt.title(f"{baslik}", fontsize=14)
        plt.axis('equal')
        
        # Grafiği kaydet
        if save:
            file_path = os.path.join(folder_path, f"{baslik}.png")
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {file_path}")
        
        # Grafiği göster
        if show:
            plt.show()
        
        # Grafiği kapat
        plt.close()
    
    except Exception as e:
        logger.error(f"Pasta grafik oluşturulurken hata: {str(e)}")

def visualize_bar(
    data: pd.DataFrame, 
    colors: str = "Accent", 
    bundan: Optional[int] = None, 
    buna: Optional[int] = None, 
    text: int = 1, 
    baslik: str = "Tüm İş Merkezleri",
    save: bool = True,
    show: bool = True
) -> None:
    """
    Duruş sürelerini çubuk grafik olarak görselleştirir.
    """
    logger.info(f"Çubuk grafik oluşturuluyor: {baslik}")
    
    # Eğer veri yoksa işlem yapma
    if len(data) == 0 or 'Süre (Dakika)' not in data.columns:
        logger.warning(f"Çubuk grafik için geçerli veri bulunamadı: {baslik}")
        return
    
    try:
        # Klasör yolunu belirle
        if " (Tezgah Başına)" in baslik:
            folder_path = 'Raporlar/Kısımlar/Son Hafta Tezgah Başına Ortalama'
        else:
            folder_path = 'Raporlar/Genel'
        ensure_dir(folder_path)
        
        # İndeksleri kontrol et
        if bundan is None:
            bundan = 0
        if buna is None:
            buna = len(data)
        
        # Veriyi filtrele
        filtered_data = data.iloc[bundan:buna].copy()
        
        # Veri yoksa uyarı ver ve çık
        if filtered_data.empty:
            logger.warning(f"Grafik için veri bulunamadı: {baslik}")
            return
        
        # Toplam süreyi hesapla
        total_time = data["Süre (Dakika)"].sum()
        
        # Yüzde hesapla
        filtered_data["Yüzde"] = (filtered_data["Süre (Dakika)"] / total_time) * 100
        
        # Grafik oluşturma
        plt.figure(figsize=(12, 8))
        
        # Çubuk grafiği
        bars = plt.bar(
            filtered_data["İş Merkezi Kodu "],
            filtered_data["Süre (Dakika)"],
            color=sns.color_palette(colors, len(filtered_data))
        )
        
        # Değerleri çubukların üzerine ekle
        if text:
            for i, bar in enumerate(bars):
                height = bar.get_height()
                percentage = filtered_data["Yüzde"].iloc[i]
                plt.text(
                    bar.get_x() + bar.get_width() / 2, height, 
                    f"{height} ({percentage:.1f}%)",
                    ha='center', va='bottom', fontsize=10
                )
        
        # Grafik başlık ve eksen etiketleri
        plt.title(baslik, fontsize=14)
        plt.xlabel("İş Merkezi Kodu", fontsize=12)
        plt.ylabel("Süre (Dakika)", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Grafiği kaydet
        if save:
            file_path = os.path.join(folder_path, f"{baslik}.png")
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {file_path}")
        
        # Grafiği göster
        if show:
            plt.show()
        
        # Grafiği kapat
        plt.close()
    
    except Exception as e:
        logger.error(f"Çubuk grafik oluşturulurken hata: {str(e)}")

def visualize_weekly_comparison(
    df: pd.DataFrame, 
    gozlem: str = "KISIM", 
    egiklik: int = 75, 
    palet: str = "tab20",
    save: bool = True,
    show: bool = True,
    sort_by_last_week: bool = True,
    target_week: int = 1
) -> None:
    """
    4 haftalık duruş karşılaştırmasını görselleştirir.
    """
    logger.info(f"{gozlem} için haftalık karşılaştırma grafikleri oluşturuluyor...")
    
    # Veri yoksa işlem yapma
    if df.empty:
        logger.warning("Haftalık karşılaştırma için veri bulunamadı.")
        return
    
    try:
        # Klasör yolunu belirle
        if gozlem == "KISIM":
            folder_path = 'Raporlar/Kısımlar/4 haftalık'
        else:
            folder_path = 'Raporlar/Tezgahlar/4 haftalık'
        
        ensure_dir(folder_path)
        
        # Her gözlem değeri için grafik oluştur
        for gozlemlenen, data in df.groupby(gozlem):
            plt.figure(figsize=(12, 8))
            
            # Hafta listesini al
            weeks = sorted(data["Hafta"].unique())
            
            # Kategorileri al
            categories = data['Duruş Adı'].unique()
            
            # X ekseni etiketleri ve pozisyonları
            x_positions = np.arange(len(categories))
            
            # Hafta başına çubuklar
            bar_width = 0.8 / len(weeks)
            
            for i, week in enumerate(weeks):
                week_data = data[data['Hafta'] == week]
                
                # Her kategori için değer bul
                heights = []
                for cat in categories:
                    cat_data = week_data[week_data['Duruş Adı'] == cat]
                    if not cat_data.empty:
                        heights.append(cat_data['Süre (Dakika)'].iloc[0])
                    else:
                        heights.append(0)
                
                # Çubukları çiz
                x_pos = x_positions - 0.4 + (i + 0.5) * bar_width
                bars = plt.bar(
                    x_pos, heights, width=bar_width, 
                    label=f'Hafta {week}',
                    color=sns.color_palette(palet)[i % 10]
                )
            
            # X ekseni etiketlerini ayarla
            plt.xticks(x_positions, categories, rotation=egiklik, ha='right')
            
            # Başlık ve açıklamalar
            plt.title(f'{gozlemlenen} - Haftalık Duruş Karşılaştırması')
            plt.xlabel('Duruş Adı')
            plt.ylabel('Süre (Dakika)')
            plt.legend(title='Hafta')
            plt.tight_layout()
            
            # Grafiği kaydet
            if save:
                file_path = os.path.join(folder_path, f"{gozlemlenen} - 4 HAFTALIK.png")
                plt.savefig(file_path, dpi=300, bbox_inches='tight')
                logger.info(f"Grafik kaydedildi: {file_path}")
            
            # Grafiği göster
            if show:
                plt.show()
            
            # Grafiği kapat
            plt.close()
    
    except Exception as e:
        logger.error(f"Haftalık karşılaştırma grafiği oluşturulurken hata: {str(e)}")

def plot_bar(
    df: pd.DataFrame, 
    machine_code_column: str = "İş Merkezi Kodu ", 
    stoppage_column: str = "Duruş Adı", 
    duration_column: str = "Süre (Dakika)", 
    threshold: float = 3,
    save: bool = True,
    show: bool = True
) -> None:
    """
    Her bir tezgah için duruş sürelerini çubuk grafik olarak görselleştirir.
    """
    logger.info("Tezgah duruş grafikleri oluşturuluyor...")
    
    # Veri yoksa işlem yapma
    if df.empty:
        logger.warning("Tezgah duruş grafikleri için veri bulunamadı.")
        return
    
    try:
        # Unique makine kodlarını al
        machine_codes = df[machine_code_column].unique()

        # Klasör yolunu tanımla
        folder_path = 'Raporlar/Tezgahlar/Son Hafta'
        ensure_dir(folder_path)
        
        for code in machine_codes:
            # Makineye ait verileri filtrele
            machine_data = df[df[machine_code_column] == code].copy()
            
            # Toplam süreyi hesapla
            total_duration = machine_data[duration_column].sum()
            
            # Eğer toplam süre 0 ise, bu makine için grafik oluşturma
            if total_duration == 0:
                logger.warning(f"Tezgah {code} için veri yok veya toplam süre 0.")
                continue
                
            # Duruş adlarına göre grupla
            machine_summary = machine_data.groupby(stoppage_column)[duration_column].sum().reset_index()
            
            # Grafiği oluştur
            plt.figure(figsize=(10, 6))
            plt.bar(
                machine_summary[stoppage_column],
                machine_summary[duration_column],
                color=sns.color_palette("pastel")
            )
            plt.title(f"{code} - Duruş Süreleri")
            plt.xlabel("Duruş Adı")
            plt.ylabel("Süre (Dakika)")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Grafiği kaydet
            if save:
                file_path = os.path.join(folder_path, f"{code}.png")
                plt.savefig(file_path, dpi=300, bbox_inches='tight')
                logger.info(f"Grafik kaydedildi: {file_path}")
            
            # Grafiği göster
            if show:
                plt.show()
            
            # Grafiği kapat
            plt.close()
    
    except Exception as e:
        logger.error(f"Tezgah duruş grafikleri oluşturulurken hata: {str(e)}")

def visualize_top_bottom_machines(
    df: pd.DataFrame,
    top_count: int = 7,
    bottom_count: int = 7,
    save: bool = True,
    show: bool = True
) -> None:
    """
    En çok ve en az duruşa sahip tezgahları görselleştirir.
    """
    logger.info(f"En çok ve en az duruşa sahip tezgahlar grafiği oluşturuluyor...")
    
    # Veri yoksa işlem yapma
    if df.empty:
        logger.warning("En çok ve en az duruşa sahip tezgahlar grafiği için veri bulunamadı.")
        return
    
    try:
        # Toplam süreyi hesapla
        total_time = df["Süre (Dakika)"].sum()

        # İlk ve son tezgahları seç
        df_sorted = df.sort_values(by="Süre (Dakika)", ascending=True)
        top = df_sorted.tail(top_count)  # En yüksek değerler
        bottom = df_sorted.head(bottom_count)  # En düşük değerler

        # Seçilen satırları birleştir
        selected_data = pd.concat([bottom, top])

        # Renkleri ayarla: ilk bottom_count yeşil, son top_count kırmızı
        colors = ['#2ca02c'] * len(bottom) + ['#d62728'] * len(top)

        # Grafik oluştur
        plt.figure(figsize=(12, 8))
        plt.bar(
            selected_data["İş Merkezi Kodu "],
            selected_data["Süre (Dakika)"],
            color=colors
        )
        plt.title(f"İş Merkezi Koduna Göre Süre (Dakika) - İlk {bottom_count} Yeşil, Son {top_count} Kırmızı")
        plt.xlabel("İş Merkezi Kodu")
        plt.ylabel("Süre (Dakika)")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Grafiği kaydet
        if save:
            file_path = "Raporlar/Genel/İlk ve Son Tezgah.png"
            ensure_dir(os.path.dirname(file_path))
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {file_path}")
        
        # Grafiği göster
        if show:
            plt.show()
        
        # Grafiği kapat
        plt.close()
    
    except Exception as e:
        logger.error(f"En çok ve en az duruşa sahip tezgahlar grafiği oluşturulurken hata: {str(e)}")

def generate_oee_visuals(
    df: pd.DataFrame, 
    weeks: List[int]
) -> None:
    """
    OEE, performans, kullanılabilirlik ve kalite değerlerini görselleştirir.
    """
    logger.info("OEE görselleri oluşturuluyor...")
    
    # Veri yoksa işlem yapma
    if df.empty:
        logger.warning("OEE görselleri için veri bulunamadı.")
        return
    
    try:
        # Her hafta için
        for week in weeks:
            week_df = df[df["Hafta"] == week]
            
            # Genel ortalama
            oee_general = week_df["Oee"].mean() if "Oee" in week_df.columns else 0
            performans_general = week_df["Performans"].mean() if "Performans" in week_df.columns else 0
            kullanilabilirlik_general = week_df["Kullanılabilirlik"].mean() if "Kullanılabilirlik" in week_df.columns else 0
            kalite_general = week_df["Kalite"].mean() if "Kalite" in week_df.columns else 0
            
            # Grafik oluştur
            plt.figure(figsize=(10, 6))
            metrics = ['OEE', 'Performans', 'Kullanılabilirlik', 'Kalite']
            values = [oee_general, performans_general, kullanilabilirlik_general, kalite_general]
            
            plt.bar(metrics, values, color=sns.color_palette("Blues_d"))
            plt.title(f"{week}. Hafta OEE Metrikleri")
            plt.ylim([0, 1])
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Değerleri çubukların üzerine ekle
            for i, v in enumerate(values):
                plt.text(i, v + 0.01, f'{v:.2%}', ha='center')
            
            # Grafiği kaydet
            folder_path = f"Raporlar/Tee/Genel"
            ensure_dir(folder_path)
            file_path = os.path.join(folder_path, f"{week} Hafta.png")
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            
            # Grafiği kapat
            plt.close()
    
    except Exception as e:
        logger.error(f"OEE görselleri oluşturulurken hata: {str(e)}")