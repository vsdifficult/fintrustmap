"""
Модуль для расчёта индексов по различным методикам
"""

import pandas as pd
import numpy as np
from typing import Dict


class CalculationError(Exception):
    """Исключение при ошибке расчёта"""
    pass


class IndexCalculator:
    """Класс для расчёта индексов финансового доверия"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: DataFrame с данными регионов
        """
        self._df = df.copy()
        self._numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self._cache = {}
    
    def calculate_index(self, method: str = 'min_max_normalized') -> pd.DataFrame:
        """
        Рассчитывает индекс по выбранному методу
        
        Args:
            method: Метод расчёта ('min_max_normalized', 'simple_average', 'pca', 'cbr_method')
            
        Returns:
            DataFrame с добавленной колонкой 'Индекс'
            
        Raises:
            CalculationError: При ошибке расчёта
        """
        if not self._numeric_cols:
            raise CalculationError("Нет числовых показателей для расчёта")
        
        # Проверка кэша
        cache_key = f"{method}_{hash(tuple(self._df.values.flatten()))}"
        if cache_key in self._cache:
            return self._cache[cache_key].copy()
        
        try:
            if method == 'min_max_normalized':
                result = self._min_max_normalized()
            elif method == 'simple_average':
                result = self._simple_average()
            elif method == 'pca':
                result = self._pca_method()
            elif method == 'cbr_method':
                result = self._cbr_method()
            else:
                raise CalculationError(f"Неизвестный метод: {method}")
            
            # Сохранение в кэш
            self._cache[cache_key] = result.copy()
            return result
            
        except Exception as e:
            raise CalculationError(f"Ошибка при расчёте индекса: {str(e)}")
    
    def _min_max_normalized(self) -> pd.DataFrame:
        """Min-Max нормализация"""
        df = self._df.copy()
        normalized = df[self._numeric_cols].copy()
        
        for col in self._numeric_cols:
            min_val, max_val = normalized[col].min(), normalized[col].max()
            if max_val > min_val:
                normalized[col] = (normalized[col] - min_val) / (max_val - min_val)
            else:
                normalized[col] = 0.0
        
        df['Индекс'] = 100 * normalized.mean(axis=1)
        return df
    
    def _simple_average(self) -> pd.DataFrame:
        """Простое среднее"""
        df = self._df.copy()
        df['Индекс'] = df[self._numeric_cols].mean(axis=1)
        return df
    
    def _pca_method(self) -> pd.DataFrame:
        """PCA метод"""
        try:
            from sklearn.preprocessing import StandardScaler
            from sklearn.decomposition import PCA
        except ImportError:
            raise CalculationError(
                "Для метода PCA требуется установить scikit-learn: pip install scikit-learn"
            )
        
        df = self._df.copy()
        
        # Стандартизация
        scaler = StandardScaler()
        scaled = scaler.fit_transform(df[self._numeric_cols])
        
        # PCA
        pca = PCA(n_components=1)
        idx_raw = pca.fit_transform(scaled).flatten()
        
        # Нормализация к [0, 100]
        if idx_raw.max() != idx_raw.min():
            df['Индекс'] = 100 * (idx_raw - idx_raw.min()) / (idx_raw.max() - idx_raw.min())
        else:
            df['Индекс'] = 50.0
        
        return df
    
    def _cbr_method(self) -> pd.DataFrame:
        """Методика ЦБ РФ"""
        df = self._df.copy()
        normalized = df[self._numeric_cols].copy()
        
        # Нормализация каждого показателя
        for col in self._numeric_cols:
            min_val, max_val = normalized[col].min(), normalized[col].max()
            if max_val > min_val:
                normalized[col] = (normalized[col] - min_val) / (max_val - min_val)
            else:
                normalized[col] = 0.5
        
        # Равные веса
        weights = np.ones(len(self._numeric_cols)) / len(self._numeric_cols)
        df['Индекс'] = normalized.dot(weights) * 100
        
        return df
    
    def get_statistics(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Возвращает статистику по рассчитанному индексу
        
        Args:
            df: DataFrame с рассчитанным индексом
            
        Returns:
            Словарь со статистикой
        """
        if 'Индекс' not in df.columns:
            return {}
        
        index_values = df['Индекс']
        return {
            'mean': float(index_values.mean()),
            'median': float(index_values.median()),
            'min': float(index_values.min()),
            'max': float(index_values.max()),
            'std': float(index_values.std())
        }
    
    def clear_cache(self):
        """Очистка кэша"""
        self._cache.clear()