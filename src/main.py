import asyncio

from clients.jupiter.api import JupiterApi

async def quote():
    ja = JupiterApi()
    data = await ja.get_quote(token_in="So11111111111111111111111111111111111111112",
                       token_out="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                       amount=int(0.001 * 1e9),
                       slippage=1,
    )
    tx_data = await ja.get_tx_data(data, sender="SOL_ADDRESS")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(quote())