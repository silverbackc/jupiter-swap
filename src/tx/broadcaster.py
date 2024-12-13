import json

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment, Confirmed

from solders.keypair import Keypair
from solana.rpc.types import TxOpts
from solders.transaction import VersionedTransaction
from solders.message import to_bytes_versioned


class TxSender:
    def __init__(self, rpc_url, private_key, skip_preflight: bool = True, commitment: Commitment = Confirmed):
        self.client = AsyncClient(rpc_url)
        self.private_key = private_key
        self.commitment = commitment
        self.opts = TxOpts(
            skip_preflight=skip_preflight,
            preflight_commitment=self.commitment,
        )
        self.signer = self.get_signer()

    async def send_tx(self, vtx: VersionedTransaction) -> str:
        signature = self.signer.sign_message(to_bytes_versioned(vtx.message))
        signed_txn = VersionedTransaction.populate(vtx.message, [signature])
        result = await self.client.send_transaction(txn=signed_txn, opts=self.opts)
        transaction_id = json.loads(result.to_json())["result"]
        return transaction_id
    
    async def simulate_tx(self, vtx: VersionedTransaction):
        signature = self.signer.sign_message(to_bytes_versioned(vtx.message))
        signed_txn = VersionedTransaction.populate(vtx.message, [signature])
        sim_resp = await self.client.simulate_transaction(signed_txn, commitment=self.commitment)
        return sim_resp

    def get_signer(self):
        return Keypair.from_bytes(bytes.fromhex(self.private_key))
