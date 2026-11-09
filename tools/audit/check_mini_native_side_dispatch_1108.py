"""Measure a short route to Mini's native side filter on the current MMC5 build."""
import argparse
from collections import defaultdict
import hashlib
from itertools import product
import json
from pathlib import Path
import shutil

from prepare_mini_fireball_art_1108 import assemble, patch
from prepare_mini_mario_native_power_1103_v56 import N, bundle
from prepare_mini_side_alias_1108 import compare_memory
from prepare_selected_native_packet_v1 import R, sha

BASE = R/'build/mini-frame-budget-1108/candidate.nes'
PIN = 'e90d30c1c9636be6eb304a7b3b1506b862f8171dc2773d809482e25b0a5417df'
SOURCE = R/'tools/reference/mini_native_side_dispatch_1108.s'
OFFSET = 16+33*8192+0x1ea2
BEFORE = bytes.fromhex('08488d6a01a9b08d6c01a9bf8d6d01a99c205a0190156828'
                       '8d6a01a9558d6c01a9b78d6d01a902205a016068288d6a01'
                       'a9e28d6c01a9be8d6d01a9a1205a0160')


def bind(raw):
    image=bundle(raw)
    image['segs']['side_fixed'] = dict(start=str(0xe000),ooffs=str(16+127*8192))
    image['syms']['SideFixed'] = dict(val=str(0xe497),seg='side_fixed')
    return image


def check(original, patched):
    seeds=[N.fresh(bind(raw)) for raw in (original,patched)]
    summary=defaultdict(list)
    for owner,engine,probe,x,y,tile,p in product((0,1,4,15,19,41), (4,8), (17,20),
            (1,253), (63,191), (0,0x10,0x54,0xc2,0xc3), (0x20,0x61)):
        pair=[N.fork(m) for m in seeds]
        returns=[]
        for m in pair:
            N.put(m,SelectedCharacter=owner,GameEngineSubroutine=engine,
                  Player_X_Position=x,Player_PageLoc=1,Player_Y_Position=y,Player_Y_HighPos=1)
            N.invoke(m,'BlockBufferColli_Side',y=probe)
            m[m[9]+256*m[10]+m[5]]=tile
            returns.append(N.invoke(m,'SideFixed',a=0x95,x=3,y=probe,p=p))
        assert all(returns[0][k]==returns[1][k] for k in ('A','X','Y','P')), (owner,engine,probe,x,y,tile,p,returns)
        compare_memory(*pair)
        assert pair[0][0x170:0x17b]==pair[1][0x170:0x17b]
        summary[owner].append(returns[0]['CPU']-returns[1]['CPU'])
    return {owner:dict(cases=len(values),minimum=min(values),maximum=max(values)) for owner,values in summary.items()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--emit-rom',action='store_true')
    args=parser.parse_args()
    assert sha(BASE)==PIN
    original=BASE.read_bytes()
    assert original[16:1048592].count(bytes.fromhex('a9a28d6c01a9be8d6d01a9a1'))==1
    assert original[16+33*8192:16+34*8192].count(bytes.fromhex('20a2be'))==0
    assert original[16+33*8192:16+34*8192].count(bytes.fromhex('4ca2be'))==0
    args.output.mkdir(exist_ok=True)
    output=args.output/'dispatch.bin'
    assemble(SOURCE,'MEMORY{M:start=$bea2,size=64,file=%O;}SEGMENTS{SIDE:load=M,type=ro;}',output)
    after=output.read_bytes()
    assert len(BEFORE)==len(after)==64
    raw=bytearray(original)
    patch(raw,OFFSET,BEFORE,after)
    results=check(original,raw)
    assert results[41]['minimum']>150
    result=dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=hashlib.sha256(raw).hexdigest(),
                cases=results,patches=[dict(file_offset=OFFSET,old_hex=BEFORE.hex(),new_hex=after.hex())],
                scope='Source CPU proof at the reached fixed side entry. Tank cookie hit, actual interrupts and native replay remain separate.')
    (args.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    if args.emit_rom:
        rom=args.output/'candidate.nes'
        rom.write_bytes(raw)
        for suffix in ('.dbg','.lbl'):
            shutil.copyfile(BASE.with_suffix(suffix),rom.with_suffix(suffix))
        manifest=json.loads(BASE.with_suffix('.json').read_text())
        manifest.update(parent_SHA256=PIN,candidate_SHA256=sha(rom),side_dispatch_CPU=results)
        (args.output/'candidate.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
