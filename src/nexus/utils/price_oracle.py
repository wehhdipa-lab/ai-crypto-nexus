"""Multi-source price oracle."""
import httpx
class PriceOracle:
    async def get_price(self, token: str, vs: str = "usd") -> float:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"https://api.coingecko.com/api/v3/simple/price?ids={token}&vs_currencies={vs}")
            return r.json().get(token, {}).get(vs, 0.0)
