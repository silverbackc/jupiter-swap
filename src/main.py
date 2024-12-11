import asyncio
import os
from dotenv import load_dotenv

from clients.jupiter.api import JupiterApi
from clients.solana_rpc.rpc import SolanaRPC


async def quote():
    ja = JupiterApi()
    data = await ja.get_quote(token_in="So11111111111111111111111111111111111111112",
                       token_out="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                       amount=int(0.001 * 1e9),
                       slippage=1,
    )
    tx_data = await ja.get_tx_data(data, sender="SOL_ADDRESS")


async def test_rpc():
    rpc_url = os.getenv("SOL_RPC")
    print(rpc_url)
    if rpc_url is None:
        raise Exception()
    rpc = SolanaRPC(rpc_url)
    bhash = await rpc.get_lastest_blockhash()


if __name__ == "__main__":
    load_dotenv()
    loop = asyncio.new_event_loop()
    # loop.run_until_complete(quote())
    loop.run_until_complete(test_rpc())
