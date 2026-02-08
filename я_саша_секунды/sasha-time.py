def to_sasha_time_simple(hours=0, minutes=0, seconds=0):
    """
    Упрощенная версия конвертации в Саша-время.
    Каждая единица времени конвертируется независимо.
    """
    # Соотношения
    S_HOUR_TO_MIN = 720  # 1 Саша-час = 720 обычных минут
    S_MIN_TO_MIN = 12    # 1 Саша-минута = 12 обычных минут
    S_SEC_TO_SEC = 42    # 1 Саша-секунда = 42 обычных секунды
    
    # Конвертируем независимо
    sasha_hours = (hours * 60) / S_HOUR_TO_MIN  # Часы → Саша-часы
    sasha_minutes = minutes / S_MIN_TO_MIN       # Минуты → Саша-минуты
    sasha_seconds = seconds / S_SEC_TO_SEC       # Секунды → Саша-секунды
    
    # Суммируем и нормализуем
    total_sasha_minutes = sasha_hours * 60 + sasha_minutes + sasha_seconds / 60
    
    s_hours = int(total_sasha_minutes // 60)
    s_minutes = int(total_sasha_minutes % 60)
    s_seconds = (total_sasha_minutes - int(total_sasha_minutes)) * 60
    
    return s_hours, s_minutes, s_seconds

print(to_sasha_time_simple(3, 2, 0))