from typing import Tuple, List
import base64
import logging

from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solders.instruction import Instruction, AccountMeta
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.address_lookup_table_account import AddressLookupTableAccount, AddressLookupTable
from solders.signature import Signature

from clients.jupiter.swap_instructions import SwapInstructions
from clients.solana_rpc.rpc import SolanaRPC

log = logging.getLogger(__name__)

MINIMUM_LAMPORTS = 10_000
MAXIMUM_LAMPORTS = 5_000_000

class TxBuilder:
    def __init__(self, rpc_url):
        self.rpc = SolanaRPC(rpc_url)

    async def build_tx_from_instructions(
        self, sender: str, tx_data: SwapInstructions, priority_fee_micro_lamports: int = 0
    ) -> Tuple[str, int]:
        try:
            payer = Pubkey.from_string(sender)
            # Setup instructions
            setup_ixs = [
                Instruction(
                    program_id=Pubkey.from_string(six.programId),
                    data=base64.b64decode(six.data),
                    accounts=[
                        AccountMeta(Pubkey.from_string(a.pubkey), is_signer=a.isSigner, is_writable=a.isWritable)
                        for a in six.accounts
                    ],
                )
                for six in tx_data.setupInstructions
            ]
            swap_ix = Instruction(
                program_id=Pubkey.from_string(tx_data.swapInstruction.programId),
                data=base64.b64decode(tx_data.swapInstruction.data),
                accounts=[
                    AccountMeta(Pubkey.from_string(a.pubkey), is_signer=a.isSigner, is_writable=a.isWritable)
                    for a in tx_data.swapInstruction.accounts
                ],
            )
            # Check if cleanupInstruction isn't empty
            cleanup_ix = None
            if tx_data.cleanupInstruction:
                cleanup_ix = Instruction(
                    program_id=Pubkey.from_string(tx_data.cleanupInstruction.programId),
                    data=base64.b64decode(tx_data.cleanupInstruction.data),
                    accounts=[
                        AccountMeta(Pubkey.from_string(a.pubkey), is_signer=a.isSigner, is_writable=a.isWritable)
                        for a in tx_data.cleanupInstruction.accounts
                    ],
                )
            # Minimum conditions to build tx
            if priority_fee_micro_lamports == 0:
                priority_fee_micro_lamports = await self.rpc.get_priority_fee(tx_data.get_writable_accounts())
                priority_fee_micro_lamports = _adjust_priority_fee(priority_fee_micro_lamports, tx_data.computeUnitLimit)
            total_prio_fee = calculate_total_priority_fee(priority_fee_micro_lamports, tx_data.computeUnitLimit)
            log.info(f"total prio fee lamports={total_prio_fee}")
            ixs = _preprend_compute_instructions(
                setup_ixs + [swap_ix], tx_data.computeUnitLimit, priority_fee_micro_lamports
            )
            if cleanup_ix:
                ixs += [cleanup_ix]

            # Getting lookup table info
            account_info = await self.rpc.get_multiple_accounts_info(tx_data.addressLookupTableAddresses)

            # https://solana.com/docs/rpc/http/getmultipleaccounts
            address_table_list = [
                AddressLookupTableAccount(
                    key=Pubkey.from_string(k),
                    addresses=AddressLookupTable.deserialize(
                        account_info[i].data
                    ).addresses
                )
                for i, k in enumerate(tx_data.addressLookupTableAddresses)
            ]
            latest_blockhash: Hash = await self.rpc.get_lastest_blockhash()
            msg_v0 = MessageV0.try_compile(payer, ixs, address_table_list, latest_blockhash)
            vtx = VersionedTransaction.populate(msg_v0, [Signature.default()])
            return vtx, total_prio_fee
        except Exception as e:
            log.warning(e)
            raise e


def _preprend_compute_instructions(
    instructions_list: List[Instruction], compute_unit_limit: int, priority_fee_micro_lamports: int
) -> List[Instruction]:
    # gas instructions to replace old budget info or add new ones
    cpu_limit_ix = set_compute_unit_limit(compute_unit_limit)
    # Adding compute unit price (in micro lamports)
    cpu_price_ix = set_compute_unit_price(priority_fee_micro_lamports)
    return [cpu_limit_ix, cpu_price_ix] + instructions_list


def calculate_total_priority_fee(priority_fee_micro_lamports: int, compute_unit_limit: int) -> int:
    return int(priority_fee_micro_lamports * compute_unit_limit / 10**6)


def _adjust_priority_fee(priority_fee_micro_lamports: int, compute_unit_limit: int) -> int:
    """Calculate final priority fee in micro lamports, given min and max total priority fee and RPC priority fee at High level

    Args:
        priority_fee_micro_lamports (int): returned from RPC
        compute_unit_limit (int): compute units required for tx

    Returns:
        int: The adjusted priority fee per unit of compute (in micro lamports)
    """
    min_micro_lamps = int((MINIMUM_LAMPORTS * 10**6) / compute_unit_limit)
    max_micro_lamps = int((MAXIMUM_LAMPORTS * 10**6) / compute_unit_limit)
    return min(max(priority_fee_micro_lamports, min_micro_lamps), max_micro_lamps)
