import asyncio
from decimal import Decimal, ROUND_DOWN


async def recommend_price(fetch_offers, current_price, min_price, timeout_s=2.0):
    try:
        result = await asyncio.wait_for(
            fetch_offers(),
            timeout=timeout_s,
        )
    except asyncio.TimeoutError:
        return {
            "price": current_price,
            "decision": "HOLD",
            "reason": "Превышено время ожидания источника",
        }
    except Exception:
        return {
            "price": current_price,
            "decision": "HOLD",
            "reason": "Ошибка получения предложений",
        }

    if result["status"] != "success":
        return {
            "price": current_price,
            "decision": "HOLD",
            "reason": "Источник вернул неполные или ошибочные данные",
        }

    prices = [
        offer["price"]
        for offer in result["offers"]
        if offer["delivery_days"] is not None
        and offer["delivery_days"] <= 6
        and offer["seller"].upper() != "MYSHOP"
    ]

    if not prices:
        return {
            "price": current_price,
            "decision": "HOLD",
            "reason": "Нет подходящих предложений конкурентов",
        }

    competitor_price = min(prices)

    discounted_price = (
        competitor_price * Decimal("0.985")
    ).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    recommended_price = max(discounted_price, min_price)

    price_change = abs(recommended_price - current_price) / current_price

    if price_change > Decimal("0.30"):
        return {
            "price": recommended_price,
            "decision": "REVIEW",
            "reason": "Изменение цены превышает 30%",
        }

    return {
        "price": recommended_price,
        "decision": "APPLY",
        "reason": "Цена рассчитана по предложениям конкурентов",
    }


async def sample_fetch_offers():
    return {
        "status": "success",
        "offers": [
            {
                "seller": "myshop",
                "price": Decimal("4300.00"),
                "delivery_days": 2,
            },
            {
                "seller": "PARTS",
                "price": Decimal("4800.00"),
                "delivery_days": 3,
            },
            {
                "seller": "SLOW",
                "price": Decimal("4700.00"),
                "delivery_days": 8,
            },
        ],
    }


if __name__ == "__main__":
    print(
        asyncio.run(
            recommend_price(
                sample_fetch_offers,
                current_price=Decimal("4900.00"),
                min_price=Decimal("4500.00"),
            )
        )
    )