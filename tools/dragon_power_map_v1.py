"""Bounded original Dragon Power US ROM/source map; no host/native build.

The local user-supplied cartridge is authoritative. No ROM download, source
clone, allocator or emulated gameplay outcome writes. CPU routine arenas are
separately labelled; this tool is not a PPU/native emulator.
"""
from pathlib import Path
import argparse,hashlib,json,zlib,re
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
ROOT=Path(__file__).resolve().parents[1]
ROM=Path('C:/NES/Dragon Power (USA).nes')
SHA='e52cc421c726181a35f0cc9e8969a8aad50abd17bdc7eea59dc065990a576147'
OUT=ROOT/'build/dragon-power-source-v1'
def digest(b):return hashlib.sha256(b).hexdigest()
def binding(p):p=Path(p);b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=digest(b))
def raw():
    b=ROM.read_bytes();assert digest(b)==SHA
    assert b[:16]==bytes.fromhex('4e45531a080421480000000000000001')
    return b
def memory(bank):
    m=bytearray(65536);r=raw();m[0x8000:]=r[16+bank*32768:16+(bank+1)*32768];return m
def disassembly(bank,pc,size):
    m=memory(bank);r=Disassembler(MPU(memory=m));end=pc+size;lines=[]
    while pc<end:
        n,t=r.instruction_at(pc);q=m[pc:pc+n]
        lines.append(f'{bank}:{pc:04X}  {q.hex(" ").upper():<8} {t}');pc+=n
    return '\n'.join(lines)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--dump',help='32KBbank:CPUhex:lengthhex')
    a=ap.parse_args()
    if a.dump:
        b,p,n=[int(v,16)for v in a.dump.split(':')];print(disassembly(b,p,n));return
    r=raw();OUT.mkdir(exist_ok=True)
    versions=[]
    for name in ['Dragon Power (USA).nes','Dragon Ball - Shen Long no Nazo (Japan).nes','Dragon Ball - Le Secret du Dragon (France).nes']:
        p=ROM.parent/name;b=p.read_bytes();versions.append(dict(**binding(p),payload_sha1=hashlib.sha1(b[16:]).hexdigest(),payload_crc32=f'{zlib.crc32(b[16:]):08X}'))
    info=dict(status='authenticated original; bounded source map/CPU witnesses separate; no allocation/port/native',ROM=binding(ROM),
              mapper=66,PRG_bytes=131072,CHR_bytes=32768,bank_model='four32KBPRG windows+four8KBCHR, bus-conflict-safe original FFCCTable',
              versions=versions,manual='https://www.digitpress.com/library/manuals/nes/Dragon%20Power.pdf',
              source_repository='No authenticated original development source/disassembly located; actual local ROM is authority.',
              original_vectors=[dict(bank=b,NMI=f'{int.from_bytes(memory(b)[0xfffa:0xfffc],"little"):04X}',
                                     RESET=f'{int.from_bytes(memory(b)[0xfffc:0xfffe],"little"):04X}',IRQ=f'{int.from_bytes(memory(b)[0xfffe:],"little"):04X}')for b in range(4)])
    (OUT/'authentication.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info,indent=2))
if __name__=='__main__':main()
