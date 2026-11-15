"""Read-only current shared-owner entry patterns, not CPU qualification."""
from hashlib import sha256
from pathlib import Path
import json
from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU

PIN='590e0ae60414d98d4b0a4d74874af58b93c6e720e8156220e0648966128b5f1f'


def run(raw):
    assert sha256(raw).hexdigest()==PIN
    start=16+65*8192;bank=raw[start:start+8192];rows=[]
    for label,pattern in(('old_cold_prologue','08488a489848a90048'),('old_retire_prologue','08488a489848a90148')):
        needle=bytes.fromhex(pattern);found=[0xa000+i for i in range(len(bank)-len(needle)+1)if bank[i:i+len(needle)]==needle]
        rows.append(dict(label=label,pattern=pattern,exact_current_hits=found))
    memory=[0]*65536;memory[0xa000:0xc000]=bank;decoder=Disassembler(MPU(memory=memory));code=[]
    for lo,hi in((0xae00,0xae22),(0xb100,0xb130)):
        pc=lo
        while pc<hi:
            size,text=decoder.instruction_at(pc);code.append([pc,text]);pc+=size
    references=[[0xa000+i,bank[i]]for i in range(len(bank)-2)if bank[i]in(0x20,0x4c)and bank[i+1:i+3]==bytes.fromhex('0aae')]
    public=[]
    for index in range(37):
        at=0x108c+3*index;assert bank[at]==0x4c
        public.append([index,0xa000+at,bank[at+1]+256*bank[at+2]])
    return dict(ROM_SHA256=PIN,native_bank65_SHA256=sha256(bank).hexdigest(),patterns=rows,
        current_public37_rows=public,current_AE0A_literal_call_candidates=references,local_disassembly=code,
        actual_ADE0_AF00=bank[0xde0:0xf00].hex(),
        actual_ABB0_ABE0=bank[0xbb0:0xbe0].hex(),
        actual_B070_B110=bank[0x1070:0x1110].hex(),
        scope='Byte-pattern inspection only; no address is admitted as a live entry without current caller proof',outputs=0,Mesen=False)


if __name__=='__main__':print(json.dumps(run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()),separators=(',',':')),flush=True)
