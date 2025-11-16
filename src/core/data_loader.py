"""
Модуль для загрузки и валидации данных
"""

import pandas as pd
import numpy as np
from typing import List
from ..config.settings import REQUIRED_COLUMN, MIN_NUMERIC_COLUMNS


class DataLoadError(Exception):
    """Исключение при ошибке загрузки данных"""
    pass


class DataLoader:
    """Класс для загрузки и валидации Excel данных"""
    
    def __init__(self):
        self._df = None
        self._file_path = None
    
    def load_excel(self, file_path: str) -> pd.DataFrame:
        """
        Загружает данные из Excel файла с валидацией
        
        Args:
            file_path: Путь к Excel файлу
            
        Returns:
            DataFrame с загруженными данными
            
        Raises:
            DataLoadError: При ошибке загрузки или валидации
        """
        try:
            df = pd.read_excel(file_path)
            self._validate_dataframe(df)
            self._df = df
            self._file_path = file_path
            return df.copy()
            
        except FileNotFoundError:
            raise DataLoadError(f"Файл не найден: {file_path}")
        except Exception as e:
            raise DataLoadError(f"Ошибка загрузки файла: {str(e)}")
    
    def _validate_dataframe(self, df: pd.DataFrame) -> None:
        """
        Валидирует DataFrame на соответствие требованиям
        
        Args:
            df: DataFrame для валидации
            
        Raises:
            DataLoadError: При несоответствии требованиям
        """
        # Проверка наличия обязательной колонки
        if REQUIRED_COLUMN not in df.columns:
            raise DataLoadError(
                f"В файле обязательно должна быть колонка '{REQUIRED_COLUMN}'"
            )
        
        # Проверка наличия числовых колонок
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < MIN_NUMERIC_COLUMNS:
            raise DataLoadError(
                f"В файле должно быть минимум {MIN_NUMERIC_COLUMNS} числовых показателей"
            )
        
        # Проверка на пустые значения в колонке регионов
        if df[REQUIRED_COLUMN].isnull().any():
            raise DataLoadError(
                f"Колонка '{REQUIRED_COLUMN}' содержит пустые значения"
            )
    
    def get_numeric_columns(self) -> List[str]:
        """Возвращает список числовых колонок"""
        if self._df is None:
            return []
        return self._df.select_dtypes(include=[np.number]).columns.tolist()
    
    def get_statistics(self) -> dict:
        """Возвращает статистику по загруженным данным"""
        if self._df is None:
            return {}
        
        return {
            'total_regions': len(self._df),
            'numeric_columns': len(self.get_numeric_columns()),
            'columns': list(self._df.columns),
            'file_path': self._file_path
        }
    
    @property
    def dataframe(self) -> pd.DataFrame:
        """Возвращает копию загруженного DataFrame"""
        return self._df.copy() if self._df is not None else None
    
    @property
    def is_loaded(self) -> bool:
        """Проверяет, загружены ли данные"""
        return self._df is not None