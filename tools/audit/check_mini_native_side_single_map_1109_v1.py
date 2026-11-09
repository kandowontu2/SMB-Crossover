"""Qualify the direct mapper path to the unchanged Mini native side leaf."""

import argparse
from collections import defaultdict
from itertools import product
import hashlib
import json
from pathlib import Path
import subprocess

from check_mini_native_side_dispatch_1108 import bind, N, sha
from prepare_mini_side_alias_1108 import compare_memory
from prepare_selected_native_packet_v1 import R


BASE = R/'build/mini-parser-lift-1109/candidate.nes'
PIN = 'a08d839b187fc6866a3fd3658200c2f26b8e3724b3b4de3b5e7d2a65702598d2'
SOURCE = R/'tools/reference/mini_native_side_single_map_1109_v1.s'
SPANS = (
    ('SIDE_FIXED',126,0x90e4,'8d6a01a9a28d6c01a9be8d6d01a9a14c5a01'+'ea'*9+'a9bc8d6d01a9d94c5a01'),
    ('SIDE_VISIBLE_TAIL',126,0x913d,'ea'*7),
    ('SIDE_BANK33',33,0xbea2,'08ad0260c929f021a9b08d6c01a9bf8d6d01a99c205a019020a9558d6c01a9b78d6d0128a9024c5a01'
                            'a99b8d6c01a9ad8d6d0128a9fc4c5a01ad6a01284ce2be0848ad0260c904f00dc90ef009c90bb00568284c8b9568284ca7e4ffffff'),
)


def offset(bank,pc):
    return 16+bank*8192+(pc&8191)


def locations(raw,hexbytes):
    start=16
    hits=[]
    needle=bytes.fromhex(hexbytes)
    while (start:=raw.find(needle,start,16+0x100000))!=-1:
        hits.append(start)
        start+=1
    return hits


def assemble(out,old):
    assert locations(old,'4ca7e4')==[offset(33,0xbefa)] and not locations(old,'20a7e4')
    assert locations(old,'4cff90')==[offset(bank,0xe4af) for bank in (119,120,125,127)]
    assert not locations(old,'20ff90')
    assert locations(old,'a9a28d6c01a9be8d6d01a9a1')==[offset(126,0x90e7)]
    assert old[offset(126,0x912b):offset(126,0x913d)]==bytes.fromhex('8d6a01a9ee8d6c01a9b98d6d01a9ce4c5a01')
    assert old[offset(126,0x9144):offset(126,0x9147)]==bytes.fromhex('4e166b')
    cfg=out/'side.cfg'
    cfg.write_text('MEMORY {\n'+''.join(
        f'{name}:start=${pc:04x},size={len(before)//2},file="{(out/(name+".bin")).as_posix()}";\n'
        for name,_,pc,before in SPANS)+'}\nSEGMENTS {\n'+''.join(
        f'{name}:load={name},type=ro;\n' for name,*_ in SPANS)+'}\n')
    cc=R/'tools/Windows/cc65/bin'
    obj=out/'side.o'
    subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',out/'unused.bin'],check=True)
    obj.unlink()
    patched=bytearray(old)
    patches=[]
    for name,bank,pc,old_hex in SPANS:
        start=offset(bank,pc)
        before=bytes.fromhex(old_hex)
        new=(out/(name+'.bin')).read_bytes()
        assert old[start:start+len(new)]==before,(name,old[start:start+len(new)].hex())
        patched[start:start+len(new)]=new
        patches.append(dict(bank=bank,pc=pc,file_offset=start,old_hex=old_hex,new_hex=new.hex()))
    return bytes(patched),patches


def paired_leaves(old,new,exhaustive=False):
    seeds=[N.fresh(bind(raw)) for raw in (old,new)]
    cases=[(41,engine,probe,x,y,tile,p) for engine,probe,x,y,tile,p in product(
        (4,8),(17,20),(1,253),(23,191),range(256),(0x20,0x61))]
    if not exhaustive:
        cases=[(41,engine,probe,(1,253)[(tile>>1)&1],(23,191)[tile&1],tile,(0x20,0x61)[(tile>>2)&1])
               for engine,probe,tile in product((4,8),(17,20),range(256))]
    cases.extend(product((0,1,4,6,10,11,14,15,19,38,40,42,255),(4,8),
                        (17,20),(1,253),(63,191),(0,0x10,0x54,0xc2,0xc3),(0x20,0x61)))
    result=defaultdict(list)
    for owner,engine,probe,x,y,tile,p in cases:
        pair=[N.fork(seed) for seed in seeds]
        returns=[]
        maps=[]
        for m in pair:
            N.put(m,SelectedCharacter=owner,GameEngineSubroutine=engine,
                  Player_X_Position=x,Player_PageLoc=1,Player_Y_Position=y,Player_Y_HighPos=1)
            N.invoke(m,'BlockBufferColli_Side',y=probe)
            m[m[9]+256*m[10]+m[5]]=tile
            n=len(m.writes)
            returns.append(N.invoke(m,'SideFixed',a=0x95,x=3,y=probe,p=p))
            maps.append(sum(at==0x5115 for at,_ in m.writes[n:]))
        assert all(returns[0][k]==returns[1][k] for k in ('A','X','Y','P')),(owner,engine,probe,x,y,tile,p,returns)
        compare_memory(*pair)
        assert pair[0][0x170:0x17b]==pair[1][0x170:0x17b]
        if owner==41:
            assert maps[0]-maps[1]==2,maps
        result[owner].append(returns[0]['CPU']-returns[1]['CPU'])
    return {k:dict(cases=len(v),cycles_saved=[min(v),max(v)]) for k,v in result.items()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--exhaustive',action='store_true')
    args=parser.parse_args()
    out=args.output.resolve()
    out.mkdir(exist_ok=True)
    old=BASE.read_bytes()
    assert sha(BASE)==PIN
    new,patches=assemble(out,old)
    cases=paired_leaves(old,new,args.exhaustive)
    assert cases[41]['cycles_saved'][0]>45,cases
    proof=dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=PIN,
               expected_memory_only_SHA256=hashlib.sha256(new).hexdigest(),patches=patches,cases=cases,
               funding=['Exact fixed low-bank side prefix and former Tn tail at 90E4..9109',
                        'Exact seven post-JMP padding bytes after GuestPlayerVisible at 913D..9144',
                        'Existing bank33 side dispatch through BF00. All Rogue Dawn pages and E mirrors untouched'],
               scope='Actual fixed side entry and authentic unchanged Mini leaf. Tank cookie hit and live interrupts separate.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k] for k in ('passed','parent_SHA256','expected_memory_only_SHA256','cases')}))


if __name__=='__main__':
    main()
