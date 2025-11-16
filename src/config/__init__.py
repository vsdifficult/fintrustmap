"""
Модуль конфигурации приложения
"""

from .settings import *
from .federal_districts import FEDERAL_DISTRICTS, get_district_by_region

__all__ = [
    'FEDERAL_DISTRICTS',
    'get_district_by_region'
]