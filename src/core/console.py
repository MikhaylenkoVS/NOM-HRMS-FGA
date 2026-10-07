"""Совместимость консольного вывода для CLI-точек входа.

Модуль решает одну задачу: не дать консольным точкам входа упасть с
``UnicodeEncodeError`` при печати русского текста. На Windows кодировка
*перенаправленного* stdout/stderr по умолчанию — ANSI (cp1251/cp1252),
поэтому ``print("ШАГ 1 …")`` в файл или в канал падает с исключением,
тогда как в реальной консоли (WriteConsoleW) тот же вывод работает.

Решение — переключить потоки на UTF-8 с политикой ``errors="replace"``:
предсказуемая кодировка важнее падения, а нечитаемые символы заменяются,
а не роняют программу.
"""

from __future__ import annotations

import sys

__all__ = ["ensure_utf8_stdio"]


def ensure_utf8_stdio(*, errors: str = "replace") -> None:
    """Переключить ``sys.stdout`` и ``sys.stderr`` на UTF-8.

    Функция идемпотентна и безопасна в окружениях, где поток не поддерживает
    ``reconfigure`` (например, подменённые объекты захвата вывода в тестах):
    такие потоки просто пропускаются.

    Parameters
    ----------
    errors : str, optional
        Политика обработки символов, непредставимых в целевой кодировке.
        Значение по умолчанию ``"replace"`` — предпочтительнее исключения.

    Returns
    -------
    None
        Функция меняет состояние ``sys.stdout``/``sys.stderr`` на месте.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors=errors)
        except (ValueError, OSError):
            # Поток закрыт либо кодировка не может быть изменена.
            continue
