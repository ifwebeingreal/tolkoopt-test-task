import asyncio
import unittest
from decimal import Decimal

from starter import recommend_price, sample_fetch_offers


class TestRecommendPrice(unittest.IsolatedAsyncioTestCase):

    async def test_normal_price(self):
        result = await recommend_price(
            sample_fetch_offers,
            current_price=Decimal("4900.00"),
            min_price=Decimal("4500.00"),
        )

        self.assertEqual(result["price"], Decimal("4728.00"))
        self.assertEqual(result["decision"], "APPLY")

    async def test_timeout(self):
        async def slow_fetch():
            await asyncio.sleep(1)

        result = await recommend_price(
            slow_fetch,
            current_price=Decimal("5000.00"),
            min_price=Decimal("4000.00"),
            timeout_s=0.01,
        )

        self.assertEqual(result["price"], Decimal("5000.00"))
        self.assertEqual(result["decision"], "HOLD")

    async def test_no_valid_offers(self):
        async def fetch():
            return {
                "status": "success",
                "offers": [
                    {
                        "seller": "MYSHOP",
                        "price": Decimal("4000.00"),
                        "delivery_days": 2,
                    },
                    {
                        "seller": "OTHER",
                        "price": Decimal("4500.00"),
                        "delivery_days": 10,
                    },
                ],
            }

        result = await recommend_price(
            fetch,
            current_price=Decimal("3000.00"),
            min_price=Decimal("4000.00"),
        )

        self.assertEqual(result["price"], Decimal("3000.00"))
        self.assertEqual(result["decision"], "HOLD")

    async def test_review_large_change(self):
        async def fetch():
            return {
                "status": "success",
                "offers": [
                    {
                        "seller": "OTHER",
                        "price": Decimal("2000.00"),
                        "delivery_days": 2,
                    },
                ],
            }

        result = await recommend_price(
            fetch,
            current_price=Decimal("5000.00"),
            min_price=Decimal("1500.00"),
        )

        self.assertEqual(result["price"], Decimal("1970.00"))
        self.assertEqual(result["decision"], "REVIEW")


if __name__ == "__main__":
    unittest.main()