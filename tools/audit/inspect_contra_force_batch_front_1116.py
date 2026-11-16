"""Current caller-front bytes/labels; metadata inspection, no CPU execution."""
from hashlib import sha256
from pathlib import Path
import json
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

R=Path(__file__).resolve().parents[2]
PIN='91dc4ac58ae749bc81f1ef91953c7c3e5aba73dd07e4b6ea2cd3059d1cdb41cc'
H=lambda b:sha256(b).hexdigest()


def run(raw):
    assert H(raw)==PIN
    bank=raw[16+124*8192:16+125*8192]
    mem=[0]*65536;mem[0xa000:0xc000]=bank;d=Disassembler(MPU(memory=mem))
    spans=[]
    for name,lo,hi in(('Selector',0xa4fb,0xa556),('CallerFront',0xa1cc,0xa200),('Suffix',0xa60d,0xa63e)):
        pc=lo;rows=[]
        while pc<hi:
            n,text=d.instruction_at(pc);rows.append(dict(PC=pc,hex=bytes(mem[pc:pc+n]).hex(),instruction=text));pc+=n
        data=bank[lo&8191:(hi&8191)]
        spans.append(dict(name=name,CPU_half_open=[lo,hi],SHA256=H(data),hex=data.hex(),linear_disassembly_leads_only=rows))
    q=dict(actual_parent_SHA256=PIN,physical_PRG124_SHA256=H(bank),spans=spans,
        no_new_arrays_or_CPU_or_state_or_overlay=True,outputs=0)
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    print('RESULT '+json.dumps(run(raw),separators=(',',':')),flush=True)
