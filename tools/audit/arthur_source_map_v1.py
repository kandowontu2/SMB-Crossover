"""Authenticate the original Arthur ROM and index exact instruction candidates.

Raw matches are explicitly candidates until actual execution or control-flow
proves that they are instructions. Never infer free space from this index.
"""
from pathlib import Path
import argparse,hashlib,json,zlib
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/arthur-source-v1'
ROM=Path("C:/NES/Ghosts'n Goblins (USA).nes")
EXPECTED='a263db625853b563aca356a8651f69c9092428dd2b665b6fd5c75ea5b1439d31'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load():
    b=ROM.read_bytes();assert hashlib.sha256(b).hexdigest()==EXPECTED
    assert b[:4]==b'NES\x1a' and len(b)==16+8*16384 and b[4]==8 and b[5]==0
    assert ((b[6]>>4)|(b[7]&240))==2
    return b

def machine(bank):
    b=load();memory=[0]*65536
    memory[0x8000:0xc000]=b[16+bank*16384:16+(bank+1)*16384]
    memory[0xc000:]=b[16+7*16384:]
    return MPU(memory=memory)

def disassemble(bank,start,end):
    m=machine(bank);d=Disassembler(m);rows=[];pc=start
    while pc<end:
        size,text=d.instruction_at(pc)
        offset=16+(7 if pc>=0xc000 else bank)*16384+(pc&16383)
        rows.append(dict(bank=7 if pc>=0xc000 else bank,address=pc,offset=offset,
                         bytes=bytes(m.memory[pc:pc+size]).hex(),instruction=text))
        pc+=size
    return rows

def main():
    a=argparse.ArgumentParser();a.add_argument('--bank',type=int)
    a.add_argument('--start',type=lambda s:int(s,0));a.add_argument('--end',type=lambda s:int(s,0))
    args=a.parse_args();b=load();OUT.mkdir(parents=True,exist_ok=True)
    if args.bank is not None:
        rows=disassemble(args.bank,args.start,args.end)
        for r in rows:print(f"{r['bank']:02X}:{r['address']:04X} {r['bytes']:<6} {r['instruction']}")
        return
    opcodes={0xad:'LDA abs',0xbd:'LDA abs,X',0xb9:'LDA abs,Y',0x8d:'STA abs',0x9d:'STA abs,X',0x99:'STA abs,Y',
             0xae:'LDX abs',0xac:'LDY abs',0xce:'DEC abs',0xee:'INC abs',0x2c:'BIT abs',0xcd:'CMP abs'}
    candidates=[]
    for addr,label in ((0x04f3,'reported native player state; unconfirmed'),(0x0642,'reported weapon kind; unconfirmed'),
                       (0x0647,'reported native injury cooldown; unconfirmed'),(0x0603,'reported shot direction; unconfirmed')):
        for off in range(16,len(b)-2):
            if b[off]in opcodes and b[off+1:off+3]==addr.to_bytes(2,'little'):
                bank=(off-16)//16384;cpu=(0xc000 if bank==7 else 0x8000)+(off-16)%16384
                candidates.append(dict(bank=bank,address=cpu,offset=off,bytes=b[off:off+3].hex(),
                    opcode=opcodes[b[off]],RAM=addr,reported_role=label,status='RAW_BYTE_CANDIDATE_NOT_EXECUTION_PROOF'))
    record=dict(status='EXACT_ORIGINAL_ROM_MAPPER_AND_RAW_XREF_INDEX',ROM=str(ROM),ROM_sha256=EXPECTED,
        header=list(b[:16]),PRG_bytes=len(b)-16,CHR_ROM_bytes=0,CHR_RAM_bytes=8192,mapper=2,
        PRG_crc32=f'{zlib.crc32(b[16:]):08X}',PRG_sha1=hashlib.sha1(b[16:]).hexdigest(),
        banks=[dict(bank=i,bytes=16384,sha256=hashlib.sha256(b[16+i*16384:16+(i+1)*16384]).hexdigest())for i in range(8)],
        vectors={n:int.from_bytes(b[-6+i*2:][:2],'little')for i,n in enumerate(('NMI','RESET','IRQ'))},
        candidates=candidates,tool=dict(path=str(Path(__file__).resolve()),sha256=sha(__file__)),
        limits='No source routine authenticated yet; raw byte matches may be data. No host PRG/CHR/RAM lease requested or allocated.')
    p=OUT/'source-index.json';p.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(status=record['status'],ROM_sha256=EXPECTED,mapper=2,PRG_bytes=len(b)-16,CHR_ROM_bytes=0,
                         candidate_refs=len(candidates),vectors=record['vectors'],index_sha256=sha(p))))

if __name__=='__main__':main()
