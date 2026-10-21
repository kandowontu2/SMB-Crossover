"""Build a diagnostic ROM restoring the old NMI graphics-bank behavior.

This does not change the shipping ROM. It removes only the C-bank restore
and malformed-header guard, so the real controller regression can identify
the previously unsafe interrupt path against the same game code/assets.
"""
from pathlib import Path
import argparse,json,re,shutil,hashlib

ROOT=Path(__file__).resolve().parents[2]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mapper',choices=('mmc3','mmc5'),default='mmc3');args=ap.parse_args()
    source=ROOT/f'build/smb-crossover-{args.mapper}.nes'
    labels={m[2]:int(m[1],16) for line in source.with_suffix('.lbl').read_text().splitlines()
            if (m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.([\w]+)',line))}
    rom=bytearray(source.read_bytes());patches=[]
    for start,end,bank,base in [('NmiBankCRestoreWrite','NmiBankCRestoreDone',63,0xe000),
                               ('MetaspriteHeaderCheck','MetaspriteHeaderValid',4,0xa000)]:
        lo,hi=labels[start],labels[end]
        offset=16+bank*8192+lo-base
        patches.append(dict(start=start,cpu=lo,bank=bank,old=rom[offset:offset+hi-lo].hex()))
        rom[offset:offset+hi-lo]=bytes([0xea])*(hi-lo)
    out=ROOT/f'build/diagnostics/smb-crossover-{args.mapper}-legacy-bank-fault.nes';out.parent.mkdir(exist_ok=True)
    out.write_bytes(rom)
    for suffix in ('.lbl','.dbg'):shutil.copyfile(source.with_suffix(suffix),out.with_suffix(suffix))
    out.with_suffix('.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),patches=patches),indent=2)+'\n')
    print(out)


if __name__=='__main__':main()
