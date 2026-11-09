"""Test the exact Mini collision adder, after the side route retires its old tail."""

import argparse
from collections import defaultdict
from itertools import product
import hashlib
import json
from pathlib import Path
import subprocess

from check_mini_native_side_single_map_1109_v1 import BASE, PIN, N, R, locations, offset, sha
from check_mini_native_collision_routes_async_1109_v1 import apply
from prepare_mini_mario_native_power_1103_v56 import bundle
from prepare_mini_side_alias_1108 import compare_memory


SOURCE=R/'tools/reference/mini_native_collision_adder_1109_v1.s'
SPANS=(('ADDER',0xed41,'8d6a01a9048d6c01a9af8d6d01a9e24c5a01'),
       ('FORMER_SIDE',0xe4a7,'8d6a01a9588d6c014cff90ea'))
MIRRORS=(119,120,125,127)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve()
    raw=BASE.read_bytes()
    assert sha(BASE)==PIN
    side=json.loads((out/'proof.json').read_text())
    prior=apply(raw,side)
    pin=hashlib.sha256(prior).hexdigest()
    assert pin==side['expected_memory_only_SHA256']
    assert not locations(prior,'4ca7e4') and not locations(prior,'20a7e4')
    assert locations(prior,'4c41ed')==[offset(126,0x8f7a)] and not locations(prior,'2041ed')
    obj,cfg=(out/f'adder.{ext}' for ext in ('o','cfg'))
    cfg.write_text('MEMORY {\n'+''.join(
        f'{name}:start=${pc:04x},size={len(before)//2},file="{(out/(name+".bin")).as_posix()}";\n'
        for name,pc,before in SPANS)+'}\nSEGMENTS {\n'+''.join(
        f'{name}:load={name},type=ro;\n' for name,*_ in SPANS)+'}\n')
    cc=R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',out/'unused.bin'],check=True)
    obj.unlink()
    patched=bytearray(prior)
    rows=[]
    for bank in MIRRORS:
        tail=offset(bank,0xed5b)
        assert prior[tail:tail+10]==bytes.fromhex('a9af8d6d01a9e24c5a01')
    for name,pc,old_hex in SPANS:
        new=(out/(name+'.bin')).read_bytes()
        for bank in MIRRORS:
            at=offset(bank,pc)
            assert prior[at:at+len(new)].hex()==old_hex
            patched[at:at+len(new)]=new
            rows.append(dict(bank=bank,pc=pc,file_offset=at,old_hex=old_hex,new_hex=new.hex()))
    seeds=[N.fresh(bundle(image)) for image in (prior,patched)]
    costs=defaultdict(list)
    for owner,engine,status,x,p,bank in product((0,1,4,6,9,11,13,15,19,25,26,28,38,40,41,42),
           (4,8),(0,1),(0,1),(0x20,0x61),MIRRORS):
        pair=[N.fork(m) for m in seeds]
        result=[]
        for m in pair:
            N.put(m,SelectedCharacter=owner,GameEngineSubroutine=engine,PlayerStatus=status,
                  PlayerSize=status,Player_State=x)
            m[0x5117]=bank|128
            result.append(N.invoke(m,'MegaManCollisionAdder',a=0x95,x=x,y=77,p=p))
        assert all(result[0][key]==result[1][key] for key in ('A','X','Y')),(owner,engine,status,x,p,bank,result)
        # B distinguishes status pushed by PHP from a hardware interrupt;
        # there is no corresponding latch in the 6502 status register.
        assert (result[0]['P']^result[1]['P'])&0xef==0,(owner,engine,status,x,p,bank,result)
        compare_memory(*pair)
        costs[owner].append(result[0]['CPU']-result[1]['CPU'])
    assert min(costs[41])>150
    proof=dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=pin,
               expected_memory_only_SHA256=hashlib.sha256(patched).hexdigest(),patches=rows,
               required_predecessor='Side routing proof.json. This reuses its retired E4A7 entry, in all four resident E mirrors.',
               cases={owner:dict(cases=len(values),cycles_saved=[min(values),max(values)]) for owner,values in costs.items()})
    (out/'adder-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k] for k in ('passed','expected_memory_only_SHA256','cases')}))


if __name__=='__main__':
    main()
