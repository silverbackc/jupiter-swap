from typing import List, Optional, Any
from pydantic import BaseModel, Extra, validator, ValidationError


class Account(BaseModel):
    pubkey: str
    isSigner: bool
    isWritable: bool


class InstructionModel(BaseModel):
    programId: str
    accounts: List[Account]
    data: str


class SwapInstructions(BaseModel, extra=Extra.allow):
    tokenLedgerInstruction: Optional[Any]
    computeBudgetInstructions: Optional[Any]
    setupInstructions: List[InstructionModel]
    swapInstruction: InstructionModel
    cleanupInstruction: Optional[InstructionModel]
    addressLookupTableAddresses: List[str]
    prioritizationFeeLamports: int
    computeUnitLimit: int

    @validator("computeUnitLimit")
    def check_is_compute_positive(cls, v):
        if v <= 0:
            raise ValidationError("Compute unit limit should be positive.")
        return v

    def get_writable_accounts(self) -> List[str]:
        setup_ixs_accounts = [a.pubkey for ix in self.setupInstructions for a in ix.accounts if a.isWritable]
        swap_ix_accounts = [a.pubkey for a in self.swapInstruction.accounts if a.isWritable]
        cleanup_ix_accounts = (
            [a.pubkey for a in self.cleanupInstruction.accounts if a.isWritable] if self.cleanupInstruction else []
        )
        return setup_ixs_accounts + swap_ix_accounts + cleanup_ix_accounts
