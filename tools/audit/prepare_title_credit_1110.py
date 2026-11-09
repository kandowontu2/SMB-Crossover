"""Fill the existing title footer without changing menu code or VRAM length."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

R = Path(__file__).resolve().parents[2]
SOURCE = R / 'tools/reference/title_credit_1110.s'
SHA = lambda data: hashlib.sha256(data).hexdigest()


def encode(s):
    return bytes(36 if c == ' ' else ord(c)-55 for c in s)


def apply_credit(raw, credit):
    pattern = (bytes((0x22,0x46,18))+encode('      START       ')
               +bytes((0x22,0x86,18))+encode('      OPTIONS     ')
               +bytes((0x22,0xc6,18))+encode('                  '))
    assert raw.count(pattern) == 1
    offset = raw.index(pattern)+45
    assert len(credit) == 18 and credit == encode('   BY KANDOWONTU  ')
    result = raw[:offset]+credit+raw[offset+18:]
    assert len(result) == len(raw)
    return result, dict(file_offset=offset, old_hex=raw[offset:offset+18].hex(),new_hex=credit.hex())


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--rom',type=Path,required=True)
    cli.add_argument('--output',type=Path,required=True)
    args=cli.parse_args()
    out=args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    parent=args.rom.read_bytes()
    out.mkdir()
    with tempfile.TemporaryDirectory(dir=out) as directory:
        temp=Path(directory)
        cfg,obj,binary=(temp/name for name in ('credit.cfg','credit.o','credit.bin'))
        cfg.write_text('MEMORY { M:start=$0000,size=$0012,file=%O; } SEGMENTS { CREDIT:load=M,type=ro; }')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
        candidate,patch=apply_credit(parent,binary.read_bytes())
    (out/'candidate.nes').write_bytes(candidate)
    receipt=dict(passed=True,native_verified=False,parent_SHA256=SHA(parent),candidate_SHA256=SHA(candidate),
                 patches=[patch],text='BY KANDOWONTU',PPU_start=0x22c6,
                 scope='Only18existing footer tiles change; title command lengths and menu code unchanged.',
                 bindings={str(args.rom.resolve()):SHA(parent),str(SOURCE):SHA(SOURCE.read_bytes()),
                           str(Path(__file__).resolve()):SHA(Path(__file__).read_bytes())})
    (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__':
    main()
