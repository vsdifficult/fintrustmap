"""
FinTrustMap GUI application module (PyQt5).

Contains `FinTrustHeatmapApp` using PyQt5 for the UI.
"""
from src.config.federal_districts import FEDERAL_DISTRICTS

import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QComboBox, QCheckBox, QFileDialog,
    QMessageBox, QTextEdit, QGroupBox, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
import os

class FinTrustHeatmapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FinTrustMap - Heatmap by Federal Districts")
        self.setGeometry(100, 100, 1400, 900)
        
        # Data
        self.df = None
        self.excel_file = None
        self.canvas = None
        
        # Setup UI
        self.init_ui()
        
        # Apply dark theme styling
        self.apply_dark_theme()
        
        # Show initial placeholder
        self.show_placeholder()
    
    def apply_dark_theme(self):
        """Apply dark theme using stylesheets"""
        dark_stylesheet = """
        QMainWindow { background-color: #1e1e1e; }
        QWidget { background-color: #1e1e1e; color: #ffffff; }
        QLabel { color: #ffffff; }
        QPushButton { 
            background-color: #0d7377; 
            color: #ffffff; 
            border: none; 
            padding: 6px;
            border-radius: 3px;
            font-weight: bold;
        }
        QPushButton:hover { background-color: #14b1ab; }
        QPushButton:pressed { background-color: #0a5a63; }
        QRadioButton { color: #ffffff; }
        QCheckBox { color: #ffffff; }
        QComboBox { 
            background-color: #2d2d2d; 
            color: #ffffff;
            border: 1px solid #0d7377;
            padding: 4px;
        }
        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            color: #ffffff;
            selection-background-color: #0d7377;
        }
        QTextEdit { 
            background-color: #1e1e1e; 
            color: #00ff00;
            border: 1px solid #0d7377;
            font-family: Courier;
            font-size: 9px;
        }
        QGroupBox {
            color: #ffffff;
            border: 1px solid #0d7377;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        """
        self.setStyleSheet(dark_stylesheet)
    
    def init_ui(self):
        """Initialize the UI"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Left panel (controls)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 0)
        
        # Right panel (preview)
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        title_label = QLabel("📈 Предпросмотр Heatmap (по ФО)")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(title_label)
        
        self.preview_frame = QWidget()
        self.preview_layout = QVBoxLayout()
        self.preview_frame.setLayout(self.preview_layout)
        right_layout.addWidget(self.preview_frame)
        
        main_layout.addWidget(right_panel, 1)
        main_layout.setStretch(0, 0)
        main_layout.setStretch(1, 1)
    
    def create_left_panel(self):
        """Create left control panel"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Header
        header = QLabel("📊 FinTrustMap — Heatmap по ФО")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # File section
        file_group = self.create_file_group()
        layout.addWidget(file_group)
        
        # Method section
        method_group = self.create_method_group()
        layout.addWidget(method_group)
        
        # Style section
        style_group = self.create_style_group()
        layout.addWidget(style_group)
        
        # Action buttons
        actions_group = self.create_actions_group()
        layout.addWidget(actions_group)
        
        # Log section
        log_group = self.create_log_group()
        layout.addWidget(log_group)
        
        layout.addStretch()
        
        scroll.setWidget(panel)
        return scroll
    
    def create_file_group(self):
        """Create file selection group"""
        group = QGroupBox("📁 Данные")
        layout = QVBoxLayout()
        
        self.file_label = QLabel("Файл не выбран")
        layout.addWidget(self.file_label)
        
        btn_load = QPushButton("Выбрать Excel")
        btn_load.clicked.connect(self.load_excel)
        layout.addWidget(btn_load)
        
        group.setLayout(layout)
        return group
    
    def create_method_group(self):
        """Create calculation method group"""
        group = QGroupBox("⚙ Метод расчёта")
        layout = QVBoxLayout()
        
        self.method_group = QButtonGroup()
        methods = [
            ("Min-Max нормализация", "min_max_normalized"),
            ("Простое среднее", "simple_average"),
            ("PCA", "pca"),
            ("Методика ЦБ РФ", "cbr_method")
        ]
        
        for i, (label, value) in enumerate(methods):
            radio = QRadioButton(label)
            radio.setProperty("value", value)
            if i == 0:
                radio.setChecked(True)
            self.method_group.addButton(radio, i)
            layout.addWidget(radio)
        
        group.setLayout(layout)
        return group
    
    def create_style_group(self):
        """Create style/appearance group"""
        group = QGroupBox("🎨 Стиль")
        layout = QVBoxLayout()
        
        label = QLabel("Цветовая схема:")
        layout.addWidget(label)
        
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems([
            "RdYlGn", "RdYlGn_r", "viridis", "plasma", "coolwarm", "Spectral"
        ])
        layout.addWidget(self.colormap_combo)
        
        self.show_values_check = QCheckBox("Показывать названия и значения")
        self.show_values_check.setChecked(True)
        layout.addWidget(self.show_values_check)
        
        group.setLayout(layout)
        return group
    
    def create_actions_group(self):
        """Create action buttons group"""
        group = QGroupBox("Действия")
        layout = QVBoxLayout()
        
        self.btn_calc = QPushButton("📊 Рассчитать индекс")
        self.btn_calc.clicked.connect(self.calculate_index)
        self.btn_calc.setEnabled(False)
        layout.addWidget(self.btn_calc)
        
        self.btn_show = QPushButton("🔥 Показать Heatmap (по ФО)")
        self.btn_show.clicked.connect(self.create_heatmap)
        self.btn_show.setEnabled(False)
        layout.addWidget(self.btn_show)
        
        self.btn_export = QPushButton("💾 Экспорт")
        self.btn_export.clicked.connect(self.export_results)
        self.btn_export.setEnabled(False)
        layout.addWidget(self.btn_export)
        
        group.setLayout(layout)
        return group
    
    def create_log_group(self):
        """Create log display group"""
        group = QGroupBox("ℹ Информация")
        layout = QVBoxLayout()
        
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(150)
        layout.addWidget(self.log_box)
        
        group.setLayout(layout)
        return group
    
    def log(self, txt):
        """Log message to log box"""
        t = datetime.now().strftime("%H:%M:%S")
        self.log_box.append(f"[{t}] {txt}")
    
    def show_placeholder(self):
        """Show placeholder in preview area"""
        try:
            # Clear any existing widgets
            for i in reversed(range(self.preview_layout.count())):
                widget = self.preview_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Create placeholder figure
            fig = Figure(figsize=(14, 8), dpi=100, facecolor="#1e1e1e")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#1e1e1e")
            ax.text(0.5, 0.5, "Загрузите файл и рассчитайте индекс", 
                   ha="center", va="center", fontsize=16, color="gray",
                   transform=ax.transAxes)
            ax.axis("off")
            
            self.canvas = FigureCanvas(fig)
            self.preview_layout.addWidget(self.canvas)
            self.canvas.draw()
        except Exception as e:
            print(f"Error showing placeholder: {e}")
    
    def load_excel(self):
        """Load Excel file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите Excel", "", "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if not file_path:
            return
        
        try:
            self.df = pd.read_excel(file_path)
            self.excel_file = file_path
            
            if 'Регион' not in self.df.columns:
                raise ValueError("В файле обязательно должна быть колонка 'Регион'")
            
            numeric = self.df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric) == 0:
                raise ValueError("В файле нет числовых показателей.")
            
            self.file_label.setText(
                f"✓ {os.path.basename(file_path)} | Р:{len(self.df)} П:{len(numeric)}"
            )
            self.file_label.setStyleSheet("color: #00ff00;")
            self.btn_calc.setEnabled(True)
            self.log(f"Файл загружен: {os.path.basename(file_path)} (показателей: {len(numeric)})")
            QMessageBox.information(self, "Успех", "Файл загружен")
        except Exception as e:
            self.log(f"Ошибка загрузки: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))
    
    def calculate_index(self):
        """Calculate index"""
        if self.df is None:
            QMessageBox.warning(self, "Предупреждение", "Загрузите файл")
            return
        
        try:
            # Get selected method
            selected_button = self.method_group.checkedButton()
            method = selected_button.property("value")
            
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) == 0:
                raise ValueError("Нет числовых показателей для расчёта")
            
            if method == "simple_average":
                self.df['Индекс'] = self.df[numeric_cols].mean(axis=1)
            
            elif method == "min_max_normalized":
                normalized = self.df[numeric_cols].copy()
                for c in numeric_cols:
                    mi, ma = normalized[c].min(), normalized[c].max()
                    if ma > mi:
                        normalized[c] = (normalized[c] - mi) / (ma - mi)
                    else:
                        normalized[c] = 0.0
                self.df['Индекс'] = 100 * normalized.mean(axis=1)
            
            elif method == "pca":
                from sklearn.preprocessing import StandardScaler
                from sklearn.decomposition import PCA
                scaler = StandardScaler()
                scaled = scaler.fit_transform(self.df[numeric_cols])
                pca = PCA(n_components=1)
                idx_raw = pca.fit_transform(scaled).flatten()
                if idx_raw.max() != idx_raw.min():
                    self.df['Индекс'] = 100 * (idx_raw - idx_raw.min()) / (idx_raw.max() - idx_raw.min())
                else:
                    self.df['Индекс'] = 50.0
            
            elif method == "cbr_method":
                normalized = self.df[numeric_cols].copy()
                for c in numeric_cols:
                    mi, ma = normalized[c].min(), normalized[c].max()
                    if ma > mi:
                        normalized[c] = (normalized[c] - mi) / (ma - mi)
                    else:
                        normalized[c] = 0.5
                
                weights = np.ones(len(numeric_cols)) / len(numeric_cols)
                self.df['Индекс'] = normalized.dot(weights) * 100
            
            else:
                self.df['Индекс'] = self.df[numeric_cols].mean(axis=1)
            
            self.log("Индекс рассчитан")
            self.log(f"Среднее: {self.df['Индекс'].mean():.2f}, Мин: {self.df['Индекс'].min():.2f}, Макс: {self.df['Индекс'].max():.2f}")
            self.btn_show.setEnabled(True)
            self.btn_export.setEnabled(True)
            QMessageBox.information(self, "Готово", "Индекс рассчитан")
        except Exception as e:
            self.log(f"Ошибка расчёта: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))
    
    def create_heatmap(self):
        """Create and display heatmap"""
        if self.df is None or 'Индекс' not in self.df.columns:
            QMessageBox.warning(self, "Предупреждение", "Сначала рассчитайте индекс!")
            return
        
        self.log("Создание Heatmap по федеральным округам...")
        
        try:
            # Prepare data
            df = self.df.copy().set_index("Регион")
            values = df["Индекс"]
            
            # Create figure
            fig = Figure(figsize=(14, 8), dpi=100, facecolor="#1e1e1e")
            gs = fig.add_gridspec(4, 2, wspace=0.25, hspace=0.35)
            
            district_positions = list(FEDERAL_DISTRICTS.keys())
            pos_idx = 0
            
            # Draw each district
            for r in range(4):
                for c in range(2):
                    if pos_idx >= len(district_positions):
                        break
                    
                    district = district_positions[pos_idx]
                    regions = FEDERAL_DISTRICTS[district]
                    real_regions = [reg for reg in regions if reg in df.index]
                    
                    ax = fig.add_subplot(gs[r, c])
                    ax.set_facecolor("#1e1e1e")
                    ax.set_title(district, fontsize=12, color="white", pad=8)
                    
                    if len(real_regions) == 0:
                        ax.text(0.5, 0.5, "Нет данных", color="gray", ha="center", va="center", fontsize=10)
                        ax.axis("off")
                        pos_idx += 1
                        continue
                    
                    # Create grid
                    n = len(real_regions)
                    cols = int(np.ceil(np.sqrt(n)))
                    rows = int(np.ceil(n / cols))
                    
                    grid = np.zeros((rows, cols))
                    labels = [["" for _ in range(cols)] for __ in range(rows)]
                    
                    for i, region in enumerate(real_regions):
                        r0 = i // cols
                        c0 = i % cols
                        val = df.loc[region, "Индекс"]
                        if values.max() != values.min():
                            norm_val = (val - values.min()) / (values.max() - values.min())
                        else:
                            norm_val = 0.0
                        
                        grid[r0, c0] = norm_val
                        labels[r0][c0] = f"{region}\n{val:.1f}"
                    
                    sns.heatmap(
                        grid, cmap=self.colormap_combo.currentText(), ax=ax, cbar=False,
                        annot=labels if self.show_values_check.isChecked() else False,
                        fmt="", linewidths=1.5, linecolor="#1e1e1e",
                        annot_kws={"color": "black", "size": 6}
                    )
                    
                    ax.set_xticks([])
                    ax.set_yticks([])
                    pos_idx += 1
            
            # Clear previous canvas
            for i in reversed(range(self.preview_layout.count())):
                widget = self.preview_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Add new canvas and draw
            self.canvas = FigureCanvas(fig)
            self.preview_layout.addWidget(self.canvas)
            self.canvas.draw()
            
            self.log("✓ Красивый Heatmap создан!")
        except Exception as e:
            import traceback
            self.log(f"Ошибка создания heatmap: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", str(e))
    
    def export_results(self):
        """Export results to Excel"""
        if self.df is None or 'Индекс' not in self.df.columns:
            QMessageBox.warning(self, "Предупреждение", "Нечего экспортировать")
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить результаты", "", "Excel Files (*.xlsx)"
            )
            if not file_path:
                return
            
            out = self.df.sort_values('Индекс', ascending=False).reset_index(drop=True)
            out.index = out.index + 1
            out.index.name = 'Ранг'
            out.to_excel(file_path)
            
            self.log(f"Экспортировано: {os.path.basename(file_path)}")
            QMessageBox.information(self, "Успех", "Экспорт завершён")
        except Exception as e:
            self.log(f"Ошибка экспорта: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))
