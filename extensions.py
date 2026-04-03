# extensions.py
import requests
import json


class APIException(Exception):
    pass


class CryptoConverter:

    @staticmethod
    def get_price(base: str, quote: str, amount: str) -> float:

        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise APIException(f"Количество должно быть положительным числом, вы ввели {amount}")
        except ValueError:
            raise APIException(f"Не удалось распознать количество: '{amount}'. Введите число.")
            
        allowed = ["USD", "EUR", "RUB"]
        base_upper = base.upper()
        quote_upper = quote.upper()

        if base_upper not in allowed:
            raise APIException(f"Валюта {base} не поддерживается. Доступны: {', '.join(allowed)}")
        if quote_upper not in allowed:
            raise APIException(f"Валюта {quote} не поддерживается. Доступны: {', '.join(allowed)}")
        if base_upper == quote_upper:
            return amount_float

        url = f"https://api.exchangerate.host/convert?from={base_upper}&to={quote_upper}&amount={amount_float}"
        try:
            response = requests.get(url, timeout=10)
            data = json.loads(response.text)
        except requests.RequestException as e:
            raise APIException(f"Ошибка сети или API: {e}")
        except json.JSONDecodeError:
            raise APIException("Ошибка парсинга JSON от API")

        if not data.get("success"):
            
            if "result" not in data:
                raise APIException(f"API вернул ошибку: {data.get('error', 'Неизвестная ошибка')}")

        result = data.get("result")
        if result is None:
            raise APIException("Не удалось получить курс. Проверьте названия валют.")

        return round(result, 2)
