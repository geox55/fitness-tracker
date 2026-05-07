"""Анонимизация — REQ-17 + NFR-03.

Все идентификаторы хэшируются sha256(salt + raw), все даты сдвигаются на
random offset в [-365, +365] дней, **детерминированно** на пользователя
(один и тот же raw_user_id → один и тот же offset). Это сохраняет
относительные дельты внутри пользователя, но скрывает абсолютные даты.
"""

from __future__ import annotations

import hashlib
import hmac
import struct


def anon_user_id(raw: str, *, salt: str) -> str:
    """sha256-hex c HMAC; выдаём короткий префикс (16 hex = 64 бита).

    HMAC, а не просто sha256(salt+raw): защищает от length-extension и
    более стандартен. 64 бита уникальности достаточно: коллизии при 2^32
    пользователях ≈ 2.3·10⁻¹⁰ — приемлемо для тренировочного датасета.
    """
    digest = hmac.new(salt.encode("utf-8"), raw.encode("utf-8"), hashlib.sha256)
    return digest.hexdigest()[:16]


def date_offset_days(raw_user_id: str, *, salt: str) -> int:
    """Детерминированный offset в [-365, +365] на raw_user_id.

    Берём первые 8 байт HMAC, конвертируем в знаковое 64-битное число,
    модулим на 731 (2·365+1), сдвигаем в нужный диапазон. Стабильно при
    повторных запусках (REQ-20).
    """
    digest = hmac.new(
        salt.encode("utf-8"), (raw_user_id + ":dateoff").encode("utf-8"),
        hashlib.sha256,
    ).digest()
    (packed,) = struct.unpack(">q", digest[:8])
    return int(packed % 731) - 365
