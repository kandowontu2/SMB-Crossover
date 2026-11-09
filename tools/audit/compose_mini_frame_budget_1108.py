"""Compose the independently qualified Mini frame-budget changes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from prepare_mini_fireball_art_1108 import patch
from prepare_mini_side_alias_1108 import BASE, PIN, compare_memory
from prepare_mini_mario_native_power_1103_v56 import N, bundle
from prepare_selected_native_packet_v1 import R, sha
from profile_mini_busy_1108_v1 import fixture

SIDE = R/'build/mini-side-alias-1108/candidate.nes'


def load(path):
    return json.loads(path.read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def compose(base, output, proof, *, parent=PIN):
    assert proof['passed'] and (proof.get('parent_SHA256') or proof['base_SHA256'])==parent
    for path,pin in proof.get('bindings',{}).items():
        assert sha(R/Path(path))==pin,path
    isolated = bytearray(base)
    for row in proof['patches']:
        offset = row.get('file_offset',row.get('offset'))
        before = bytes.fromhex(row.get('old_hex') or row['preimage'])
        after = bytes.fromhex(row.get('new_hex') or row['replacement'])
        patch(isolated,offset,before,after)
        patch(output,offset,before,after)
    assert digest(isolated)==proof['expected_memory_only_SHA256']


def check_full_cpu(base, new, ram_exclusions):
    images=[bundle(raw) for raw in (base,new)]
    rows=[]
    for enemies,terrain,parser in [(0,False,False),(2,True,False),(4,False,True),(5,False,False)]:
        pair=[fixture(b,enemies,terrain,parser) for b in images]
        cycles=[]
        for frame in range(2,26):
            keys=1 | (128 if 6<=frame<20 else 0)
            result=[]
            for m in pair:
                N.put(m,FrameCounter=frame,SavedJoypadBits=keys,SavedJoypad1Bits=keys,
                      VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                result.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
            assert all(result[0][key]==result[1][key] for key in ('A','X','Y','P')),result
            compare_memory(*pair,ram_exclusions=ram_exclusions)
            cycles.append([r['CPU'] for r in result])
        savings=[old-new for old,new in cycles]
        rows.append(dict(enemies=enemies,terrain=terrain,parser=parser,updates=len(cycles),
                         min_saved=min(savings),max_saved=max(savings),average_saved=sum(savings)/len(savings)))
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--lift-irq',type=Path,required=True)
    parser.add_argument('--goomba-irq',type=Path,required=True)
    parser.add_argument('--projectile',type=Path,required=True)
    args=parser.parse_args()
    assert sha(BASE)==PIN
    paths=[R/'build/mini-audio-1108-v1/mixer-irq.json',R/'build/mini-lift-admission-fast-1108/proof.json',
           R/'build/mini-goomba-mini-only-1108-v4/proposal.json']
    proofs=[load(p) for p in paths]
    for irq,proof in zip((args.lift_irq,args.goomba_irq),proofs[1:],strict=True):
        receipt=load(irq)
        assert receipt['passed'] and proof['expected_memory_only_SHA256'] in irq.read_text(),irq
    side=load(SIDE.with_suffix('.json'))
    assert side['passed'] and side['parent_SHA256']==PIN and side['candidate_SHA256']==sha(SIDE)
    base=BASE.read_bytes()
    raw=bytearray(SIDE.read_bytes())
    for proof in proofs:
        compose(base,raw,proof)
    assert raw[1048592:]==base[1048592:], 'All CHR, donor art and Mini kernel carriers stay exact'
    projectile=load(args.projectile)
    compose(base,raw,projectile)
    data=load(BASE.with_suffix('.json'))
    for frame in data['frames'].values():
        start=1048592+967*1024+frame['CHR_offset']
        assert raw[start:start+32].hex()==frame['bytes']
    rows=check_full_cpu(base,raw,{int(bank):ranges for bank,ranges in projectile['ram_exclusions'].items()})
    assert all(row['average_saved']>0 for row in rows)
    args.output.mkdir()
    rom=args.output/'candidate.nes'
    rom.write_bytes(raw)
    for ext in ('.lbl','.dbg'):
        shutil.copyfile(BASE.with_suffix(ext),rom.with_suffix(ext))
    data.update(parent_SHA256=PIN,candidate_SHA256=sha(rom),whole_GameCore=rows,
                native_draw_address=projectile['native_draw_address'],native_draw_bytes=projectile['native_draw_bytes'],
                performance_proofs={str(p):sha(p) for p in [SIDE.with_suffix('.json'),*paths,args.lift_irq,args.goomba_irq,args.projectile]},
                scope='Exact Mini lift/art release with background, Goomba draw, lift admission, projectile draw and audio speedups. Native replay remains separate.')
    (args.output/'candidate.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(candidate_SHA256=sha(rom),whole_GameCore=rows)))


if __name__=='__main__':
    main()
