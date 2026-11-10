"""Actual forced-blank NMI/IRQ cuts for current-a5 eighth330 cold boot.

The partial final row is distinguished by real row, destination page and
Y=0/E0/other, so its last-byte/header-boundary branch is actually exercised.
No ROM, native gameplay, ordinary-frame interrupt claim or output file.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import check_sonic_eighth_cold_owner_1110 as E
import check_sonic_seventh_cold_vectors_1110 as Old

R,O,N,V=E.R,E.O,E.N,Old.V


def qualify(trial,packet):
    spans=((251,0xaf40,0xb000),(251,0xb9d6,0xba00),(193,0xae00,0xb013),
           (193,0xabc9,0xabd5),(219,0xb1ba,0xb1fc),
           (2,0xd25e,0xd25e+len(packet['startup']['image'])))
    counts=Counter();minimum=224;resumed=0;partial=set();boot_writes=0
    for owner in range(37,44):
        print('Actual eighth cold vectors owner',owner,flush=True)
        m=O.blank(trial);O.scene(m,owner);c=V.entry(m)
        points=set();consumed=set()
        for _ in range(4_000_000):
            if c.pc==V.STOP:break
            tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else m.rawtags[1]
            used=0x15a<=c.pc<0x17b or any(tag==bank and lo<=c.pc<hi for bank,lo,hi in spans)
            boot=owner==43 and tag==2 and 0xd25e<=c.pc<0xd25e+len(packet['startup']['image'])
            if used:
                phase=m.ram[2][0x1fe0],m.ram[3][0x1fe0]
                cursor=(m[5],m[4],c.y if c.y in(0,0xe0)else'other')if boot else None
                if boot and m[5]==7 and m[4]==0xbf:partial.add((c.pc,c.y if c.y in(0,0xe0)else'other'))
                key=tag,c.pc,c.sp,c.p&4,phase,cursor
                if key not in points:
                    points.add(key);O.clear_logs(m)
                    for kind in('FF','IRQ')if not c.p&4 else('FF',):
                        minimum=min(minimum,V.interrupt(Old.clone(c),kind));counts[owner,kind]+=1
                    boundary=tag,c.pc,phase,cursor
                    if c.pc in(0xaf40,0xb9d6,0xae8c,0xd25e)and boundary not in consumed:
                        consumed.add(boundary);minimum=min(minimum,V.interrupt(c,'FF'));resumed+=1
            # Attribute each private write to the actual foreground opcode.
            if boot:
                O.clear_logs(m);V.step(c)
                assert not any(bank==3 and at>=0x1fe0 for bank,at,_ in m.ram_writes)
                boot_writes+=len(m.ram_writes)
            else:V.step(c)
        else:raise AssertionError(('Full eighth cold bound',owner,hex(c.pc)))
        assert c.p&1 and c.sp==224 and len(points)>100
        if owner==43:E.owned(m,packet)
        assert counts[owner,'FF']and counts[owner,'IRQ']
        print('Eighth owner cuts',owner,{k:v for(o,k),v in counts.items()if o==owner},flush=True)
    # Both copy and verify final-page E0 branches must be represented.
    assert len({pc for pc,y in partial if y==0xe0})>=4,partial
    assert boot_writes==8160,boot_writes
    return dict(actual_cuts={f'{o}/{k}':v for(o,k),v in sorted(counts.items())},minimum_SP=minimum,
        full_cold_resumed_vectors=resumed,actual_startup_private_writes=boot_writes,
        startup_header_writes=0,partial_BF_E0_cut_PCs=sorted(pc for pc,y in partial if y==0xe0),
        scope='All7 cold owners; mappedPC/SP/I/header-phase cuts. Sonic startup also distinguishes actual row/destination page/Y=0/E0/other. Actual forced-blank NMI and unmasked hardware IRQ restore foreground/PPU/state. No ordinary-frame interrupts or native gameplay.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    assert args.output.resolve().is_relative_to(R/'build')and not args.output.exists()
    old=E.C.ROM.read_bytes();current=(Path('C:/Users/kando/Downloads')/'SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    image,_,packet,_,_=E.proposal(old,current)
    receipt=qualify(E.C.Current.W.bundle(image),packet)
    assert not args.output.exists()
    print(json.dumps(dict(passed=True,source_only=True,outputs_written=0,ROM_written=False,
        current_parent_SHA256=E.PIN,in_memory_SHA256=E.digest(image),vectors=receipt,
        source_SHA256=sha256(Path(__file__).read_bytes()).hexdigest()),sort_keys=True),flush=True)


if __name__=='__main__':main()
