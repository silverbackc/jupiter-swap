from typing import List, Any
import json

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment, Confirmed, Finalized, Processed

from solders.pubkey import Pubkey
from solders.hash import Hash

from clients.base.client import BaseHTTPClient

class SolanaRPC(BaseHTTPClient):
    def __init__(self, rpc_url: str, commitment: Commitment = Confirmed):
        self.url = rpc_url
        self.client = AsyncClient(rpc_url)
        self.commitment = commitment

    async def get_lastest_blockhash(self, commitment: Commitment = None) -> Hash:
        return (await self.client.get_latest_blockhash(commitment if commitment else self.commitment)).value.blockhash

    async def get_multiple_accounts_info(self, accounts: List[str]):
        return (await self.client.get_multiple_accounts([Pubkey.from_string(a) for a in accounts])).value

    async def custom_rpc_call(self, method: str, params: List[Any]):
        payload = {"method": method, "params": params, "jsonrpc": "2.0", "id": "jupiter-swap"}
        return await self._post(self.url, json.dumps(payload), debug=True)
