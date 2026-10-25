"""Inventory native sprite pairs used by each simultaneous weapon loadout.

The source CPU, not guessed pose ranges, generates the frame sets. This is a
graphics-budget probe; it does not prove exhaustive gameplay frame coverage.
"""
from pathlib import Path
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('pn_check',ROOT/'tools/audit/check_parodius_native.py')
check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
spec=importlib.util.spec_from_file_location('pn_art',ROOT/'tools/reference/export_parodius_art.py')
art=importlib.util.module_from_spec(spec);spec.loader.exec_module(art)


def main():
    raw,cpu=art.native.source_cpu();records=art.records(raw)
    chr_data=raw[131088:]
    seen={}
    for variant in range(4):
        for mode in (0,0x40,0x80):
            for big in (False,True):
                cpu.memory[:0x8000]=[0]*0x8000
                cpu.memory[0x8f]=cpu.memory[0x87]=variant
                cpu.memory[0x6200]=1
                cpu.memory[0x6500]=0x80
                cpu.memory[0x63e0]=1
                cpu.memory[0x6260]=80
                cpu.memory[0x62c0]=112
                cpu.memory[0x76]=mode|0x28|(4 if variant<2 else 3)
                cpu.memory[0x7a]=2
                cpu.memory[0x7b]=2 if big else 0
                for index in range(64):
                    cpu.memory[0x640+2*index]=80
                    cpu.memory[0x641+2*index]=112
                for frame in range(1600 if big else 640):
                    cpu.memory[0x23]=frame&255
                    direction=[0,1,4,8,5,9,2,6,10][(frame//23)%9]
                    cpu.memory[0x42]=0x40|direction
                    cpu.memory[0x40]=0x40 if frame%7==0 else 0
                    cpu.x=0
                    check.run_call(cpu,0x8191 if cpu.memory[0x7b]&2 else 0x824c,{0x83b2},
                                   art.native.EXTERNALS,[],0)
                    for index in range(1,28):
                        cpu.memory[0x6230+index]=1 if frame>160 and frame%31==0 else 0
                    cpu.x=0
                    check.run_call(cpu,0x8493,set(),art.native.EXTERNALS,[],
                                   int(frame>220 and frame%13==0))
                    key=(variant,cpu.memory[0x87],mode)
                    frames=seen.setdefault(key,set())
                    for index in range(28):
                        value=cpu.memory[0x6410+index]
                        if value:frames.add(value)
    report=[]
    for (variant,skin,mode),frames in sorted(seen.items()):
        pairs=set()
        for frame in frames:
            for part in records[frame]['parts']:
                tile=part['tile'];offset=(tile&1)*4096+(tile&254)*16
                page=[skin,4,11,5][offset//1024]
                address=page*1024+offset%1024
                pairs.add(bytes(chr_data[address:address+32]))
        report.append(dict(variant=variant,skin=skin,gun_mode=mode,frames=sorted(frames),
                           native_pairs=len(pairs),bytes=len(pairs)*32))
    output=ROOT/'reference/parodius-nes/art/frame-sets.json'
    output.write_text(json.dumps(dict(source_sha256=art.native.SHA,
                                     exhaustive=False,loadouts=report),indent=2)+'\n')
    print(json.dumps([dict(variant=r['variant'],skin=r['skin'],gun=r['gun_mode'],
                           frames=len(r['frames']),pairs=r['native_pairs']) for r in report]))


if __name__=='__main__':main()
