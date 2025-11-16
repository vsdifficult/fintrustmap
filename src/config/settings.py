"""
Конфигурация и константы приложения
"""

# Версия приложения
VERSION = "2.0.0"
LICENSE = "MIT"

# UI настройки
WINDOW_TITLE = "FinTrustMap - Heatmap by Federal Districts"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
LEFT_PANEL_WIDTH = 400

# Цветовая схема
COLORS = {
    'background': '#1e1e1e',
    'panel': '#2d2d2d',
    'header': '#0d7377',
    'accent': '#14b1ab',
    'text': '#ffffff',
    'text_secondary': '#aaa',
    'success': '#00ff00',
    'error': '#ff0000',
    'button_hover': '#14b1ab'
}

# Доступные цветовые схемы для heatmap
COLORMAPS = [
    "RdYlGn",
    "RdYlGn_r",
    "viridis",
    "plasma",
    "coolwarm",
    "Spectral",
    "Blues",
    "Reds"
]

# Методы расчёта индекса
CALCULATION_METHODS = {
    'min_max_normalized': 'Min-Max нормализация',
    'simple_average': 'Простое среднее',
    'pca': 'PCA',
    'cbr_method': 'Методика ЦБ РФ'
}

# Настройки matplotlib
MPL_FIGURE_SIZE = (16, 10)
MPL_DPI = 100
MPL_FACECOLOR = '#1e1e1e'

# Настройки heatmap
HEATMAP_GRID_ROWS = 4
HEATMAP_GRID_COLS = 2
HEATMAP_ANNOT_SIZE = 8
HEATMAP_LINEWIDTH = 1.5

# Форматы файлов
EXCEL_FORMATS = "Excel Files (*.xlsx *.xls);;All Files (*)"
EXPORT_FORMAT = "Excel Files (*.xlsx)"

# Логирование
LOG_TIMESTAMP_FORMAT = "%H:%M:%S"
LOG_FONT_FAMILY = "Courier"
LOG_FONT_SIZE = 9

# Валидация данных
REQUIRED_COLUMN = "Регион"
MIN_NUMERIC_COLUMNS = 1

# Кэширование
CACHE_ENABLED = True
CACHE_SIZE_LIMIT = 100  # MB