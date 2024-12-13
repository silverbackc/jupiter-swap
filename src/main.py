import asyncio
import os
from dotenv import load_dotenv

from clients.jupiter.api import JupiterApi
from clients.solana_rpc.rpc import SolanaRPC
from tx.builder import TxBuilder
from tx.broadcaster import TxSender

load_dotenv()

RPC_URL = os.getenv("SOL_RPC")
PAYER = os.getenv("PAYER")
SOL_PRIVATE_KEY = os.getenv("SOL_PRIVATE_KEY")


async def quote():
    ja = JupiterApi()
    data = await ja.get_quote(token_in="So11111111111111111111111111111111111111112",
                       token_out="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                       amount=int(0.001 * 1e9),
                       slippage=5,
    )
    tx_data = await ja.get_tx_data(data, sender=PAYER)
    return tx_data


async def test_quote_rpc():
    tx = await quote()
    rpc = SolanaRPC(RPC_URL)
    print(await rpc.get_priority_fee(tx.get_writable_accounts()))


async def test_complete_flow():
    tx = await quote()
    tb = TxBuilder(RPC_URL)
    vtx, _ = await tb.build_tx_from_instructions(
        sender=PAYER,
        tx_data=tx,
    )
    ts = TxSender(RPC_URL, SOL_PRIVATE_KEY)
    res = await ts.simulate_tx(vtx)
    # res = await ts.send_tx(vtx)
    print(res)



if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(test_complete_flow())
