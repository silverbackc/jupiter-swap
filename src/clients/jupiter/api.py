import logging
from pydantic import ValidationError
from typing import Dict


from clients.base.client import BaseHTTPClient
from clients.jupiter.swap_instructions import SwapInstructions

JUPITER_URL = "https://quote-api.jup.ag/v6"
log = logging.getLogger(__name__)


class JupiterApi(BaseHTTPClient):
    def __init__(self):
        pass

    async def get_quote(self, token_in, token_out, amount, slippage=None):
        url = f"{JUPITER_URL}/quote?inputMint={token_in}&outputMint={token_out}&amount={amount}"
        url += f"&slippageBps={int(slippage * 100)}"
        data = await self._get(url)
        return data
    
    async def get_tx_data(self, route: Dict, sender: str):
        try:
            swap_params = {
                "quoteResponse": route,
                "userPublicKey": sender,
                "wrapAndUnwrapSol": True,
                "dynamicComputeUnitLimit": True,
            }

            swap_instr_resp = await self._post(
                f"{JUPITER_URL}/swap-instructions",
                data=swap_params,
            )
            print(type(swap_instr_resp))
            tx_data = SwapInstructions(**swap_instr_resp)
            log.info(f"prioritizationFeeLamports: {tx_data.prioritizationFeeLamports}")
            return tx_data
        except ValidationError as v_e:
            log.warning(f"validation error in get_tx_api: {v_e}")
            raise v_e
