# extensions.py
import requests
import json


class APIException(Exception):
    """Пользовательское исключение для ошибок API и ввода"""
    pass


class CryptoConverter:
    """
    Класс для получения курса валют через внешнее API.
    Используется статический метод get_price().
    """

    @staticmethod
    def get_price(base: str, quote: str, amount: str) -> float:
        """
        Возвращает цену amount единиц base в валюте quote.
        base  - исходная валюта
        quote - целевая валюта
        amount - количество (строка, преобразуется в float)
        """
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise APIException(f"Количество должно быть положительным числом, вы ввели {amount}")
        except ValueError:
            raise APIException(f"Не удалось распознать количество: '{amount}'. Введите число.")

        # Доступные валюты (можно расширить)
        # API: https://api.exchangerate.host/latest?base=RUB
        # или другой. Возьмём exchangerate.host (бесплатно, без ключа)
        # Сначала нужно получить курс base к RUB, затем RUB к quote? Проще — direct курс, если есть.
        # exchangerate.host поддерживает пары: https://api.exchangerate.host/convert?from=USD&to=EUR&amount=1

        # Нормализуем валюты (допустим: USD, EUR, RUB)
        allowed = ["USD", "EUR", "RUB"]
        base_upper = base.upper()
        quote_upper = quote.upper()

        if base_upper not in allowed:
            raise APIException(f"Валюта {base} не поддерживается. Доступны: {', '.join(allowed)}")
        if quote_upper not in allowed:
            raise APIException(f"Валюта {quote} не поддерживается. Доступны: {', '.join(allowed)}")
        if base_upper == quote_upper:
            # Если валюты одинаковые, просто возвращаем amount
            return amount_float

        # Запрос к API
        url = f"https://api.exchangerate.host/convert?from={base_upper}&to={quote_upper}&amount={amount_float}"
        try:
            response = requests.get(url, timeout=10)
            data = json.loads(response.text)
        except requests.RequestException as e:
            raise APIException(f"Ошибка сети или API: {e}")
        except json.JSONDecodeError:
            raise APIException("Ошибка парсинга JSON от API")

        if not data.get("success"):
            # некоторые API в success=false дают ошибку, но exchangerate.host возвращает success всегда
            # но на всякий случай проверим наличие result
            if "result" not in data:
                raise APIException(f"API вернул ошибку: {data.get('error', 'Неизвестная ошибка')}")

        # В ответе поле result — итоговая сумма
        result = data.get("result")
        if result is None:
            raise APIException("Не удалось получить курс. Проверьте названия валют.")

        # Округляем до 2 знаков (можно и больше)
        return round(result, 2)