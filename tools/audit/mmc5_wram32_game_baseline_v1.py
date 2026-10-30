"""Private header-only32KBWRAM game baseline, with exact native Bill parity."""
from pathlib import Path
import hashlib
import json
import os
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import rogue_current_native_v1 as base
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load

P=R/'build/full-roster-menu-v5'
O=R/'build/mmc5-wram32-game-baseline-v1'
REF=R/'build/rogue-current-menu-v6/native/bill-parent-v1'
C=R/'build/character-host-union-v11/native_cold.lua'


def main():
    assert not O.exists()
    original=(P/'candidate.nes').read_bytes()
    assert base.sha(P/'candidate.nes')=='5b09a3ed02aa678fb1d6fca57d905224e95c7b8f0f4e12f13901bf3f41f12d1e'
    assert original[10]==7
    raw=bytearray(original)
    raw[10]=9
    assert [i for i,(a,b)in enumerate(zip(original,raw))if a!=b]==[10]
    O.mkdir(parents=True)
    (O/'candidate.nes').write_bytes(raw)
    for suffix in ['dbg','lbl']:
        (O/('candidate.'+suffix)).write_bytes((P/('candidate.'+suffix)).read_bytes())
    digest=base.sha(O/'candidate.nes')
    out=O/'native'
    out.mkdir()
    b=scoped_load(O/'candidate.nes')
    ret=address(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1
    controller=out/'controller.lua'
    controller.write_text('COLD_ARGS={raw=3,slot=3,variant=0,sha256="'+digest+'",main_return='+str(ret)+'}\n'+
        'dofile([=['+C.as_posix()+']=])\n',newline='\n')
    inputs={str(p):base.sha(p)for p in [Path(__file__).resolve(),P/'candidate.nes',
        P/'candidate.dbg',P/'candidate.lbl',O/'candidate.nes',controller,C,REF/'binding.json']}
    ready=dict(prepared=True,scope='Header-only mapper baseline, not new-character integration or source-built header adoption.',
        ROM_sha256=digest,parent_ROM_sha256=base.sha(P/'candidate.nes'),
        changed_offsets=[10],old_header=list(original[:16]),new_header=list(raw[:16]),
        PRG_CHR_payload_SHA256=hashlib.sha256(raw[16:]).hexdigest(),
        shared_installation=False,bindings=inputs)
    (O/'ready.json').write_text(json.dumps(ready,indent=2)+'\n')
    os.environ['SMB_RUN_OUTPUT']=str(out)
    rc=base.run(controller,O/'candidate.nes',timeout=120,emulator_options=[
        '--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros',
        '--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    for path,h in inputs.items():assert base.sha(path)==h,path
    assert rc==0
    old=json.loads((REF/'result.json').read_text())
    new=json.loads((out/'result.json').read_text())
    assert old.pop('ROM_sha256')==ready['parent_ROM_sha256']
    assert new.pop('ROM_sha256')==digest
    assert old==new,(old,new)
    equal=[]
    for path in REF.iterdir():
        if path.name in ['trace.csv','main-cycles.csv']or path.suffix=='.png':
            assert(out/path.name).read_bytes()==path.read_bytes(),path.name
            inputs[str(path)]=base.sha(path)
            equal.append(path.name)
    for path in out.iterdir():
        if path.is_file():inputs[str(path)]=base.sha(path)
    inputs[str(O/'ready.json')]=base.sha(O/'ready.json')
    proof=dict(passed=True,native=True,ROM_sha256=digest,parent_ROM_sha256=ready['parent_ROM_sha256'],
        exact_same_native_result_except_ROM_hash=True,exact_native_files=sorted(equal),
        baseline=new,shared_installation=False,bindings=inputs,
        limits=['Header-only8KB→32KBgame baseline; no selected-owner loader, RAMcode, new-character or native-hardware qualification.',
                'One300frame Bill scenario fromcoldtitle; no all-roster/fullcampaign/constant60Hz claim.'])
    (O/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,ROM_sha256=digest,exact_files=sorted(equal))))


if __name__=='__main__':main()
