from typing import List, Any, Optional

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment, Confirmed

from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.account import Account

from clients.base.client import BaseHTTPClient


class SolanaRPC(BaseHTTPClient):
    def __init__(self, rpc_url: str, commitment: Commitment = Confirmed):
        self.url = rpc_url
        self.client = AsyncClient(rpc_url)
        self.commitment = commitment

    async def get_lastest_blockhash(self, commitment: Commitment = None) -> Hash:
        return (await self.client.get_latest_blockhash(commitment if commitment else self.commitment)).value.blockhash

    async def get_multiple_accounts_info(self, accounts: List[str]) -> List[Account]:
        return (await self.client.get_multiple_accounts([Pubkey.from_string(a) for a in accounts])).value

    async def custom_rpc_call(self, method: str, params: List[Any]):
        payload = {"method": method, "params": params, "jsonrpc": "2.0", "id": "jupiter-swap"}
        return await self._post(self.url, payload)

    async def get_priority_fee(self, writable_accounts: Optional[List[str]] = None) -> int:
        prio_fees_data = (await self.custom_rpc_call(method="getRecentPrioritizationFees", params=[writable_accounts]))["result"]
        positive_prio_fees = [p["prioritizationFee"] for p in prio_fees_data if p["prioritizationFee"] > 0]
        return int(sum(positive_prio_fees) / max(len(positive_prio_fees),1))
